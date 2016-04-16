.. image:: https://img.shields.io/travis/Nekmo/python-akismet.svg?style=flat-square&maxAge=2592000
  :target: https://travis-ci.org/Nekmo/python-akismet
  :alt: Latest Travis CI build status

.. image:: https://img.shields.io/pypi/v/python-akismet.svg?style=flat-square
  :target: https://pypi.python.org/pypi/python-akismet
  :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/pyversions/python-akismet.svg?style=flat-square
  :target: https://pypi.python.org/pypi/python-akismet
  :alt: Python versions

.. image:: https://img.shields.io/codeclimate/github/Nekmo/python-akismet.svg?style=flat-square
  :target: https://codeclimate.com/github/Nekmo/python-akismet
  :alt: Code Climate

.. image:: https://img.shields.io/codecov/c/github/Nekmo/python-akismet/master.svg?style=flat-square
  :target: https://codecov.io/github/Nekmo/python-akismet
  :alt: Test coverage

.. image:: https://img.shields.io/requires/github/Nekmo/python-akismet.svg?style=flat-square
     :target: https://requires.io/github/Nekmo/python-akismet/requirements/?branch=master
     :alt: Requirements Status


Python-akismet
##############

Pykismet3 fork. Support older versions of Python and improvements.

Supported API
=============

The Following Akismet API Calls are currently supported:

- Comment Check
- Submit Ham
- Submit Spam

Unsupported API
===============

The following Akismet API Calls are not yet supported:
* Key Verification

Installation
============

1. Signup for Akismet and get yourself an API key at http://akismet.com/plans/ (You don't need to pay)

2. Install this library::

    pip install python-akismet

3. Make some calls to Akismet (see example below to get started)

Example
=======

Import and instance Akismet.

.. code-block:: python

    from akismet import Akismet

    # API KEY (first argument) is required. blog can be defined later.
    akismet = Akismet('1ba29d6f120c', blog="http://your.blog/url",
                      user_agent="My Application Name/0.0.1")


Comment Check
-------------

.. code-block:: python

    akismet.check('192.168.1.3', 'Firefox / COMMENT USER AGENT', comment_author='King Arthur',
                  comment_author_email='arthur@camelot.co.uk', comment_author_url='http://camelot.co.uk',
                  comment_content='The Lady of the Lake, her arm clad in the purest shimmering samite, '
                                   'held aloft Excalibur from the bosom of the water, signifying by divine'
                                   ' providence that I, Arthur, was to carry Excalibur. That is why I '
                                   'am your king.', referrer='http://camelot-search/?q=Peasant+Woman')

Submit Ham
----------

.. code-block:: python

    akismet.submit_ham('192.168.1.12', 'FIREFOX / COMMENT USER AGENT', comment_author='Tim',
                       comment_author_email='tim@witch.co.uk',
                       comment_author_url='http://witch.co.uk',
                       comment_content="Look, that rabbit's got a vicious streak a mile wide!"
                                       "It's a killer!")

Submit Spam
-----------

.. code-block:: python

    akismet.submit_spam('192.168.1.4', 'FIREFOX / COMMENT USER AGENT', comment_author='Frenchman',
                        comment_author_email='frenchman@guy-de-lombard.fr',
                        comment_author_url='http://guy-de-lombard.fr',
                        comment_content="You don't frighten us, English pig-dogs! Go and boil your "
                                        "bottoms, sons of a silly person! I blow my nose at you, "
                                        "so-called Ah-thoor Keeng, you and all your silly English "
                                        "K-n-n-n-n-n-n-n-niggits!")

Documentation
#############

The examples above show you pretty much everything you need to know.

For a full list of supported parameters for each API call, see http://akismet.com/development/api/

The code is only ~100 lines long anyway, so just look at '''akismet''' if you aren't sure about something.

