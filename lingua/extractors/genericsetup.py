from __future__ import absolute_import
import collections
from xml.etree import ElementTree as etree
from xml.parsers.expat import ExpatError

def extract_genericsetup(fileobj, keywords, comment_tags, options):
    try:
        doc = etree.parse(fileobj)
    except ExpatError:
        return []

    return []

