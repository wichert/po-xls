Changelog
=========

1.2.0 - June 12, 2015
---------------------

- Fix ReST syntax error in package description.

- Skip rows without a message id.


1.1.0 - 25 March 2015
---------------------

- Use `openpyxl <http://openpyxl.readthedocs.org/>`_ instead of xlrd/xlwt. This
  fixes warnings about cell type conversions when opening generated xlsx files
  in Apple Numbers (and possibly others).


1.0.0 - 15 March 2015
---------------------

- Split po-excel conversion tools out from `lingua <https://github.com/wichert/lingua>`_.

- Simplify CLI interfaces.
