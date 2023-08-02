# coding: utf-8

from setuptools import setup

setup(
    name='clg-conf',
    version='1.0.0',
    author='François Ménabé',
    author_email='francois.menabe@gmail.com',
    #url = 'https://clg.readthedocs.org/en/latest/',
    url = 'http://github.com/fmenabe/python-clg-conf',
    download_url = 'http://github.com/fmenabe/python-clg-conf',
    license='MIT License',
    description='Manage per command configuration files.',
    long_description=open('README.rst').read(),
    keywords=['command-line', 'argparse', 'wrapper', 'clg'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
    ],
    packages=['clg/conf'],
    install_requires=['clg', 'addict'])
