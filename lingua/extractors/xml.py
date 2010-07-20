import collections
import re
from chameleon.zpt.language import Parser

def extract_xml(fileobj, keywords, comment_tags, options):
    parser = Parser()
    doc = parser.parse(fileobj.read())
    root = doc.getroot()

    todo = collections.deque([(root, None)])
    while todo:
        (node, domain) = todo.pop()
        domain = getattr(node, "i18n_domain", domain) or domain

        attrs = getattr(node, "i18n_attributes", None)
        if attrs:
            for (attr, label) in attrs:
                value = node.attrib.get(attr, None)
                if not value:
                    continue

                if label:
                    yield (node.position[0], None, label,  [u"Default: %s" % value])
                else:
                    yield (node.position[0], None, value, [])

        label = getattr(node, "i18n_translate", None)
        if label is not None:
            msg = []
            if node.text:
                msg.append(node.text.lstrip())
            for child in node.getchildren():
                name = getattr(child, "i18n_name")
                if name:
                    msg.append(u"${%s}" % name)
                if child.tail:
                    msg.append(child.tail)
            msg = u"".join(msg)
            msg = re.sub(u"\s{2,}", u" ", msg)
            if label:
                yield (node.position[0], None, label, [u"Default: %s" % msg])
            else:
                yield (node.position[0], None, msg, [])

        for child in node.getchildren():
            todo.append((child, domain))


