from setuptools import setup, find_packages
import sys

version = "1.3"

install_requires=[
        "polib",
        "xlrd",
        "xlwt",
        ]
if sys.version_info<(2,7):
    install_requires.append("argparse")

setup(name="lingua",
      version=version,
      description="Translation toolset",
      long_description=open('README.rst').read() + '\n' + \
              open('changes.rst').read(),
      classifiers=[
          "Intended Audience :: Developers",
          "License :: DFSG approved",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='translation po gettext Babel',
      author="Wichert Akkerman",
      author_email="wichert@wiggy.net",
      url='https://github.com/wichert/lingua',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=True,
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      po-to-xls = lingua.xlsconvert:ConvertPoXls
      xls-to-po = lingua.xlsconvert:ConvertXlsPo
      polint = lingua.polint:main

      [babel.extractors]
      lingua_python = lingua.extractors.python:extract_python
      lingua_xml = lingua.extractors.xml:extract_xml
      lingua_zcml = lingua.extractors.zcml:extract_zcml
      """
      )
