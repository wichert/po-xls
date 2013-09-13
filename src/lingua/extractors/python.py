import tokenize
from babel.util import parse_encoding


def safe_eval(s, encoding='ascii'):
    if encoding != 'ascii':
        s = s.decode(encoding)
    return eval(s, {'__builtins__': {}}, {})


class PythonExtractor(object):
    def __call__(self, fileobj, keywords, comment_tags, options):
        if not isinstance(keywords, dict):
            keywords = dict.fromkeys(keywords)
            if 'ngettext' in keywords:
                keywords['ngettext'] = (1, 2)
                keywords['pluralize'] = (1, 2)
        self.state = self.stateWaiting
        self.msg = None
        self.keywords = keywords
        self.messages = []
        self.encoding = parse_encoding(fileobj) or "ascii"
        tokens = tokenize.generate_tokens(fileobj.readline)
        for (ttype, tstring, stup, etup, line) in tokens:
            self.state(ttype, tstring, stup[0])
        return self.messages

    def stateWaiting(self, ttype, tstring, lineno):
        if ttype == tokenize.NAME:
            if tstring in self.keywords:
                self.state = self.stateKeywordSeen
                self.msg = dict(lineno=lineno)
                if self.keywords[tstring] is None:
                    self.msg['type'] = 'singular'
                else:
                    self.msg['type'] = 'plural'
    
    def stateKeywordSeen(self, ttype, tstring, lineno):
        # We have seen _, now check if this is a _( .. ) call
        if ttype == tokenize.OP and tstring == '(':
            self.state = self.stateWaitForLabel
        else:
            self.state = self.stateWaiting

    def stateWaitForLabel(self, ttype, tstring, lineno):
        # We saw _(, wait for the message label
        if ttype == tokenize.STRING:
            self.msg.setdefault('label', []).append(
                    safe_eval(tstring, self.encoding))
        elif ttype == tokenize.OP and tstring == ',':
            self.state = self.stateWaitForDefault
        elif ttype == tokenize.OP and tstring == ')':
            self.addMessage(self.msg)
            self.state = self.stateWaiting
        elif ttype == tokenize.NAME:
            self._parameter = tstring
            self.state = self.stateInFactoryParameter
        elif ttype == tokenize.NL:
            pass
        else:
            # Effectively a syntax error, but ignore and reset state
            self.msg = None
            self.state = self.stateWaiting

    def stateWaitForDefault(self, ttype, tstring, lineno):
        # We saw _('label', now wait for a default translation
        if ttype == tokenize.STRING:
            self.msg.setdefault('default', []).append(
                    safe_eval(tstring, self.encoding))
        elif ttype == tokenize.NAME:
            self._parameter = tstring
            self.state = self.stateInFactoryParameter
        elif ttype == tokenize.OP and tstring == ',':
            self.state = self.stateInFactoryWaitForParameter
        elif ttype == tokenize.OP and tstring == ')':
            self.addMessage(self.msg)
            self.state = self.stateWaiting
        # We ignore anything else (ie whitespace, comments, syntax errors,
        # etc.)

    def stateInFactoryWaitForParameter(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == ')':
            self.addMessage(self.msg)
            self.msg = None
            self.state = self.stateWaiting
        elif ttype == tokenize.NAME:
            self._parameter = tstring
            self.state = self.stateInFactoryParameter

    def stateInFactoryParameter(self, ttype, tstring, lineno):
        if ttype == tokenize.STRING:
            self.msg.setdefault(self._parameter, []).append(
                    safe_eval(tstring, self.encoding))
        elif ttype == tokenize.OP and tstring == ',':
            self.state = self.stateInFactoryWaitForParameter
        elif ttype == tokenize.OP and tstring == ')':
            self.addMessage(self.msg)
            self.state = self.stateWaiting

    def addMessage(self, msg):
        if not msg.get('label'):
            return
        default = msg.get('default', None)
        if default:
            comments = [u'Default: %s' % u''.join(default)]
        else:
            comments = []
        label = msg['label']
        if (msg['type'] == 'singular'):
            label = u''.join(msg['label'])
            positions = '_'
        else:
            label += default
            positions = 'ngettext'
        self.messages.append(
                (msg['lineno'], positions, label, comments))


extract_python = PythonExtractor()
