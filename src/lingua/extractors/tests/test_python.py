# coding=utf-8

import unittest


class ExtractTests(unittest.TestCase):
    def extract(self, snippet):
        from lingua.extractors.python import extract_python
        from StringIO import StringIO
        snippet = StringIO(snippet)
        return list(extract_python(snippet, {'_':None, 'pluralize':(1,2)}, None, None))

    def test_syntax_error(self):
        self.assertEqual(
                self.extract("def class xya _('foo')"),
                [(1, '_', u'foo', [])])

    def test_multiline_string(self):
        self.assertEqual(
                self.extract("_('one two '\n'three')"),
                [(1, '_', u'one two three', [])])
    
    def test_gettext_plural(self):
        self.assertEqual(
                self.extract("pluralize('cow_number', 'There are ${n} cows', 9, domain='foo', mapping={'n':'9'})"),
                [(1, 'ngettext', ['cow_number', 'There are ${n} cows'], [u'Default: There are ${n} cows'])])
