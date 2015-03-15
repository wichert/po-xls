import re
import click
import polib
import xlrd
import xlwt


VARIABLE_RE = re.compile(r"\${(.*?)}")


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
    catalogs = []
    for (locale, path) in p:
        input = path
        catalogs.append((locale, polib.pofile(input)))

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
    sheet.write(0, column, u'Message context')
    column += 1
    sheet.write(0, column, u'Message id')
    column += 1
    if 'reference' in comments or 'all' in comments:
        sheet.write(0, column, u'References')
        column += 1
    if 'extracted' in comments or 'all' in comments:
        sheet.write(0, column, u'Source comment')
        column += 1
    if 'translator' in comments or 'all' in comments:
        sheet.write(0, column, u'Translator comment')
        column += 1
    for (i, cat) in enumerate(catalogs):
        sheet.write(0, column, cat[0])
        column += 1

    row = 1
    ref_catalog = catalogs[0][1]
    for (msgid, msgctxt, message) in messages:
        column = 0
        sheet.write(row, column, msgctxt)
        column += 1
        sheet.write(row, column, msgid)
        column += 1
        msg = ref_catalog.find(msgid)
        if 'reference' in comments or 'all' in comments:
            o = []
            if msg is not None:
                for (entry, lineno) in msg.occurrences:
                    if lineno:
                        o.append(u'%s:%s' % (entry, lineno))
                    else:
                        o.append(entry)
            sheet.write(row, column, u', '.join(o))
            column += 1
        if 'extracted' in comments or 'all' in comments:
            if msg is not None:
                sheet.write(row, column, msg.comment)
            column += 1
        if 'translator' in comments or 'all' in comments:
            if msg is not None:
                sheet.write(row, column, msg.tcomment)
            column += 1
        for (i, cat) in enumerate(catalogs):
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
