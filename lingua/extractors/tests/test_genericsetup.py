import unittest
from StringIO import StringIO


class ExtractTests(unittest.TestCase):
    def extract(self, snippet):
        from lingua.extractors.genericsetup import extract_genericsetup
        snippet=StringIO(snippet)
        return list(extract_genericsetup(snippet, None, None, None))

    def testInvalidXML(self):
        self.assertEqual(self.extract(""), [])

    def testEmptyXml(self):
        self.assertEqual(self.extract("<root/>"), [])

    def testi18nWithoutDomain(self):
        snippet="""\
                <configure>
                  <directive title="">
                </configure>
              """
        self.assertEqual(self.extract("<root/>"), [])

