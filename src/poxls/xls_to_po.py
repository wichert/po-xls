import argparse
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
import os
import shutil
import sys
import time
import polib
import xlrd


def replace_catalog(filename, catalog):
    tmpfile = filename + '~'
    catalog.save(tmpfile)
    if sys.platform in ['win32', 'cygwin']:
        # Windows does not support atomic renames.
        shutil.move(tmpfile, filename)
    else:
        os.rename(tmpfile, filename)


def po_timestamp(filename):
    local = time.localtime(os.stat(filename).st_mtime)
    offset = -(time.altzone if local.tm_isdst else time.timezone)
    return '%s%s%s' % (
        time.strftime('%Y-%m-%d %H:%M', local),
        '-' if offset < 0 else '+',
        time.strftime('%H%M', time.gmtime(abs(offset))))


def main():
    parser = argparse.ArgumentParser(
            description='Convert a XLS(X) file to a .PO file')

    parser.add_argument('locale', metavar='<locale>',
            help='Locale to process')
    parser.add_argument('input_file', metavar='<xls file>',
            help='Input XLS file')
    parser.add_argument('output_file', metavar='<po file>',
            help='PO file to update')
    options = parser.parse_args()

    book = xlrd.open_workbook(filename=options.input_file, logfile=sys.stderr)
    catalog = polib.POFile()
    catalog.header = u'This file was generated from %s' % options.input_file
    catalog.metata_is_fuzzy = True
    catalog.metadata = OrderedDict()
    catalog.metadata['PO-Revision-Date'] = po_timestamp(options.input_file)
    catalog.metadata['Content-Type'] = 'text/plain; charset=UTF-8'
    catalog.metadata['Content-Transfer-Encoding'] = '8bit'
    catalog.metadata['Generated-By'] = 'xls-to-po 1.0'

    for sheet in book.sheets():
        headers = [c.value for c in sheet.row(0)]
        headers = dict((b, a) for (a, b) in enumerate(headers))
        msgctxt_column = headers.get('Message context')
        msgid_column = headers.get('Message id')
        tcomment_column = headers.get('Translator comment')
        msgstr_column = headers.get(options.locale)
        if not msgid_column:
            continue
        if not msgstr_column:
            continue

        for row in range(1, sheet.nrows):
            row = [c.value for c in sheet.row(row)]
            try:
                entry = polib.POEntry(
                        msgctxt=row[msgctxt_column] if msgctxt_column else None,
                        msgid=row[msgid_column],
                        msgstr=row[msgstr_column])
                if tcomment_column:
                    entry.tcomment = row[tcomment_column]
                catalog.append(entry)
            except IndexError:
                print >> sys.stderr, 'Row %s is too short' % row

    replace_catalog(options.output_file, catalog)
