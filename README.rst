Translating via spreadsheets
============================

Not all translators are comfortable with using PO-editors such as `Poedit
<http://www.poedit.net/>`_ or translation tools like `Transifex
<http://trac.transifex.org/>`_. For them this package provides simple tools to
convert PO-files to `xlsx`-files and back again. This also has another benefit:
it is possible to include multiple languages in a single spreadsheet, which can be
helpful when translating to multiple similar languages at the same time (for
example simplified and traditional chinese).

The format for spreadsheets is simple: 

* If any message use a message context the first column will specify the
  context.  If message contexts are not used this column will be skipped.
* The next (or first) column contains the message id. This is generally the
  canonical text.
* A set of columns for any requested comment types (message occurrences, source
  comments or translator comments).
* A column with the translated text for each locale. Fuzzy translations are
  marked in italic.

The first row contains the column headers. *``xls-to-po`` uses these to locale
information in the file, so make sure never to change these!*


Catalog to spreadshseet
-----------------------

Converting one or more PO-files to an xls file is done with the `po-to-xls`
command::

    po-to-xls nl.po

This will create a new file `messages.xlsx` with the Dutch translations. Multiple
PO files can be specified::

    po-to-xls -o texts.xlsx zh_CN.po zh_TW.po nl.po

This will generate a ``texts.xlsx`` file with all simplified Chinese,
traditional Chinese and Dutch translations.

``po-to-xls`` will guess the locale for a PO file by looking at the `Language`
key in the file metadata, falling back to the filename of no language informatino
is specified. You can override this by explicitly specifying the locale on the
commandline. For example:

    po-to-xs nl:locales/nl/LC_MESSAGES/mydomain.po

This will read ``locales/nl/LC_MESSAGES/mydomain.po`` and treat it as Dutch
(``nl`` locale).


Spreadshseet to catalog
-----------------------

Translations can be converted back from a spreadsheet into a PO-file using the
`xls-to-po` command::

    xls-to-po nl texts.xlsx nl.po

This will take the Dutch (`nl`) translations from `texts.xls`, and (re)create a
``nl.po`` file using those. You can merge those into an existing po-file using
a tool like gettext's ``msgmerge``.
