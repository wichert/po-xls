try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
import os
import shutil
import sys
import time
import click
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


@click.command(help=u'Convert a XLS(X) file to a .PO file')
@click.argument('locale', required=True)
@click.argument('input_file',
        type=click.Path(exists=True, readable=True),
        required=True)
@click.argument('output_file', required=True)
def main(locale, input_file, output_file):
    book = xlrd.open_workbook(filename=input_file, logfile=sys.stderr)
    catalog = polib.POFile()
    catalog.header = u'This file was generated from %s' % input_file
    catalog.metata_is_fuzzy = True
    catalog.metadata = OrderedDict()
    catalog.metadata['PO-Revision-Date'] = po_timestamp(input_file)
    catalog.metadata['Content-Type'] = 'text/plain; charset=UTF-8'
    catalog.metadata['Content-Transfer-Encoding'] = '8bit'
    catalog.metadata['Generated-By'] = 'xls-to-po 1.0'

    for sheet in book.sheets():
        headers = [c.value for c in sheet.row(0)]
        headers = dict((b, a) for (a, b) in enumerate(headers))
        msgctxt_column = headers.get('Message context')
        msgid_column = headers.get('Message id')
        tcomment_column = headers.get('Translator comment')
        msgstr_column = headers.get(locale)
        if not msgid_column:
            click.echo(u'Could not find a "Message context" column in sheet %s' %
                    sheet.name, err=True)
            continue
        if not msgstr_column:
            click.echo(u'Could not find a "%s" column in sheet %s' %
                    (locale, sheet.name), err=True)
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
                click.echo('Row %s is too short' % row, err=True)

    if not catalog:
        click.echo('No messages found, aborting', err=True)
        sys.exit(1)

    replace_catalog(output_file, catalog)


if __name__ == '__main__':
    main()
