collective.purgebyid
====================

.. image:: https://img.shields.io/pypi/v/collective.purgebyid.svg
    :target: https://pypi.python.org/pypi/collective.purgebyid/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/collective.purgebyid.svg?style=plastic   
     :alt: Supported - Python Versions

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
X-Ids-Involved, which contains thee uuids of the objects involved in the
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

Varnish
-------

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


References
----------

* Blog post http://www.biodec.com/it/blog/migliorare-la-gestione-del-purge-caching-in-plone-collective-purgebyid (italian language) 
