.. This Source Code Form is subject to the terms of the Mozilla Public
.. License, v. 2.0. If a copy of the MPL was not distributed with this
.. file, You can obtain one at http://mozilla.org/MPL/2.0/.

How to Maintain the Troop 89 Website
====================================

This document outlines how to maintain the Troop 89 website without any coding or web design experience. If you are interested in contributing to the website's source code, please see :doc:`contributing`.


Accessing the Admin site
------------------------

Link: `The Troop 89 admin site`_.

Most management of the Troop 89 website can be accomplished within the customized `admin site`_. If you are already logged in to the Troop 89 and have been granted access to the admin site, you should be able to access it by the link listed above. If you unable to reach the admin site and beleive that you should have access, contact a webmaster.

.. _The Troop 89 admin site: https://www.troop89medfield.org/admin/
.. _admin site: https://www.troop89medfield.org/admin/

.. _Django admin: https://docs.djangoproject.com/en/2.2/ref/contrib/admin/

Posting Announcements
---------------------

From the admin site, navigate to Troop Announcement | Announcements | Add Announcement.

In the announcement creation form, provide a title, a date of publication, and some content for the announcement. Currently, announcements can be written in either plain text or `Markdown`_. For a brief tutorial on how to stylize writing with Markdown, see GitHub's `Mastering Markdown`_ guide. In the future, a rich WYSIWYG editor may be provided for announcement creation, such as the one available for flatpage creation.

.. admonition:: Advanced

    At the bottom of the announcement creation form, you will find a collapsed fieldset title "Advanced". Expanding this fieldset will give you access to two additional fields: the user, and the slug.

    The user field determines the person who is *displayed* as the author of a post. Note that this is separated from the system that records actions in the admin interface: the users responsible for creating and editing an announcement will be visible in the changelog.

    The slug field determine the url that the announcement can be accessed with. By default, this field is generated from the the announcement's title, but you may wish to edit it in some circumstances to create a more expressive url.

After saving your announcement, you can view it on the live site by either navigating to the `homepage`_ or clicking the "View on Site" buttom in editing form.

.. _Markdown: https://daringfireball.net/projects/markdown/
.. _Mastering Markdown: https://guides.github.com/features/mastering-markdown/
.. _homepage: https://www.troop89medfield.org/


Creating events
---------------

From the admin site, navigate to the Events | Events | Add Event.

In the announcement creation form, provide a title, type, description, and start and end time for the event. Currently, event descriptions can be written in either plain text or `Markdown`_. For a brief tutorial on how to stylize writing with Markdown, see GitHub's `Mastering Markdown`_ guide. In the future, a rich WYSIWYG editor may be provided for announcement creation, such as the one available for flatpage creation.

.. admonition:: Advanced

    At the bottom of the event creation form, you will find a collapsed fieldset title "Advanced". Expanding this fieldset will give you access to one additional fields: the slug.

    The slug field determine the url that the event can be accessed with. By default, this field is generated from the the event's title, but you may wish to edit it in some circumstances to create a more expressive url.


Creating and editing static pages
---------------------------------

The management of static or "flat" pages is handled by our custom flatpage app.

Navigate to the Flat page listing in the admin to view the page currently available on the site. From there, you may search for a page by title in the search box, filter what pages are shown by their parent page, or sort the pages by url or title.

To create a new flat page, click the "Add Flat Page" button in the top right corner of the page. In the flat page creation form, provide a URL, title, and rich body for the new page.

Take particular care when picking the URL for the new page. The URL that you provide will be used to determine where your new page should be displayed on the site. For example, a page with the URL ``/about/squirrels`` will be listed as a subpage on the ``/about/`` page and will visible as a related page on the ``/about/chipmunks`` page.


.. admonition:: Advanced

    At the bottom of the flat page creation form, you will find a collapsed fieldset title "Advanced options". Expanding this fieldset will give you access to two additional fields: a "registration required" checkbox, and a template name.

    If selected, the "registration required" flag will restrict access to the flat page to users who are logged in to the website with a Troop 89 account. The page will not be listed for users who are not logged in to the site.

    The "template name" field specifies the Django template from source control to use to render the page. This field defaults to ``flatpages/default.html``. You should only edit this field if you need to heavily customize the rendering of your flatpage, such as loading a custom template tags or querying additional data from the database.

Updating the newsletter archive
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The newsletter archive can be edited in the same way as any other flat page. The view all of the current newsletter archive, navigate to the Flat page app in the admin and select ``/records/newsletters/`` under the parent page filter.

To update the archive, first upload the most recent newsletter and its supplementary document to the Troop 89 Google Drive. You may direct any questions regarding the upload process to a webmaster or past troop historian.

Once you have uploaded the relevant files, create a section in the newsletter year archive in the following format:

    {MONTH} Newsletter & Trip Information

    {MONTH} {YEAR} Newsletter

    {MONTH} {YEAR} Dates

    Supplementary Documents

    * Document-1
    * Document-2
    * ...

For each document listed above, highlight the document's name and then type ``CTRL+K`` to insert a link. In the window that pops up, enter the public URL for the document that you uploaded the the Google Drive. This can be found by right-clicking on the document in the Drive folder, clicking "Share", and the copying the shareable link shown.

