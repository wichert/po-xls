import unittest


class ExtractTests(unittest.TestCase):
    def extract(self, snippet):
        from lingua.extractors.zcml import extract_zcml
        from StringIO import StringIO
        snippet = StringIO(snippet)
        return list(extract_zcml(snippet, None, None, None))

    def testInvalidXML(self):
        self.assertEqual(self.extract(""), [])

    def testEmptyXml(self):
        self.assertEqual(self.extract("<configure/>"), [])

    def testi18nWithoutDomain(self):
        snippet = """\
                <configure>
                  <dummy title="test title"/>
                </configure>
                """
        self.assertEqual(self.extract(snippet), [])

    def testi18nWithDomain(self):
        snippet = """\
                <configure i18n_domain="lingua">
                  <dummy title="test title"/>
                </configure>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, "test title", [])])

    def testMultipleMessages(self):
        snippet = """\
                <configure i18n_domain="lingua">
                  <dummy title="test title 1"/>
                  <dummy title="test title 2"/>
                </configure>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, "test title 1", []),
                 (3, None, "test title 2", [])])

    def testDomainNesting(self):
        snippet = """\
                <configure>
                  <configure i18n_domain="lingua">
                      <dummy title="test title 1"/>
                  </configure>
                  <dummy title="test title 2"/>
                </configure>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "test title 1", [])])
