# coding=utf-8

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
                  <dummy i18n:attributes="title" title="tést title"/>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, u"tést title", [])])

    def test_attributes_explicitMessageId(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:attributes="msg_title title" title="test tïtle"/>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, u"msg_title", [u"Default: test tïtle"])])

    def test_attributes_NoDomain(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n">
                  <dummy i18n:attributes="title" title="test title"/>
                </html>
                """
        self.assertEqual(self.extract(snippet), [])

    def test_attributes_multipleAttributes(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:attributes="title ; alt" title="tést title" alt="test ålt"/>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, u"tést title", []),
                 (2, None, u"test ålt", [])])

    def test_attributes_multipleAttributesWithExplicitMessageId(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:attributes="msg_title title; msg_alt alt" title="test titlé" alt="test ålt"/>
                </html>
                """
        self.assertEqual(sorted(self.extract(snippet)),
                [(2, None, "msg_alt", [u"Default: test ålt"]),
                 (2, None, "msg_title", [u"Default: test titlé"])])


    def test_translate_minimal(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="">Dummy téxt</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, u"Dummy téxt", [])])

    def test_translate_explicitMessageId(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy téxt</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, u"msgid_dummy", [u"Default: Dummy téxt"])])

    def test_translate_subelement(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy <strong>text</strong> demø</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, "msgid_dummy", [u"Default: Dummy <dynamic element> demø"])])

    def test_translate_namedSubelement(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy <strong i18n:name="text">téxt</strong> demø</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, u"msgid_dummy", [u"Default: Dummy ${text} demø"])])

    def test_translate_translatedSubElement(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy <strong i18n:name="text" i18n:translate="msgid_text">téxt</strong> demø</dummy>
                </html>
                """
        self.assertEqual(sorted(self.extract(snippet)),
                [(2, None, u"msgid_dummy", [u"Default: Dummy ${text} demø"]),
                 (2, None, u"msgid_text", [u"Default: téxt"])])

    def test_translate_stripExtraWhitespace(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <dummy i18n:translate="">Dummy


                  text</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, u"Dummy text", [])])

    def test_translate_HtmlEntity(self):
        snippet="""\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="lingua">
                  <button i18n:translate="">lock &amp; load&nbsp;</button>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(2, None, u"lock &amp; load&nbsp;", [])])

