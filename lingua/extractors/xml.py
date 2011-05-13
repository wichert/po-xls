from __future__ import absolute_import
import collections
import re
from xml.parsers import expat

class TranslateContext(object):
    WHITESPACE = re.compile(u"\s{2,}")

    def __init__(self, msgid, lineno):
        self.msgid = msgid
        self.text = []
        self.lineno = lineno

    def addText(self, text):
        self.text.append(text)


    def addNode(self, name, attributes):
        name = attributes.get("http://xml.zope.org/namespaces/i18n name")
        if name:
            self.text.append(u"${%s}" % name)
        else:
            self.text.append(u"<dynamic element>")


    def message(self):
        text = u"".join(self.text)
        text = self.WHITESPACE.sub(u" ", text)
        if self.msgid:
            return (self.lineno, None, self.msgid, [u"Default: %s" % text])
        else:
            return (self.lineno, None, text, [])


class XmlExtractor(object):
    ENTITY = re.compile(r"&([A-Za-z]+|#[0-9]+);")

    def __call__(self, fileobj, keywords, comment_tags, options):
        self.keywords = keywords
        self.comment_tags = comment_tags
        self.options = options
        self.messages = []
        self.parser = expat.ParserCreate(namespace_separator=' ')
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

        try:
            self.parser.ParseFile(fileobj)
        except expat.ExpatError:
            pass
        return self.messages


    def addMessage(self, message, comments=[]):
        self.messages.append((self.parser.CurrentLineNumber, None, message, comments))


    def StartElementHandler(self, name, attributes):
        new_domain = attributes.get("http://xml.zope.org/namespaces/i18n domain")
        if new_domain:
            self.domainstack.append(new_domain)
        elif self.domainstack:
            self.domainstack.append(self.domainstack[-1])

        if self.translatestack[-1]:
            self.translatestack[-1].addNode(name, attributes)

        i18n_translate = attributes.get("http://xml.zope.org/namespaces/i18n translate")
        if i18n_translate is not None:
            self.translatestack.append(TranslateContext(i18n_translate, self.parser.CurrentLineNumber))
        else:
            self.translatestack.append(None)

        if not self.domainstack:
            return

        i18n_attributes = attributes.get("http://xml.zope.org/namespaces/i18n attributes")
        if i18n_attributes:
            parts = [p.strip() for p in i18n_attributes.split(";")]
            for msgid in parts:
                if " " not in msgid:
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
                    self.addMessage(msgid, [u"Default: %s" % attributes[attr]])


    def DefaultHandler(self, data):
        if data.startswith(u"&") and self.translatestack[-1]:
            self.translatestack[-1].addText(data)


    def CharacterDataHandler(self, data):
        if not self.translatestack[-1]:
            return

        data_length = len(data)
        context = self.parser.GetInputContext()

        while data:
            m = self.ENTITY.search(context)
            if m is None or m.start()>=data_length:
                self.translatestack[-1].addText(data)
                break

            n = self.ENTITY.match(data)
            if n is not None:
                length = n.end()
            else:
                length = 1

            self.translatestack[-1].addText(context[0: m.end()])
            data = data[m.start()+length:]



    def EndElementHandler(self, name):
        if self.domainstack:
            self.domainstack.pop()

        translate = self.translatestack.pop()
        if translate:
            self.messages.append(translate.message())


def extract_xml(fileobj, keywords, comment_tags, options):
    extractor = XmlExtractor()
    return extractor(fileobj, keywords, comment_tags, options)


