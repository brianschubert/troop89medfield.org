.. This Source Code Form is subject to the terms of the Mozilla Public
.. License, v. 2.0. If a copy of the MPL was not distributed with this
.. file, You can obtain one at http://mozilla.org/MPL/2.0/

Contributing to the Troop 89 Website
====================================

How Can I Contribute?
---------------------

Members of Troop 89 are welcome and encouraged to contribute to the website in any way that they can. Common ways to contribute include `Reporting a Bug`_ that you found or `Requesting a Feature`_ to be implemented by the webmasters.

All members of Troop 89, particular those holding leadership positions such as Historian or Scribe, are welcome to submit content to be published on our website. If you are interested contributing in this way, please contact our webmasters over email or during a weekly meeting.

Scout who are interested in exploring the fields of web design, computer science, graphic design, or any of their relatives are encouraged to help with the maintenance of the troop's website. Possible ways to contribute include:

- Improving the presentation of our website by modifying the `stylesheets`_
- Creating artwork or media to be posted to our website
- Developing new features for the website with the `Django framework`_

.. _stylesheets: https://developer.mozilla.org/en-US/docs/Web/CSS
.. _Django framework: https://www.djangoproject.com/


Reporting a Bug
---------------

Bugs are tracked with `GitHub issues`_. Before reporting a bug, be sure to check if it has already been reported by searching the `existing issues`_ on GitHub. If no report exists, go ahead a submit a `new issue`_.

When submitting a report, be sure to include sufficient details for our webmasters to replicate the problem:

- Use a clear and descriptive title for the issue to identify the problem.
- Describe the exact steps to reproduce the problem with as many details as possible.
- Explain the behavior you expected to see instead and why.

When reporting a bug that affects the visual appearance of the Troop 89 website, please also provide details about how you are accessing the website. Specifically, please note what browser you are using along with any details about your system that may be relevant to the issue, such as Ad-blocking software.

You may also consider submitting a patch for the bug by `Making a Pull Request`_.

.. _GitHub issues: https://guides.github.com/features/issues/
.. _existing issues: https://github.com/blueschu/troop89medfield.org/issues
.. _new issue: https://github.com/blueschu/troop89medfield.org/issues/new

Requesting a Feature
--------------------

Enhancements requests are also tracked with `GitHub issues`_. As with bug reports, please provide a clear and descriptive title that identifies the request. Be sure to explain the desired behavior of the new feature and how it would benefit the Troop 89 website.

Making a Pull Request
---------------------

Contributions to the Troop 89 website should be submitted as a `pull request`_ on GitHub. The basic workflow for contributing a change is as follows.

1. `Fork`_ the `Troop 89 Website repository`_.
2. `Clone`_ the fork repository to your machine.
3. Commit changes to a new feature branch.
4. `Push`_ your changes to the fork repository.
5. `Submit a pull request`_ to merge your work into the Troop 89 website.

.. _pull request: https://help.github.com/en/articles/about-pull-requests
.. _Fork: https://help.github.com/en/articles/fork-a-repo
.. _Troop 89 Website repository:
.. _Clone: https://help.github.com/en/articles/cloning-a-repository
.. _Push: https://help.github.com/en/articles/pushing-to-a-remote
.. _Submit a pull request: https://help.github.com/en/articles/creating-a-pull-request-from-a-fork

This repository uses branching conventions that are adapted from `A successful Git branching model`_:

- New features branches should be named ``feature/your-feature-description`` and should be based off of the ``development`` branch
- "Hot fixes" should be named ``hotfix/v{SEMVER}`` where ``{SEMVER}`` is the `semantic version`_ of the latest release with the patch version incremented. Hotfix branches should be based off of the ``master`` branch.

Commit messages should adhere to `these general guidelines`_.

All Python code should adhere to the `standard style guide for Python code (PEP 8)`_.

.. _semantic version: https://semver.org/
.. _standard style guide for Python code (PEP 8): https://www.python.org/dev/peps/pep-0008/
.. _A successful Git branching model: https://nvie.com/posts/a-successful-git-branching-model/
.. _these general guidelines: https://chris.beams.io/posts/git-commit/
