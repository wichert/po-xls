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


def addRow(catalog, locale, sheet, row, column):
    msgid=CellString(sheet, row, 0)
    default=CellString(sheet, row, 1)
    if not default:
        default=msgid

    translation=CellString(sheet, row, column)
    if not translation:
        return False

    fuzzy=False
    if default.count("|")!=translation.count("|"):
        print >> sys.stderr, ("Bad %s translation in cell %s:%s: different number of texts." %
                (locale, sheet.name, CellId(row, column)))
        fuzzy=True

    if getVariables(default)!=getVariables(translation):
        print >> sys.stderr, ("Bad %s translation in cell %s:%s: different variables used." %
                (locale, sheet.name, CellId(row, column)))
        fuzzy=True

    if msgid not in catalog:
        print >>sys.stderr, ("Can not find %s translation for cell %s:%s in PO file." %
                (locale, sheet.name, CellId(row, column)))
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

    parser.add_argument("-l", "--locale", action="append",
            dest="locale",
            help="Locale to process (must be repeated for every translation column)")
    parser.add_argument("input_file", metavar="<xls file>",
            help="Input XLS file")
    parser.add_argument("root_directory", metavar="<directory>",
            help="Locales directory")
    parser.add_argument("domain", metavar="<domain>",
            help="Domain to process")
    options=parser.parse_args()

    if not options.locale:
        print >>sys.stderr, "No locales to process given, aborting."
        sys.exit(1)

    book=xlrd.open_workbook(filename=options.input_file, logfile=sys.stderr)
    catalogs={}
    for locale in options.locale:
        pofile=os.path.join(options.root_directory, locale, "LC_MESSAGES", "%s.po" % options.domain)
        catalogs[locale]=(pofile, read_po(open(pofile)))

    for sheet in book.sheets():
        missing=set(options.locale)
        for col in range(2, sheet.ncols):
            locale=CellString(sheet, 0, col)
            if locale not in catalogs:
                continue
            (_, catalog)=catalogs[locale]
            missing.remove(locale)

            for row in range(1, sheet.nrows):
                if not checkRow(sheet, row):
                    continue
                addRow(catalog, locale, sheet, row, col)

        if missing:
            print >>sys.stderr, "Sheet %s has no translations for: %s" %\
                    (sheet.name, ", ".join(sorted(missing)))

    for (locale, info) in catalogs.items():
        if locale in missing:
            continue
        replaceCatalog(info[0], info[1])



def ConvertPoXls():
    import lingua.monkeys
    lingua.monkeys.applyPatches()

    parser=argparse.ArgumentParser(
            description="Convert Po files for a domain to an Excel file.")
    parser.add_argument("-l", "--locale", action="append",
            dest="locale",
            help="Restrict output to this locale (can be repeated)")
    parser.add_argument("root_directory", metavar="<directory>",
            help="Locales directory")
    parser.add_argument("domain", metavar="<domain>",
            help="Domain to process")
    parser.add_argument("output_file", metavar="<xls file>",
            help="Output XLS file")
    options=parser.parse_args()

    catalogs=[]

    for lang in os.listdir(options.root_directory):
        if lang.startswith("."):
            continue
        if options.locale and lang not in options.locale:
            continue
        path=os.path.join(options.root_directory, lang, "LC_MESSAGES", "%s.po" % options.domain)
        if not os.path.isfile(path):
            continue
        catalogs.append((lang, read_po(open(path))))


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
                sheet.write(row, i+2, cat[msgid].string)
        row+=1

    book.save(options.output_file)

