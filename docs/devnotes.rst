.. This Source Code Form is subject to the terms of the Mozilla Public
.. License, v. 2.0. If a copy of the MPL was not distributed with this
.. file, You can obtain one at http://mozilla.org/MPL/2.0/.

Notes to Webmasters
===================

Repository Structure
--------------------

The notable parts of the Troop 89 website repository are listed below:

.. code-block:: console

    $ tree -a -L 2 --dirsfirst
    .
    ├── assets
    │   ├── img
    │   ├── scss
    │   └── robots.txt
    ├── bin
    ├── docs
    ├── fixtures
    ├── requirements
    │   ├── base.txt
    │   ├── dev.txt
    │   └── prod.txt
    ├── static
    ├── templates
    │   ├── admin
    │   ├── includes
    ├── troop89
    │   ├── announcements
    │   ├── auth
    │   ├── date_range
    │   ├── events
    │   ├── flatpages
    │   ├── json_ld
    │   ├── settings
    │   ├── trooporg
    │   ├── __init__.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── CONTRIBUTING.rst
    ├── demo.secrets.json
    ├── LICENSE
    ├── manage.py
    ├── README.rst
    └── requirements.txt
    ├── .coveragerc
    ├── .secrets.json
    ├── .secrets.json.travis
    ├── .travis.yml

Briefly, the purpose of each file and directory is as follows:

* ``assets``: A directory containing the site-wide `static files`_

    * ``scss``: The site's `Sass`_ stylesheets, which are describe to overall appearance of the site. These files are compiled to CSS before being served by the production server.
    * ``img``: The static media and graphics used by the website.
    * ``robots.txt``: A file that contains instructions for web crawlers, such as those used by Google and other search engines.

* ``bin``: A directory containing executable scripts to help manage the site.
* ``docs``: The root directory for the site's Sphinx documentation.
* ``fixture``: A directory containing `data fixtures`_ for the site's Django models.
* ``requirements``: A directory containing the site's Python package dependencies, which can be installed using ``pip``.

    * ``base.txt``: Fundamental package requirements for both production and development
    * ``prod.txt``: Production-only package requirements
    * ``dev.txt``:  Development-only package requirements, e.g. debug tools, test coverage

* ``static``: The root directory for servable static media. The ``assets`` directory and all ``*/static`` directories are copied here to be served by the production server.
* ``templates``: The root directory for site-wide Django templates, such as the homepage and the error pages.
* ``troop89``: A Python package containing the site's Django apps and configuration files

    * ``announcements``: A Django app for troop announcements.
    * ``auth``: A Django app for custom user authentication.
    * ``date_range``: A helper app for creating models that can reason about ranges of dates.
    * ``events``: A Django app for handling event creation and calendar display.
    * ``flatpages``: A Django app for customized hierarchical flatpages.
    * ``json_ld``: A helper app for rendering json-ld formatted structured data.
    * ``settings``: A Python module for site settings.
    * ``trooporg``: A Django app for troop organization (patrols, election terms, positions, etc).
    * ``__init__.py``: The Python package file.
    * ``urls.py``: The root url configuration.
    * ``wsgi.py``: The WSGI application entry-point.

* ``CONTRIBUTING.rst`` and ``README.rst``: Files containing documentation for the site's repository.
* ``demon.secrets.json``: A configuration file for jump-starting a new site instance for development.
* ``LICENSE``: The project license file (MPL-2.0).
* ``manage.py``: A Python script `provided by Django`_ for managing the site's Django apps.
* ``requirements.txt``: A requirements file that references the production package dependencies. It is equivalent to ``requirements/prod.txt``.
* ``.coveragerc``: A configuration file for the ``coverage`` Python package, which is used generate test coverage data.
* ``.travis.yml`` and ``.secrets.json.travis``: Configuration files for Travis-CI continuous integration.
* ``.secrets.json``: A configuration file for sensitive data, such as database passwords and encryption keys. This file is not kept in version control.


.. _static files: https://docs.djangoproject.com/en/2.2/howto/static-files/
.. _Sass: https://sass-lang.com/
.. _data fixtures: https://docs.djangoproject.com/en/2.2/howto/initial-data/#providing-data-with-fixtures
.. _provided by Django: https://docs.djangoproject.com/en/2.2/ref/django-admin/

External Services
-----------------

Travis CI
^^^^^^^^^

The Troop 89 website uses `Travis CI`_ for `continuous integration`_. Documentation for Travis is `available online`_, though you will likley never need to worry about changing the configuration.

.. _Travis CI: https://travis-ci.com/blueschu/troop89medfield.org
.. _continuous integration: https://docs.travis-ci.com/user/for-beginners/#what-is-continuous-integration-ci
.. _available online: https://docs.travis-ci.com/

All configuration for Travis CI is contained in the ``.travis.yml`` file.

Coveralls
^^^^^^^^^

The Troop 89 website uses `Coveralls.io`_ to display its code coverage data. Code coverage analysis is performed by the Python `coverage`_ package. If you have installed the development dependencies, you can generate a manual coverage report by running the following commands

.. code-block:: console

    $ coverage run manage.py test
    $ coverage report

Documentation for ``coverage`` is available on `coverage Read the Docs`_.

.. _Coveralls.io: https://coveralls.io/github/blueschu/troop89medfield.org
.. _coverage: https://pypi.org/project/coverage/
.. _coverage Read the Docs: https://coverage.readthedocs.io/en/v4.5.x/


Coverage data is submitted to `Coveralls.io`_ by a `Travis CI`_ job phase. This step is handled by the `coveralls-python`_ package. Note that the coveralls API key is stored by Travis CI in an environment variable.

.. _coveralls-python: https://github.com/coveralls-clients/coveralls-python

Uptime Robot
^^^^^^^^^^^^

`Uptime Robot`_ periodically monitors the Troop 89 Website for server issues. Uptime statistics are available on the `Troop 89 Website Public Status page`_.

.. _Uptime Robot: https://stats.uptimerobot.com/
.. _Troop 89 Website Public Status page: https://stats.uptimerobot.com/5WPm9SmQZ

Read the Docs
^^^^^^^^^^^^^

Documentation for the Troop 89 website is automatically built and published by `ReadTheDocs.org`_. If you are not already, you can `browse this documentation online`_ through Read the Docs. Otherwise, you can manually build the documentation using `Sphinx`_ by running the following commands.

.. code-block:: console

    $ cd docs
    $ make html

The documentation will then be available in ``_build/html``. Open the ``index.html`` file in a browser to begin browsing the documentation.

.. _ReadTheDocs.org: https://readthedocs.org/
.. _browse this documentation online: https://troop89medfieldorg.readthedocs.io/en/latest/
.. _Sphinx: http://www.sphinx-doc.org/en/master/
