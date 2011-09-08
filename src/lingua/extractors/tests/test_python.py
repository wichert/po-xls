# coding=utf-8

import unittest


class ExtractTests(unittest.TestCase):
    def extract(self, snippet):
        from lingua.extractors.python import extract_python
        from StringIO import StringIO
        snippet = StringIO(snippet)
        return list(extract_python(snippet, ['_'], None, None))

    def test_multiline_string(self):
        self.assertEqual(
                self.extract("_('one two '\n'three')"),
                [(1, None, u'one two three', [])])
