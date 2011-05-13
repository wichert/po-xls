from setuptools import setup, find_packages
import sys

version = "1.0b1"

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
          "Programming Language :: Python :: 2.4",
          "Programming Language :: Python :: 2.5",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords="",
      author="Wichert Akkerman",
      author_email="wichert@wiggy.net",
      url="",
      license="BSD",
      packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      po-to-xls = lingua.xlsconvert:ConvertPoXls
      xls-to-po = lingua.xlsconvert:ConvertXlsPo

      [babel.extractors]
      lingua_python = lingua.extractors.python:extract_python
      lingua_xml = lingua.extractors.xml:extract_xml
      lingua_zcml = lingua.extractors.zcml:extract_zcml
      """
      )
