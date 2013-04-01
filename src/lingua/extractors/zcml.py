from __future__ import absolute_import
import collections
import sys
from xml.parsers import expat


class ZcmlExtractor(object):
    ATTRIBUTES = set(['title', 'description'])

    def __call__(self, fileobj, keywords, comment_tags, options):
        self.keywords = keywords
        self.comment_tags = comment_tags
        self.options = options
        self.messages = []
        self.parser = expat.ParserCreate()
        self.parser.StartElementHandler = self.StartElementHandler
        self.parser.EndElementHandler = self.EndElementHandler
        self.domainstack = collections.deque()
        try:
            self.parser.ParseFile(fileobj)
        except expat.ExpatError as e:
            if getattr(fileobj, 'name', None):
                print >> sys.stderr, \
                        ('Aborting due to parse error in %s: %s' %
                                (fileobj.name, e.message))
            else:
                print >> sys.stderr, \
                        ('Aborting due to parse error: %s' % e.message)
            sys.exit(1)
        return self.messages

    def addMessage(self, message, comments=[]):
        self.messages.append(
                (self.parser.CurrentLineNumber, None, message, comments))

    def StartElementHandler(self, name, attributes):
        if 'i18n_domain' in attributes:
            self.domainstack.append(attributes["i18n_domain"])
        elif self.domainstack:
            self.domainstack.append(self.domainstack[-1])

        if not self.domainstack:
            return

        for (key, value) in attributes.items():
            if key in self.ATTRIBUTES:
                self.addMessage(value)

    def EndElementHandler(self, name):
        if self.domainstack:
            self.domainstack.pop()


def extract_zcml(fileobj, keywords, comment_tags, options):
    extractor = ZcmlExtractor()
    return extractor(fileobj, keywords, comment_tags, options)
