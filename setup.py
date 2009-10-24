from distutils.core import setup
import sys

from magro.environment import DEFAULT_TEMPLATES_LIBRARY_DIR

setup(name='magro',
      version='1.0',
      author='Isaac Rivas',
      author_email='isaac@isaacrivas.com',
      url='http://github.com/isaacrivas/magro',
      download_url='http://github.com/isaacrivas/magro',
      description='Template engine for lean code.',
      long_description='A general purpose template engine ideal for hierarchised languages such as html.',
      provides=['magro'],
      packages=['magro'],
      package_dir={'magro':'magro'},
      package_data={'magro': [DEFAULT_TEMPLATES_LIBRARY_DIR+'/*']},
      scripts=['scripts/magro_eval'],
      keywords='templates',
      license='Public Domain',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'License :: Public Domain',
                   'Topic :: Software Development',
                   'Topic :: Software Development :: Libraries',
                  ],
      requires=['ply']
     )
