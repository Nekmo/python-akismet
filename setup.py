import os

from setuptools import setup

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='pykismet3',
    version='0.1.1',
    description='A Python 3 module for the Akismet spam comment-spam-detection web service.',
    long_description=(read('README.md')),
    url='https://github.com/grundleborg/pykismet3',
    license='MIT',
    author='George Goldberg',
    author_email='george@grundleborg.com',
    py_modules=['pykismet3'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[ "requests", ],
)
