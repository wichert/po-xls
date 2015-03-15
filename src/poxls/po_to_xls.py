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


@click.command(help='Convert .PO files to an XLSX file')
@click.option('--comments', multiple=True,
        type=click.Choice(['translator', 'extracted', 'reference', 'all']))
@click.option('-p', nargs=2, multiple=True, required=True,
    help=u'Locale and filename of po-file to process')
@click.argument('output_file', type=click.File('wb'), required=True)
def main(comments, p, output_file):
    has_msgctxt = False
    catalogs = []
    for (locale, path) in p:
        input = path
        catalogs.append((locale, polib.pofile(input)))
        has_msgctxt = has_msgctxt or any(m.msgctxt for m in catalogs[-1][1])

    messages = []
    seen = set()
    for catalog in catalogs:
        for msg in catalog[1]:
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
    for (msgid, msgctxt, message) in messages:
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

    book.save(output_file)


if __name__ == '__main__':
    main()
