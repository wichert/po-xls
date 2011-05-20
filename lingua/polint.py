import argparse
import collections
import textwrap
import polib


def verify_po(path, show_path):
    leader = '[%s] ' % path if show_path else ''
    try:
        catalog = polib.pofile(path)
    except UnicodeDecodeError:
        print 'Character encoding problems occured while parsing %s' % path
        print 'Perhaps this is not a PO file?'
        return
    msgids = collections.defaultdict(int)
    reverse_map = collections.defaultdict(list)

    for entry in catalog:
        key = (entry.msgctxt, entry.msgid)
        msgids[key] += 1
        if entry.msgstr:
            reverse_map[entry.msgstr].append(key)

    for (key, count) in msgids.items():
        if count == 1:
            continue
        print '%sMessage repeated %d times:' % (leader, count)
        (context, msgid) = key
        if context:
            msgid = u'[%s] %s' % (context, msgid)
        print textwrap.fill(msgid, initial_indent=u' ' * 5,
                subsequent_indent=u' ' * 8).encode('utf-8')
        print

    for (msgstr, keys) in reverse_map.items():
        if len(keys) == 1:
            continue

        print '%sTranslation:' % leader
        print textwrap.fill(msgstr, initial_indent=u' ' * 8,
                subsequent_indent=u' ' * 8).encode('utf-8')
        print "Used for %d canonical texts:" % len(keys)
        for (idx, info) in enumerate(keys):
            (context, msgid) = info
            if context:
                msgid = u'[%s] %s' % (context, msgid)
            print textwrap.fill(msgid, initial_indent='%-8d' % (idx + 1),
                    subsequent_indent=8 * ' ').encode('utf-8')
        print


def main():
    parser = argparse.ArgumentParser(
            description="Perform sanity checks on PO files")
    parser.add_argument('input', metavar='PO-file', nargs='+',
            help='PO file to check')
    options = parser.parse_args()

    show_path = len(options.input) > 1
    for path in options.input:
        verify_po(path, show_path)
