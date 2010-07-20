import unittest


class ExtractTests(unittest.TestCase):
    def extract(self, snippet):
        from lingua.extractors.xml import extract_xml
        from StringIO import StringIO
        snippet=StringIO(snippet)
        return list(extract_xml(snippet, None, None, None))

    def testInvalidXML(self):
        self.assertEqual(self.extract(""), [])

    def testEmptyXml(self):
        self.assertEqual(self.extract("<html/>"), [])

    def test_attributes_plain(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:attributes="title" title="test title"/>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, "test title", [])])

    def test_attributes_explicitMessageId(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:attributes="msg_title title" title="test title"/>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, "msg_title", ["Default: test title"])])

    def test_attributes_NoDomain(self):
        snippet="""\
                <html>
                  <dummy i18n:attributes="title" title="test title"/>
                </html>
                """
        self.assertEqual(self.extract(snippet), [])

    def test_attributes_multipleAttributes(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:attributes="title ; alt" title="test title" alt="test alt"/>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, "test title", []),
                 (2, None, "test alt", [])])

    def test_attributes_multipleAttributesWithExplicitMessageId(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:attributes="msg_title title; msg_alt alt" title="test title" alt="test alt"/>
                </html>
                """
        self.assertEqual(sorted(self.extract(snippet)),
                [(2, None, "msg_alt", ["Default: test alt"]),
                 (2, None, "msg_title", ["Default: test title"])])


    def test_translate_minimal(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="">Dummy text</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, u"Dummy text", [])])

    def test_translate_explicitMessageId(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy text</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, "msgid_dummy", [u"Default: Dummy text"])])

    def test_translate_subelement(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy <strong>text</strong> demo</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, "msgid_dummy", [u"Default: Dummy <dynamic element> demo"])])

    def test_translate_namedSubelement(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy <strong i18n:name="text">text</strong> demo</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, "msgid_dummy", [u"Default: Dummy ${text} demo"])])

    def test_translate_translatedSubElement(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy <strong i18n:name="text" i18n:translate="msgid_text">text</strong> demo</dummy>
                </html>
                """
        self.assertEqual(sorted(self.extract(snippet)),
                [(2, None, "msgid_dummy", [u"Default: Dummy ${text} demo"]),
                 (2, None, "msgid_text", [u"Default: text"])])

    def test_translate_stripExtraWhitespace(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="">Dummy


                  text</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, u"Dummy text", [])])

