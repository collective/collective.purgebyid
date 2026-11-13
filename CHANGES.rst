Changelog
=========

2.1.0 (unreleased)
------------------

- Cap the ``X-Ids-Involved`` header at 4096 bytes by default, so that large
  listings no longer produce headers that Varnish, Apache or nginx reject.
  Ids that do not fit are dropped and a warning is logged. The limit can be
  changed with the ``COLLECTIVE_PURGEBYID_MAX_HEADER_LENGTH`` environment
  variable (``0`` disables it). Ids in the header are now sorted, so its
  value is stable across requests.
  [mamico]

- Validate involved ids: only letters, digits, ``.``, ``_`` and ``-`` are
  accepted. Other ids (whitespace, ``#``, CR/LF, regular expression
  metacharacters, non-strings) are logged and ignored, because they would
  break the header format, the Varnish ``ban()`` expression or the HTTP
  header itself.
  [mamico]

- Remove dead code: the ``IResourceRegistry`` adapter (its ZCML condition
  named a non-existent ``Products.ResourceRegistry`` package) and the site
  root adapter for Plone < 6.
  [mamico]


2.0.0 (2026-11-13)
------------------

- Tests: migrate from the deprecated ``plone.testing.z2`` API to
  ``plone.testing.zope`` (``installProduct``, ``WSGI_SERVER_FIXTURE``, ``Browser``).
  [mamico]

- Plone < 6.0 and Python 2.7 are no longer supported by 2.x: they remain
  maintained on the ``1.x`` branch (1.2.x releases).
  [mamico]

- Configure the package with plone.meta 2.11.1 (tox.ini, pre-commit, GHA workflows).
  Backwards incompatible: this drops support for Plone < 6.0 and Python < 3.9
  (previously tested down to Plone 4.3 and Python 2.7/3.7/3.8). Supported
  versions are now Plone 6.0, 6.1, 6.2, 6.3 on Python 3.9 to 3.14.
  [mamico]

- Switch the ``collective`` namespace to a native PEP 420 namespace package,
  fixing a ``ConfigurationError`` on ``collective.monkeypatcher`` under
  recent setuptools/Python versions.
  [mamico]

- Declare all runtime and test dependencies actually imported by the
  package (``Zope``, ``Products.CMFCore``, ``plone.resource``,
  ``plone.transformchain``, ``z3c.caching``, ``plone.testing``), drop
  unused ones (``setuptools``, ``six``).
  [mamico]

- Remove CI/config leftovers made obsolete by the plone.meta migration:
  the pre-plone.meta GitHub Actions test workflow, the Bandit workflow
  (broken, unmaintained Docker image), and the legacy buildout
  configuration/requirements files.
  [mamico]

1.2.3 (2024-12-12)
------------------

- Do not register IInvolvedID adapter for ISiteRoot on Plone6 because now it is a content with UID.
  [cekk]


1.2.2 (2024-02-29)
------------------

- plone 6.0 / python 3.11, 3.12 support
  [mamico]

1.2.1 (2022-12-08)
------------------

- plone 6.0 / python 3.10 support
  [mamico]

- avoid marking requests with the UUID of the plonesite
  [mamico]

1.2.0 (2022-08-04)
------------------

- collective.xkey backports. Add utility browser view.
  [pgrunewald, mamico]

- fix p.a.multilingual IUUID adapter inconsistency
  [mamico]

1.1.2 (2021-11-22)
------------------

- Remove unused importDependencies (for pip install compatibility).
  [cekk]

1.1.1 (2019-06-05)
------------------

- Python 3 support 
  [mamico]


1.1.0 (2018-05-14)
------------------

- moved headers mutator from PubSuccess event to plone.transformchain.
  fix missing header using p.a.caching's ramcache operations #2
  [mamico]
- added IIDinvolved adapter for easy implements "involved id" extractors
  [mamico]
- manage resourcedirectory, because previously all resources were marked as "involved" by
  navigation root
  [mamico]
- fix issue where IUUID-adaptation did not have default value
  [datakurre]


1.0.0 (2016-01-14)
------------------

- use zope.annotation on request
  [mamico]
- unused generic setup profile removed
  [mamico]

1.0.0a1 (2013-09-11)
--------------------

- Package created using templer
  [Mauro Amico]
