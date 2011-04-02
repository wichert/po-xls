import argparse
import os.path
import re
import sys
import xlrd
import xlwt
import polib

VARIABLE_RE = re.compile(r"\${(.*?)}")

def replaceCatalog(filename, catalog):
    tmpfile=filename+"~"
    catalog.save(tmpfile)
    os.rename(tmpfile, filename)



def toBase26(value):
    if not value:
        return "A"
    output=[]
    while value:
        digit=value%26
        if output:
            digit-=1
        output.append(chr(ord('A')+digit))
        value/=26
    return "".join(reversed(output))



def CellId(row, column):
    return "%s%d" % (toBase26(column), row+1)



def CellString(sheet, row, col):
    cell=sheet.cell(row, col)
    if cell.ctype!=xlrd.XL_CELL_TEXT:
        return None
    return cell.value.strip()


def checkRow(sheet, row):
    msgid=CellString(sheet, row, 0)
    if not msgid:
        print >>sys.stderr, ("Missing message id in cell %s:%s" %
                (sheet.name, CellId(row, 0)))
        return False

    return True



def getVariables(text):
    variables=set(VARIABLE_RE.findall(text))
    if "newline" in variables:
        variables.remove("newline")
    return variables



def addRow(catalog, sheet, row, column):
    msgid=CellString(sheet, row, 0)
    default=CellString(sheet, row, 1)
    if not default:
        default=msgid

    translation=CellString(sheet, row, column)
    if not translation:
        return False

    fuzzy=False
    if getVariables(default)!=getVariables(translation):
        print >> sys.stderr, ("Bad translation in cell %s:%s: different variables used." %
                (sheet.name, CellId(row, column)))
        fuzzy=True

    msg=catalog.find(msgid)
    if msg is None:
        print >>sys.stderr, ("Can not find translation for cell %s:%s in PO file." %
                (sheet.name, CellId(row, column)))
        return False

    msg.msgstr=translation
    if fuzzy and "fuzzy" not in msg.flags: 
        msg.flags.append("fuzzy")
    elif not fuzzy and "fuzzy" in msg.flags:
        msg.flags.remove("fuzzy")



def ConvertXlsPo():
    parser=argparse.ArgumentParser(
            description="Merge translation from XLS file to a .PO file")

    parser.add_argument("locale", metavar="<locale>", help="Locale to process")
    parser.add_argument("input_file", metavar="<xls file>", help="Input XLS file")
    parser.add_argument("output_file", metavar="<po file>", help="PO file to update")
    options=parser.parse_args()

    book=xlrd.open_workbook(filename=options.input_file, logfile=sys.stderr)
    catalog=polib.pofile(options.output_file)

    found_locale=False
    for sheet in book.sheets():
        for col in range(2, sheet.ncols):
            locale=CellString(sheet, 0, col)
            if locale!=options.locale:
                continue
            found_locale=True

            for row in range(1, sheet.nrows):
                if not checkRow(sheet, row):
                    continue
                addRow(catalog, sheet, row, col)

    if not found_locale:
        print >>sys.stderr, "No translations found for locale %s" % options.locale
        sys.exit(1)

    replaceCatalog(options.output_file, catalog)



def ConvertPoXls():
    parser=argparse.ArgumentParser(
            description="Convert Po files for a domain to an Excel file.")
    parser.add_argument("-p",
            dest="input", action="append", nargs=2, required=True,
            metavar=("<locale>", "<po file>"),
            help="Locale and filename of po-file to process")
    parser.add_argument("output_file", metavar="<xls file>",
            help="Output XLS file")
    options=parser.parse_args()

    catalogs=[]
    for (locale, path) in options.input:
        catalogs.append((locale, polib.pofile(path)))

    messages=[]
    seen=set()
    for catalog in catalogs:
        for msg in catalog[1]:
            if not msg.msgid:
                continue
            if msg.msgid not in seen:
                default=msg.comment
                if default.startswith("Default: "):
                    default=default[9:]
                messages.append((msg.msgid, default))
                seen.add(msg.msgid)

    book=xlwt.Workbook(encoding="utf-8")
    italic_style=xlwt.XFStyle()
    italic_style.num_format_str="Italic"
    italic_style.font.italic=True
    italic_style.font.bold=True
    sheet=book.add_sheet(u"Translations")
    row=1
    sheet.write(0, 0, u"Message id")
    sheet.write(0, 1, u"Default text")
    for (i, cat) in enumerate(catalogs):
        sheet.write(0, i+2, cat[0])

    for (msgid, default) in messages:
        sheet.write(row, 0, msgid)
        sheet.write(row, 1, default)
        for (i, cat) in enumerate(catalogs):
            cat=cat[1]
            msg=cat.find(msgid)
            if msgid is not None:
                if "fuzzy" in msg.flags:
                    sheet.write(row, i+2, msg.msgstr, italic_style)
                else:
                    sheet.write(row, i+2, msg.msgstr)
        row+=1

    book.save(options.output_file)

