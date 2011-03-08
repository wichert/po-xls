import argparse
import os.path
import re
import sys
import xlrd
import xlwt
from babel.messages.pofile import read_po
from babel.messages.pofile import write_po

VARIABLE_RE = re.compile(r"\${(.*?)}")

def replaceCatalog(filename, catalog):
    tmpfile=filename+"~"
    output=open(tmpfile, "w")
    write_po(output, catalog)
    output.close()
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
    if default.count("|")!=translation.count("|"):
        print >> sys.stderr, ("Bad translation in cell %s:%s: different number of texts." %
                (sheet.name, CellId(row, column)))
        fuzzy=True

    if getVariables(default)!=getVariables(translation):
        print >> sys.stderr, ("Bad translation in cell %s:%s: different variables used." %
                (sheet.name, CellId(row, column)))
        fuzzy=True

    if msgid not in catalog:
        print >>sys.stderr, ("Can not find translation for cell %s:%s in PO file." %
                (sheet.name, CellId(row, column)))
        return False

    msg=catalog[msgid]
    msg.string=translation
    if fuzzy and not msg.fuzzy:
        msg.flags.add("fuzzy")
    elif not fuzzy and msg.fuzzy:
        msg.flags.remove("fuzzy")



def ConvertXlsPo():
    import lingua.monkeys
    lingua.monkeys.applyPatches()

    parser=argparse.ArgumentParser(
            description="Merge translation from XLS file to a .PO file")

    parser.add_argument("locale", metavar="<locale>", help="Locale to process")
    parser.add_argument("input_file", metavar="<xls file>", help="Input XLS file")
    parser.add_argument("output_file", metavar="<po file>", help="PO file to update")
    options=parser.parse_args()

    book=xlrd.open_workbook(filename=options.input_file, logfile=sys.stderr)
    catalog=read_po(open(options.output_file))

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
    import lingua.monkeys
    lingua.monkeys.applyPatches()

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
        catalogs.append((locale, read_po(open(path))))

    messages=[]
    seen=set()
    for catalog in catalogs:
        for msg in catalog[1]:
            if not msg.id:
                continue
            if msg.id not in seen:
                default=u" ".join(msg.auto_comments)
                if default.startswith("Default: "):
                    default=default[9:]
                messages.append((msg.id, default))
                seen.add(msg.id)

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
            if msgid in cat:
                msg=cat[msgid]
                if msg.fuzzy:
                    sheet.write(row, i+2, msg.string, italic_style)
                else:
                    sheet.write(row, i+2, msg.string)
        row+=1

    book.save(options.output_file)

