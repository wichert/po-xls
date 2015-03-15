import argparse
import re
import sys
import xlrd
import xlwt
import polib


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
        print >> sys.stderr, ('Missing message id in cell %s:%s' %
                (sheet.name, cell_id(row, 1)))
        return None

    msg = catalog.find(msgid, msgctxt or False)
    if msg is None:
        print >> sys.stderr, \
                ('Can not find translation for cell %s:%s in PO file.' %
                (sheet.name, cell_id(row, 0)))
        return None

    return msg


class CommentAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        options = ['translator', 'extracted', 'reference']
        values = [v.strip() for v in values.split(',')]
        comments = set()
        for value in values:
            if value == 'all':
                comments.update(options)
                break
            elif value in options:
                comments.add(value)
            else:
                raise argparse.ArgumentError(self, 'Invalid comment option')
        setattr(namespace, self.dest, comments)


def ConvertPoXls():
    parser = argparse.ArgumentParser(
            description='Convert Po files for a domain to an Excel file.')
    parser.add_argument('--comments',
            action=CommentAction, default='extracted',
            help='Comments to include in xls file. This is a comma separated '
                 'list of "translator", "extracted", "reference" or "all".')
    parser.add_argument('-p',
            dest='input', action='append', nargs=2, required=True,
            metavar=('<locale>', '<po file>'),
            help='Locale and filename of po-file to process')
    parser.add_argument('output_file', metavar='<xls file>',
            help='Output XLS file')
    options = parser.parse_args()

    catalogs = []
    for (locale, path) in options.input:
        catalogs.append((locale, polib.pofile(path)))

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
    if 'reference' in options.comments:
        sheet.write(0, column, u'References')
        column += 1
    if 'extracted' in options.comments:
        sheet.write(0, column, u'Source comment')
        column += 1
    if 'translator' in options.comments:
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
        if 'reference' in options.comments:
            o = []
            if msg is not None:
                for (entry, lineno) in msg.occurrences:
                    if lineno:
                        o.append(u'%s:%s' % (entry, lineno))
                    else:
                        o.append(entry)
            sheet.write(row, column, u', '.join(o))
            column += 1
        if 'extracted' in options.comments:
            if msg is not None:
                sheet.write(row, column, msg.comment)
            column += 1
        if 'translator' in options.comments:
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

    book.save(options.output_file)
