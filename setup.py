from setuptools import setup, find_packages
import sys

version = '1.4.0'

install_requires=[
        'click',
        'polib',
        'openpyxl',
        ]
if sys.version_info<(2,7):
    install_requires.append('argparse')

setup(name='poxls',
      version=version,
      description='Convert between Excel and PO files',
      long_description=open('README.rst').read() + '\n' + \
              open('changes.rst').read(),
      classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: DFSG approved',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          ],
      keywords='translation po gettext Babel lingua',
      author='Wichert Akkerman',
      author_email='wichert@wiggy.net',
      url='https://github.com/wichert/po-xls',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=True,
      install_requires=install_requires,
      entry_points='''
      [console_scripts]
      po-to-xls = poxls.po_to_xls:main
      xls-to-po = poxls.xls_to_po:main
      '''
      )
