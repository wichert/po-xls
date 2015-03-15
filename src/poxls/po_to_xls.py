import os
import click
import polib
import xlrd
import xlwt
from . import ColumnHeaders


def to_base26(value):
    """Convert a column number to the base-26 notation used by spreadsheets.
    """
    if not value:
        return 'A'
    output = []
    while value:
        digit = value % 26
        if output:
            digit -= 1
        output.append(chr(ord('A') + digit))
        value /= 26
    return ''.join(reversed(output))


def cell_id(row, column):
    """Return the cell coordinate in spread-sheet notation.

    This convers a row and column number into a standard cell coordinate
    such as F6.
    """

    return '%s%d' % (to_base26(column), row + 1)


def cell_string(sheet, row, col):
    """Get the text contents of a spreadsheet cell.
    """
    cell = sheet.cell(row, col)
    if cell.ctype != xlrd.XL_CELL_TEXT:
        return None
    return cell.value.strip()


def find_msg(sheet, row, catalog):
    msgctxt = cell_string(sheet, row, 0)
    msgid = cell_string(sheet, row, 1)
    if not msgid:
        click.echo('Missing message id in cell %s:%s' %
                (sheet.name, cell_id(row, 1)), err=True)
        return None

    msg = catalog.find(msgid, msgctxt or False)
    if msg is None:
        click.echo('Can not find translation for cell %s:%s in PO file.' %
                (sheet.name, cell_id(row, 0)), err=True)
        return None

    return msg


class CatalogFile(click.Path):
    def __init__(self):
        super(CatalogFile, self).__init__(exists=True, dir_okay=False,
                readable=True)

    def convert(self, value, param, ctx):
        if not os.path.exists(value) and ':' in value:
            # The user passed a <locale>:<path> value
            (locale, path) = value.split(':', 1)
            path = os.path.expanduser(path)
            real_path = super(CatalogFile, self).convert(path, param, ctx)
            return (locale, polib.pofile(real_path))
        else:
            real_path = super(CatalogFile, self).convert(value, param, ctx)
            catalog = polib.pofile(real_path)
            locale = catalog.metadata.get('Language')
            if not locale:
                locale = os.path.splitext(os.path.basename(real_path))[0]
            return (locale, catalog)


@click.command()
@click.option('-c', '--comments', multiple=True,
        type=click.Choice(['translator', 'extracted', 'reference', 'all']),
        help='Comments to include in the spreadsheet')
@click.option('-o', '--output', type=click.File('wb'), default='messages.xlsx',
        help='Output file', show_default=True)
@click.argument('catalogs', metavar='CATALOG', nargs=-1, required=True, type=CatalogFile())
def main(comments, output, catalogs):
    """
    Convert .PO files to an XLSX file.

    po-to-xls tries to guess the locale for PO files by looking at the
    "Language" key in the PO metadata, falling back to the filename. You
    can also specify the locale manually by adding prefixing the filename
    with "<locale>:". For example: "nl:locales/nl/mydomain.po".
    """
    has_msgctxt = False
    for (locale, catalog) in catalogs:
        has_msgctxt = has_msgctxt or any(m.msgctxt for m in catalog)

    messages = []
    seen = set()
    for (_, catalog) in catalogs:
        for msg in catalog:
            if not msg.msgid or msg.obsolete:
                continue
            if msg.msgid not in seen:
                messages.append((msg.msgid, msg.msgctxt, msg))
                seen.add(msg.msgid)

    book = xlwt.Workbook(encoding='utf-8')
    italic_style = xlwt.XFStyle()
    italic_style.num_format_str = 'Italic'
    italic_style.font.italic = True
    italic_style.font.bold = True
    sheet = book.add_sheet(u'Translations')

    column = 0
    msgctxt_column = msgid_column = occurrences_column = comment_column = tcomment_column = None
    if has_msgctxt:
        msgctxt_column = column
        sheet.write(0, column, ColumnHeaders.msgctxt)
        column += 1

    msgid_column = column
    sheet.write(0, column, ColumnHeaders.msgid)
    column += 1

    if 'reference' in comments or 'all' in comments:
        occurrences_column = column
        sheet.write(0, column, ColumnHeaders.occurrences)
        column += 1

    if 'extracted' in comments or 'all' in comments:
        comment_column = column
        sheet.write(0, column, ColumnHeaders.comment)
        column += 1

    if 'translator' in comments or 'all' in comments:
        tcomment_column = column
        sheet.write(0, column, ColumnHeaders.tcomment)
        column += 1

    msgstr_column = column
    for (i, cat) in enumerate(catalogs):
        sheet.write(0, column, cat[0])
        column += 1

    row = 1
    ref_catalog = catalogs[0][1]
    with click.progressbar(messages, label='Writing catalog to sheet') as todo:
        for (msgid, msgctxt, message) in todo:
            if msgctxt_column is not None:
                sheet.write(row, msgctxt_column, msgctxt)
            sheet.write(row, msgid_column, msgid)
            msg = ref_catalog.find(msgid)
            if occurrences_column is not None:
                o = []
                if msg is not None:
                    for (entry, lineno) in msg.occurrences:
                        if lineno:
                            o.append(u'%s:%s' % (entry, lineno))
                        else:
                            o.append(entry)
                sheet.write(row, occurrences_column, u', '.join(o))
            if comment_column is not None:
                if msg is not None:
                    sheet.write(row, comment_column, msg.comment)
            if tcomment_column is not None:
                if msg is not None:
                    sheet.write(row, tcomment_column, msg.tcomment)
            for (column, cat) in enumerate(catalogs, msgstr_column):
                cat = cat[1]
                msg = cat.find(msgid)
                if msg is not None:
                    if 'fuzzy' in msg.flags:
                        sheet.write(row, column, msg.msgstr, italic_style)
                    else:
                        sheet.write(row, column, msg.msgstr)
                column += 1
            row += 1

    book.save(output)


if __name__ == '__main__':
    main()
