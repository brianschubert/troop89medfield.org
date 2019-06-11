.. This Source Code Form is subject to the terms of the Mozilla Public
.. License, v. 2.0. If a copy of the MPL was not distributed with this
.. file, You can obtain one at http://mozilla.org/MPL/2.0/.

.. _install:

Installing the Troop 89 Website
===============================

.. note::

    This guide assumes that you already have Python installed. At the time of this writing, the troop 89 website requires Python 3.6 or greater.

Getting a local copy of the troop 89 website running is a fairly simple process, though there are several steps. This guide is intended to be especially detailed so that it may serve as a partial reference for future webmasters in training.

Fetching the Source
-------------------

The easiest way to get a copy of the troop 89 website source is by cloning the `public github repository`_. This has the added benefit of integrating `git`_ into your development environment, which will be necessary if you intend on making changes to the website's source.

.. code-block:: console

    $ git clone git://github.com/blueschu/troop89medfield.org.git
    $ cd troop89medfield.org

.. _public github repository: https://github.com/blueschu/troop89medfield.org
.. _git: https://git-scm.com/

If you are planning on submitting contributions to the website via a `pull request`_, you should begin by `forking`_ the repository and then cloning that repository instead.

.. _pull request: https://help.github.com/en/articles/about-pull-requests
.. _forking: https://help.github.com/en/articles/fork-a-repo

.. _install-dep:

Installing the Dependencies
---------------------------

You will need to create a virtual environment for Python libraries. If you are using Python3.6+ (which you should be), the tools needed to create virtual environments ship with the interpreter as the `venv`_ module.

.. note::

    Third party packages for creating virtual environments also exist. Some popular options are the `virtualenv`_ and `virtualenvwrapper`_ packages, which preceded the standard `venv`_ module and provide additional convenience tools. Both of these packages can be installed with pip, and can be freely used inplace of the `venv`_ module in the following instructions.

.. _venv: https://docs.python.org/3.6/library/venv.html
.. _virtualenv: https://pypi.org/project/virtualenv/
.. _virtualenvwrapper: https://pypi.org/project/virtualenvwrapper/

To install the site dependencies, execute the following:

.. code-block:: console

    $ python3 -m venv troop89_venv         # Create a virtual environment in the folder 'troop89_venv'
    $ source troop89_venv/bin/active       # Active the virtual environment
    $ pip install -r requirements/dev.txt  # Install the development dependencies

On Windows, run ``venv\Scripts\activate.bat`` in place of ``source troop89_venv/bin/active``.

Compiling the Stylesheets
-------------------------

The stylesheets for our website are written in `sass`_, an extension language to `css`_. You can either install sass system wide, use a feature in your IDE (if one is offered), or you can use the Python `libsass`_ package. Regardless of what method you use, you want to compile all the files in ``assets/scss/*.scss`` that don’t begin with an underscore to ``assets/css/``.

If you have already installed the site dependencies (:ref:`install-dep`), you will have the `libsass`_ package in your virtual environment, which provides the ``sassc`` utility. With this program on your path (which will be the case if you have activated the virtual environment), you can run the following script to compile the stylesheets.

.. code-block:: console

    $ ./bin/build-scss.sh


.. _sass: https://sass-lang.com/
.. _css: https://developer.mozilla.org/en-US/docs/Web/CSS
.. _libsass: https://sass-lang.com/libsass#python

Adding the Configuration File
------------------------------

You will need to create a file called ``.secrets.json`` in the root directory of the project sources. This is a config file that stores sensitive information such as database credentials and encryption keys.

An example configuration is located in the ``demo.secrets.json`` file, which you can temporarily copy to get the site running:

.. code-block:: console

    $ cp demo.secrets.json .secrets.json

This file includes the credentials for an `SQLite`_ database, which is a single-file based relational database that ships with Python. Before beginning significant development, you should install and configure a `PostreSQL`_ database (for which the site is designed) and substitute its credentials into ``.secrets.json``. See :ref:`deployment-database-config` for more details.

.. _SQLite: https://docs.python.org/3/library/sqlite3.html
.. _PostreSQL: https://www.postgresql.org/

Initializing the Database
-------------------------

Assuming all configurations are good, you should only need to run

.. code-block:: console

    $ ./manage.py migrate

This will create the necessary tables and relations, but will not populate the database with data.

.. _install-populate-database:

Populating the Database
-----------------------

The Troop 89 website ships with some default data to populate the database. This data is provided using Django `fixtures`_, which are contained in the ``fixtures`` directory.

To load the default hostnames for the ``django.contrib.sites`` app, run

.. code-block:: console

    $ ./mange.py loaddata ./fixtures/sites.json

To load the demo flatpages, run

.. code-block:: console

    $ ./mange.py loaddata ./fixtures/demo_flatpages.json

.. _fixtures: https://docs.djangoproject.com/en/2.2/howto/initial-data/#providing-data-with-fixtures

Creating the Django Superuser
-----------------------------

Run the following command

.. code-block:: console

    $ ./manage.py createsuperuser

and follow the prompts. This will create a user instance in the database that has all possible site privileges. You will need this to access the site admin.


Collecting the Static Media
---------------------------

Simply run

.. code-block:: console

    $ ./manage.py collectstatic

This will collect the static files and media from across the project into a single directory (``./static/``) so that they can be served by the web server. See the `django staticfiles`_ docs for more information

.. _django staticfiles: https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/

Updating Local Hostnames (Optional)
-----------------------------------

If you would like to use a host name (e.g. troop89.localhost) in place of a numeric IP (e.g. 127.0.0.1) when accessing the development site, you will want to update your machines hostname configuration. For Unix system (MacOS, Linux, etc), add the following entry to your ``/etc/hosts`` file::

    127.0.0.1 troop89.localhost

Note that the ``.localhost`` TLD is `reserved for loop back addresses`_ of this sort. In fact, some browsers will treat ``.localhost`` domains as loop back addresses even without a DNS configuration or modified ``/etc/hosts`` file.

.. _reserved for loop back addresses: https://tools.ietf.org/html/rfc2606

Running the Server
------------------

.. warning::

    The following instructions are for development only. For production, a fully fledged HTTP server such as Apache or Nginx should be used in place of the lightweight server that ships with Django. See the `Django runserver`_ docs for more information.

.. _Django runserver: https://docs.djangoproject.com/en/2.2/ref/django-admin/#django-admin-runserver

To run the testing server, simple run

.. code-block:: console

    $ export DJANGO_SETTINGS_MODULE=troop89.settings.dev  # Use the development settings. Run once per session.
    $ ./mange.py runserver

If you updated your hosts files to include a local hostname, you can run the following instead

.. code-block:: console

    $ ./manage.py runserver troop89.localhost

Do note that by default, the production setting will be used (as defined in ``troop89/wsgi.py``). To run the development flavor, set the environment variables ``DJANGO_SETTINGS_MODULE`` to ``troop89.settings.dev``. This can be done by modifying your ``~/.bashrc`` file (to set it every time you begin a new bash session), by running ``export DJANGO_SETTINGS_MODULE=troop89.settings.dev`` in your terminal (as in the commands above), or by preceding the run server command itself with ``DJANGO_SETTINGS_MODULE=troop89.settings.dev``.
