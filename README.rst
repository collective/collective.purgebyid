collective.purgebyid
====================

.. image:: https://img.shields.io/pypi/v/collective.purgebyid.svg
    :target: https://pypi.python.org/pypi/collective.purgebyid/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/collective.purgebyid.svg?style=plastic
    :target: https://pypi.python.org/pypi/collective.purgebyid/
    :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/dm/collective.purgebyid.svg
    :target: https://pypi.python.org/pypi/collective.purgebyid/
    :alt: Number of PyPI downloads
    
.. image:: https://img.shields.io/pypi/l/collective.purgebyid.svg
    :target: https://pypi.python.org/pypi/collective.purgebyid/
    :alt: License

.. image:: https://github.com/collective/collective.purgebyid/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/collective/collective.purgebyid/actions
    :alt: Tests

.. image:: https://coveralls.io/repos/github/collective/collective.purgebyid/badge.svg?branch=master
    :target: https://coveralls.io/github/collective/collective.purgebyid?branch=master
    :alt: Coverage

collective.purgbyid is a new method for cache invalidation of Plone
based web sites. It uses the idea of adding an extra header, called
X-Ids-Involved, which contains the uuids of the objects involved in the
construction of the resources. For example, an image contains just its
uuid::

    % wget -S http://localhost:8080/Plone/image01
    ...
      X-Ids-Involved: #c8d7c0bc2b794325b916d990de91d7ee#

Other pages may be more complicated. Then a new purge rewrite rule adds
a custom URL to the set of URLs to purge: the "purge by id" custom URL
is in the form /@@purgebyid/<UUID> where UUID is the object's uuid to be
purged.

Last, Varnish is configured so that, when an URL /@@purgebyid/<UUID> is
purged, it will ban all the objects that match an X-Ids-Involved header
of the right type (i.e. containing the uuid of the resource to purge).
This means that when a resources is purged, it is enough to purge also
it /@@purgebyid/<UUID> URL because it will be Varnish responsibily to
also catch all of the occurrencies of the resources whenever the URL
which is used to access it.

Varnish without xkey varnish module
-----------------------------------

Without the xkey module, the way to purge a resource is to ban all objects
which have the X-Ids-Involved header with the id of the resource to be purged.

For a better understanding of the differences between the two approaches (ban vs. purge), please read:
https://varnish-cache.org/docs/trunk/users-guide/purging.html

Config example::

    sub vcl_recv {
      if (req.method == "PURGE") {
         if (!client.ip ~ purge) {
            return (synth(405, "This IP is not allowed to send PURGE requests."));
         }
         if (req.url ~ "^/@@purgebyid/") {
            ban("obj.http.x-ids-involved ~ #" + regsub(req.url, "^/@@purgebyid/", "") + "#");
            return(synth(200, "Ban added"));
        }
        return(purge);
      }
    }

    sub vcl_deliver {
        unset resp.http.x-ids-involved;
    }


Varnish with xkey varnish module
--------------------------------

By default, Varnish uses the URL as the hash key for purging, but with
the xkey module (https://github.com/varnish/varnish-modules/blob/master/src/vmod_xkey.vcc)
there comes a secondary hash for doing so. Cached objects
being tagged can be specifically purged for a more targeted cache control.

To have xkey working, it is mandatory to provide a special HTTP header called
"Xkey" which contains all the tags (separated by white-space). Few additional codes in
the `vcl_backend_response` transforms the X-Ids-Involved header into an XKey.

Config example::

    import xkey;

    sub vcl_recv {
        if (req.method == "PURGE") {
            if (!client.ip ~ purge) {
                return (synth(405, "This IP is not allowed to send PURGE requests."));
            }
            if (req.url ~ "^/@@purgebyid/") {
                set req.http.n-gone = xkey.purge(regsub(req.url, "^/@@purgebyid/", ""));
                # or: set req.http.n-gone = xkey.softpurge(regsub(req.url, "^/@@purgebyid/", ""));
                return (synth(200, "Invalidated "+req.http.n-gone+" objects"));
            }
        }
        return(purge);
    }

    sub vcl_backend_response {
        if (beresp.http.x-ids-involved) {
            set beresp.http.xkey = regsuball(beresp.http.x-ids-involved, "#", " ");
        }
    }

    sub vcl_deliver {
        unset resp.http.x-ids-involved;
        unset resp.http.xkey;
    }


A softpurge differs from a regular purge in that it resets an
object's TTL but keeps it available for grace mode and conditional
requests for the remainder of its configured grace and keep time.

How does it work? How to extend it?
-----------------------------------

During the publishing process all involved IDs (UUIDs and custom IDs) are collected
(by subscribing to IPubAfterTraversal).

Important are the adapters for IInvolvedID, which are responsible for collecting IDs for their given context.
The base implementation looks for the UUIDs, but may be specialized for your custom content types.

Apart from the adapter approach, there is the inline approach. You may call the following methods
from collective.purgebyid.api:

* mark_involved_objects(request, objs, stoponfirst=False)
* mark_involved(request, single_id)

Whereas the first method uses internally the adapters for IInvolvedIDs for the given objects,
the second one allows setting any arbitrary IDs.
These methods combined might be used in your views, whenever a certain object or part is being rendered.

Additionally, there is a utility browser view "purgebyid", that can be used in your template as follows:

.. code-block:: xml

    <body tal:define="purgeutils nocall:context/@@purgebyid">
    ...
        <tal:image tal:define="image python:context.get_image()" tal:condition="python: image">

            <tal:mark-involved tal:define="dummy python:purgeutils.mark(image)" />
            <!-- put image rendering here -->
            ...

        </tal:image>
    ...
    </body>

Alternatively, you can again set arbitrary IDs:

.. code-block:: xml

    <tal:mark-involved tal:define="dummy python:purgeutils.mark('my_custom_id')" />

After having collected all IDs a ITransform adapter puts the expected `X-Ids-Involved` header in
the HTTP response header.

When Plone sends a purge request to the configured Cache Proxy, it sends additionally a specialized
request for handling objects with tags.


References
----------

* Blog post https://www.biodec.com/it/blog/migliorare-la-gestione-del-purge-caching-in-plone-collective-purgebyid (italian language)
