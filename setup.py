from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='plone.app.contentlisting',
      version=version,
      description="Listing of content for the Plone CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Geir B\xc3\xa6kholt',
      author_email='baekholt@jarn.com',
      url='http://svn.plone.org/svn/plone/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points = '''
          [z3c.autoinclude.plugin]
          target = plone
      ''',
      )
