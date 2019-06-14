.. This Source Code Form is subject to the terms of the Mozilla Public
.. License, v. 2.0. If a copy of the MPL was not distributed with this
.. file, You can obtain one at http://mozilla.org/MPL/2.0/.

Notes to Webmasters
===================

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
