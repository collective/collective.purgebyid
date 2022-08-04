Changelog
=========

1.2.0 (unreleased)
------------------

- collectice.xkey backports. Add utility browser view.
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
