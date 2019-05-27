.. This Source Code Form is subject to the terms of the Mozilla Public
.. License, v. 2.0. If a copy of the MPL was not distributed with this
.. file, You can obtain one at http://mozilla.org/MPL/2.0/.

Running the Tests
=================

The unit tests for the troop 89 website are pretty sparse at the moment. Contributions are always welcome!

Unit tests can be run via Django's test runner::

    $ ./manage.py test

To speed-up the tests by running them in parallel, you can pass the ``--parallel`` flag. To preserve the testing database after the tests run, you pass the ``--keepdb`` flag.

For more information, see the `Django testing`_ docs.

.. _Django testing: https://docs.djangoproject.com/en/2.2/topics/testing/overview/
