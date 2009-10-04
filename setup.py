from distutils.core import setup
import sys

setup(name='magro',
      version='1.0',
      author='Isaac Rivas',
      author_email='isaac@isaacrivas.com',
      url='http://github.com/isaacrivas/magro',
      download_url='http://github.com/isaacrivas/magro',
      description='Template engine for lean code.',
      long_description='A general purpose template engine ideal for hierarchised languages such as html.',
      packages=['magro'],
      provides=['magro'],
      keywords='templates',
      license='Public Domain',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'License :: Public Domain',
                   'Topic :: Software Development'
                   'Topic :: Software Development :: Libraries',
                  ],
      requires='ply'
     )
