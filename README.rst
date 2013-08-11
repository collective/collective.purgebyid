.. contents::

Introduction
============

TODO.

Varnish
-------

Config example::

    sub vcl_recv {
        ...
        if (req.request == "PURGE") {
            if (!client.ip ~ purge) {
                error 405 "Not allowed.";
            }
            if (req.url ~ "^/@@purgebyid/") {
                ban("obj.http.x-ids-involved ~ #" + regsub(req.url, "^/@@purgebyid/", "") + "#");
                error 200 "Ban added";
            }
            ...
        }
        ...
    }
    ...
