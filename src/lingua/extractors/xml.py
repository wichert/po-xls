from __future__ import absolute_import
import collections
import re
from StringIO import StringIO
from xml.parsers import expat

from lingua.extractors.python import PythonExtractor


class TranslateContext(object):
    WHITESPACE = re.compile(u"\s{2,}")
    EXPRESSION = re.compile(u"\s*\${[^}]*}\s*")

    def __init__(self, msgid, lineno, i18n_prefix):
        self.msgid = msgid
        self.text = []
        self.lineno = lineno
        self.i18n_prefix = i18n_prefix

    def addText(self, text):
        self.text.append(text)

    def addNode(self, name, attributes):
        name = attributes.get('%s:name' % self.i18n_prefix)
        if name:
            self.text.append(u'${%s}' % name)
        else:
            self.text.append(u'<dynamic element>')

    def ignore(self):
        text = u''.join(self.text).strip()
        text = self.WHITESPACE.sub(u' ', text)
        text = self.EXPRESSION.sub(u'', text)
        return not text

    def message(self):
        text = u''.join(self.text).strip()
        text = self.WHITESPACE.sub(u' ', text)
        if self.msgid:
            return (self.lineno, None, self.msgid, [u'Default: %s' % text])
        else:
            return (self.lineno, None, text, [])


class XmlExtractor(object):
    ENTITY = re.compile(r"&([A-Za-z]+|#[0-9]+);")
    UNDERSCORE_CALL = re.compile("_\(")

    def __call__(self, fileobj, keywords, comment_tags, options):
        self.keywords = keywords
        self.comment_tags = comment_tags
        self.options = options
        self.messages = []
        self.parser = expat.ParserCreate()
        self.parser.returns_unicode = True
        self.parser.UseForeignDTD()
        self.parser.SetParamEntityParsing(
            expat.XML_PARAM_ENTITY_PARSING_ALWAYS)
        self.parser.StartElementHandler = self.StartElementHandler
        self.parser.CharacterDataHandler = self.CharacterDataHandler
        self.parser.EndElementHandler = self.EndElementHandler
        self.parser.DefaultHandler = self.DefaultHandler
        self.domainstack = collections.deque()
        self.translatestack = collections.deque([None])
        self.prefix_stack = collections.deque(['i18n'])

        try:
            self.parser.ParseFile(fileobj)
        except expat.ExpatError:
            pass
        return self.messages

    def addMessage(self, message, comments=[]):
        self.messages.append(
                (self.parser.CurrentLineNumber, None, message, comments))

    def addUndercoreCalls(self, message):
        msg = message
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        py_extractor = PythonExtractor()
        py_messages = py_extractor(StringIO(msg), ['_'], None, None)
        for (line, _, py_message, comments) in py_messages:
            self.addMessage(py_message, comments)

    def StartElementHandler(self, name, attributes):
        i18n_prefix = self.prefix_stack[-1]
        for (attr, value) in attributes.items():
            if value == 'http://xml.zope.org/namespaces/i18n' and \
                    attr.startswith('xmlns:'):
                i18n_prefix = attr[6:]
        self.prefix_stack.append(i18n_prefix)

        new_domain = attributes.get('%s:domain' % i18n_prefix)
        if i18n_prefix and new_domain:
            self.domainstack.append(new_domain)
        elif self.domainstack:
            self.domainstack.append(self.domainstack[-1])

        if self.translatestack[-1]:
            self.translatestack[-1].addNode(name, attributes)

        i18n_translate = attributes.get('%s:translate' % i18n_prefix)
        if i18n_prefix and i18n_translate is not None:
            self.translatestack.append(TranslateContext(
                i18n_translate, self.parser.CurrentLineNumber, i18n_prefix))
        else:
            self.translatestack.append(None)

        if not self.domainstack:
            return

        i18n_attributes = attributes.get('%s:attributes' % i18n_prefix)
        if i18n_prefix and i18n_attributes:
            parts = [p.strip() for p in i18n_attributes.split(';')]
            for msgid in parts:
                if ' ' not in msgid:
                    if msgid not in attributes:
                        continue
                    self.addMessage(attributes[msgid])
                else:
                    try:
                        (msgid, attr) = msgid.split()
                    except ValueError:
                        continue
                    if attr not in attributes:
                        continue
                    self.addMessage(msgid, [u'Default: %s' % attributes[attr]])

        for (attr, value) in attributes.items():
            if self.UNDERSCORE_CALL.search(value):
                self.addUndercoreCalls(value)

    def DefaultHandler(self, data):
        if data.startswith(u'&') and self.translatestack[-1]:
            self.translatestack[-1].addText(data)

    def CharacterDataHandler(self, data):
        if TranslateContext.EXPRESSION.search(data) and \
                self.UNDERSCORE_CALL.search(data):
            self.addUndercoreCalls(data)
        if not self.translatestack[-1]:
            return

        data_length = len(data)
        context = self.parser.GetInputContext()

        while data:
            m = self.ENTITY.search(context)
            if m is None or m.start() >= data_length:
                self.translatestack[-1].addText(data)
                break

            n = self.ENTITY.match(data)
            if n is not None:
                length = n.end()
            else:
                length = 1

            self.translatestack[-1].addText(context[0: m.end()])
            data = data[m.start() + length:]

    def EndElementHandler(self, name):
        if self.prefix_stack:
            self.prefix_stack.pop()
        if self.domainstack:
            self.domainstack.pop()
        translate = self.translatestack.pop()
        if translate and not translate.ignore():
            self.messages.append(translate.message())


def extract_xml(fileobj, keywords, comment_tags, options):
    extractor = XmlExtractor()
    return extractor(fileobj, keywords, comment_tags, options)
