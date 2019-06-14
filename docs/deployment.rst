.. This Source Code Form is subject to the terms of the Mozilla Public
.. License, v. 2.0. If a copy of the MPL was not distributed with this
.. file, You can obtain one at http://mozilla.org/MPL/2.0/.

Deployment Considerations
=========================

Django Settings Module
----------------------

Django uses the environment variable ``DJANGO_SETTINGS_MODULE`` to determine which Python module to import as the Django settings. Per the `Django settings docs`_:

    When you use Django, you have to tell it which settings you’re using. Do this by using an environment variable, ``DJANGO_SETTINGS_MODULE``.

    The value of ``DJANGO_SETTINGS_MODULE`` should be in Python path syntax, e.g. ``mysite.settings``. Note that the settings module should be on the Python `import search path`_.

    **The django-admin utility**

    When using ``django-admin``, you can either set the environment variable once, or explicitly pass in the settings module each time you run the utility.

    Example (Unix Bash shell):

    .. code-block:: console

        $ export DJANGO_SETTINGS_MODULE=mysite.settings
        $ django-admin runserver

    Example (Windows shell):

    .. code-block:: powershell

        > set DJANGO_SETTINGS_MODULE=mysite.settings
        > django-admin runserver

    Use the ``--settings`` command-line argument to specify the settings manually:

    .. code-block:: console

        $ django-admin runserver --settings=mysite.settings

    --- `Django settings docs`_

.. _import search path: https://www.diveinto.org/python3/your-first-python-program.html#importsearchpath
.. _Django settings docs: https://docs.djangoproject.com/en/dev/topics/settings/#designating-the-settings

Settings in Production
^^^^^^^^^^^^^^^^^^^^^^

In most cases, you do not have to worry about explicitly setting the Django settings module on the production server. This is because most entry points for interacting with Django (namely, ``manage.py`` and ``troop89/wsgi.py``) will default to using ``troop89.settings.prod``.

Note that if you use ``django-admin`` in place of ``manage.py`` when executing Django commands, you will have to explicitly define the settings module with ``DJANGO_SETTIGNS_MODULE`` or the ``--settings`` flag, as explained above.

Settings in Development
^^^^^^^^^^^^^^^^^^^^^^^

For development, you’ll want to use the ``troop89.settings.dev`` setting module. This module adds some helpful development tools such as the django debug toolbar and removes some access constraints such as forced redirects to HTTPS.

This can be explicitly set  by setting the ``DJANGO_SETTINGS_MODULE`` variable, or by passing the ``—settings`` flag to ``manage.py`` or ``django-admin``, as detailed above.

Initializing the ``sites`` app
------------------------------

The Troop 89 website makes use of the `Django sites framework`_. In order for the website to function, a ``Site`` model with an appropriate domain name needs to be added to the database.

Since the domain name that the Troop 89 websites operates behind will vary between instances, this model is not created by a database migration.

For development, a default model is provided in a fixture. See :ref:`install-populate-database` for details on how to load it.

For production, you must manually create the ``Site`` model. This can be accomplished in three ways:

1.  **Load a fixture**. Created a file (say ``prod_site.json``) with the following contents

    .. code-block:: json

        [{"model": "sites.site", "pk": 1, "fields": {"domain": "YOUR_DOMAIN_NAME", "name": "Troop 89 Website"}}]

    where ``YOUR_DOMAIN_NAME`` is the domain for the production server. Then, execute the following command:

    .. code-block:: console

        ./manage.py loaddata ./prod_site.json

2.  **Use the Djano Admin**. If your Django instance is already running, you can navigate to ``YOUR_DOMAIN_NAME/admin/sites/site/1/change/`` to update the default site model with the correct domain name.

3.  **Use the Django shell**. Start a `Django shell`_ session and enter the following:

    .. code-block:: pycon

        >>>  from django.contrib.sites.models import Site
        >>> site = Site(pk=1, domain='YOUR_DOMAIN_NAME', name='Troop 89 Website')
        >>> site.save()

    Note that your should not use ``Site.objects.create()``, since you want to override the default site rather than create a new one.


.. _Django sites framework: https://docs.djangoproject.com/en/2.2/ref/contrib/sites/
.. _Django shell: https://docs.djangoproject.com/en/2.2/ref/django-admin/#shell

.. _deployment-database-config:

Database Configuration
----------------------

The Troop 89 website is designed and tested with a `PostgreSQL`_ database server. It is highly recommended that you continue to use a PostgreSQL database in production to ensure that no compatibility errors occur. At the time of this writing, Django requires PostregreSQL 9.4 or higher. See the `Django database installation docs`_ for further details on how to run Django with a PostgreSQL backend.

.. _PostgreSQL: https://www.postgresql.org/
.. _Django database installation docs: https://docs.djangoproject.com/en/2.2/topics/install/#database-installation

Redirecting Traffic to HTTPS
----------------------------

The Troop 89 website implements `many web security standards`_ to ensure the safety its users' data. Notably, the Troop 89 website is configured for `HTTPS Strict-Transport-Security`_, which mandates that browsers only access the site over an encrypted connection.

To ensure compatibility with HSTS standards, the production server should always redirect HTTP traffic to HTTPS. How this is accomplished will vary between web servers and hosts.

If you are running the Troop 89 website on a Apache server, `Webfaction recommends`_ directing all HTTP traffic to a site that has an ``.htaccess`` file with the following rules:

.. code-block:: apacheconf

  RewriteEngine On
  RewriteCond %{HTTP:X-Forwarded-SSL} !on
  RewriteCond %{REQUEST_URI} !^/(.well-known)(/|$)
  RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]

.. note::

    The ``troop89.settings.prod`` setting module defines the ``SECURE_SSL_REDIRECT`` option for Django’s SecurityMiddleware. When this option is set, Django will emit a permanent redirect to HTTPS whenever it receives a request over HTTP. However, it is recommended that this redirect be performed by the webserver itself instead of Django. Performing redirects with the webserver will yield better performance and will reduce the risk of misconfiguration in the future.



.. _many web security standards: https://observatory.mozilla.org/analyze/troop89medfield.org
.. _HTTPS Strict-Transport-Security: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security
.. _Webfaction recommends: https://docs.webfaction.com/software/static.html#redirecting-from-http-to-https




