Translating via spreadsheets
============================

Not all translators are comfortable with using PO-editors such as `Poedit
<http://www.poedit.net/>`_ or translation tools like `Transifex
<http://trac.transifex.org/>`_. For them lingua has simple tools to convert
PO-files to `xls`-files and back again. This also has another benefit: it is
possible to include multiple languages in a single spreadsheet, which is
helpful when translating to multiple similar languages at the same time (for
example simplified and traditional chinese).

The format for spreadsheets is simple: the first column lists the canonical
text, and all further columns contain a translation for the text, with the
language code on the first row. Fuzzy translations are marked in italic.

Converting one or more PO-files to an xls file is done with the `po-to-xls`
command::

    po-to-xls -p nl nl.po texts.xls

This will create a new file `texts.xls` with the Dutch translations. The `-p`
parameter can be given multiple times to include more languages::

    po-to-xls -p zh_CN zh_CN.po -p zh_TW zh_TW.po -p nl nl.po texts.xls

This will generate a file with all simplified chinese, traditional chinese and
Dutch translations.


Translations can be merged back from a spreadsheet into a PO-file using the
`xls-to-po` command::

    xls-to-po nl texts.xls nl.po

This will take the Dutch (`nl`) translations from `texts.xls` and use those to
upgrade the `nl.po` file.
