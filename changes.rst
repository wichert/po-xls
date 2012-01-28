Changelog
=========

1.3 - January 28, 2012
----------------------

- XLS->Po conversion failed for the first language if no comment or
  reference columns were generated. Reported by Rocky Feng.

- Properly support Windows in the xls-po convertors: Windows does not
  support atomic file renames, so revert to shutils.rename on that
  platform. Reported by Rocky Feng.


1.2 - January 13, 2012
----------------------

- Extend XML extractor to check python expressions in templates. This
  fixes `issue 7 <https://github.com/wichert/lingua/pull/7>`_. Thanks to
  Nuno Teixeira for the patch.


1.1 - November 16, 2011
-----------------------

- Set 'i18n' attribute as default prefix where there was no prefix found.
  This fixes issues `5 <https://github.com/wichert/lingua/issues/5>`_ and
  `6 <https://github.com/wichert/lingua/issues/5>`_. Thanks to
  Mathieu Le Marec - Pasquet for the patch.


1.0 - September 8, 2011
-----------------------

- Update XML extractor to ignore elements which only contain a Chameleon
  expression (``${....}``). These can happen to give the template engine
  a hint that it should try to translate the result of an expression. This
  fixes `issue 2 <https://github.com/wichert/lingua/issues/2>`_.

* Update XML extractor to not abort when encountering undeclared
  namespaces. This fixes `issue 3
  <https://github.com/wichert/lingua/issues/3>`_.

* Fix Python extractor to handle strings split over multiple lines
  correctly.


1.0b4 - July 20, 2011
---------------------

* Fix po-to-xls when including multiple languages in a single xls file.


1.0b3 - July 18, 2011
---------------------

* Paper brown bag: remove debug leftover which broke po-to-xls.


1.0b2 - July 18, 2011
---------------------

* Update PO-XLS convertors to allow selection of comments to include in
  the xls files.

* Correct XML extractor to strip leading and trailing white. This fixes
  `issue 1 <https://github.com/wichert/lingua/issues/1>`_.

* Add a very minimal polint tool to perform sanity checks in PO files.

* Update trove data: Python 2.4 is not supported due to lack of absolute
  import ability.


1.0b1 - May 13, 2011
--------------------

* First release.
