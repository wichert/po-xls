import os
import click
import polib
import openpyxl
from openpyxl.styles import Font
from openpyxl.writer.dump_worksheet import WriteOnlyCell
from . import ColumnHeaders


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

    fuzzy_font = Font(italic=True, bold=True)

    messages = []
    seen = set()
    for (_, catalog) in catalogs:
        for msg in catalog:
            if not msg.msgid or msg.obsolete:
                continue
            if msg.msgid not in seen:
                messages.append((msg.msgid, msg.msgctxt, msg))
                seen.add(msg.msgid)

    book = openpyxl.Workbook(write_only=True)
    sheet = book.create_sheet(title=u'Translations')

    row = []
    has_msgctxt_column = has_occurrences_column = has_comment_column = has_tcomment_column = None
    if has_msgctxt:
        has_msgctxt_column = True
        row.append(ColumnHeaders.msgctxt)
    row.append(ColumnHeaders.msgid)
    if 'reference' in comments or 'all' in comments:
        has_occurrences_column = True
        row.append(ColumnHeaders.occurrences)
    if 'extracted' in comments or 'all' in comments:
        has_comment_column = True
        row.append(ColumnHeaders.comment)
    if 'translator' in comments or 'all' in comments:
        has_tcomment_column = True
        row.append(ColumnHeaders.tcomment)

    for (i, cat) in enumerate(catalogs):
        row.append(cat[0])
    sheet.append(row)

    ref_catalog = catalogs[0][1]

    with click.progressbar(messages, label='Writing catalog to sheet') as todo:
        for (msgid, msgctxt, message) in todo:
            row = []
            if has_msgctxt_column is not None:
                row.append(msgctxt)
            row.append(msgid)
            msg = ref_catalog.find(msgid)
            if has_occurrences_column:
                o = []
                if msg is not None:
                    for (entry, lineno) in msg.occurrences:
                        if lineno:
                            o.append(u'%s:%s' % (entry, lineno))
                        else:
                            o.append(entry)
                row.append(u', '.join(o) if o else None)
            if has_comment_column:
                row.append(msg.comment if msg is not None else None)
            if has_tcomment_column:
                row.append(msg.tcomment if msg is not None else None)
            for cat in catalogs:
                cat = cat[1]
                msg = cat.find(msgid)
                if msg is None:
                    row.append(None)
                elif 'fuzzy' in msg.flags:
                    cell = WriteOnlyCell(sheet, value=msg.msgstr)
                    cell.font = fuzzy_font
                    row.append(cell)
                else:
                    row.append(msg.msgstr)
            sheet.append(row)

    sheet.freeze_panes = 'B1'
    book.save(output)


if __name__ == '__main__':
    main()
