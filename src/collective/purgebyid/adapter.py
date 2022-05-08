# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.purgebyid.api import NOID
from collective.purgebyid.interfaces import IInvolvedID
from plone.resource.interfaces import IResourceDirectory
from plone.uuid.interfaces import IUUID
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import hashlib
import pkg_resources


try:
    pkg_resources.get_distribution("Products.ResourceRegistries")
    from Products.ResourceRegistries.interfaces import (
        IResourceRegistry,
    )  # pragma: nocover
except pkg_resources.DistributionNotFound:
    HAS_RESOURCEREGISTRY = False
else:
    HAS_RESOURCEREGISTRY = True  # pragma: nocover


@adapter(Interface)
@implementer(IInvolvedID)
def contentAdapter(obj):
    """return uid for context.

    * the object is a string
    * the object implements IUUID
    * the object has a UID attribute that is a string (e.g. a catalog
      brain, AT object, ...
    """
    uuid = None
    if isinstance(obj, str):
        return obj
    obj = aq_base(obj)
    uuid = IUUID(obj, None)
    if uuid is None:
        if hasattr(obj, "UID"):
            uuid = getattr(obj, "UID")
            if callable(uuid):
                uuid = uuid()
            if not isinstance(uuid, str):
                uuid = None
    return uuid


@adapter(IResourceDirectory)
@implementer(IInvolvedID)
def resourceDirectoryAdapter(context):
    if hasattr(context, "directory"):
        # file system resources
        return hashlib.sha1(context.directory.encode("utf-8")).hexdigest()  # nosec
    else:
        # ZODB persistent resources
        return NOID


if HAS_RESOURCEREGISTRY:

    @adapter(IResourceRegistry)
    @implementer(IInvolvedID)
    def resourceRegistryAdapter(context):
        """portal_javascript, portal_css, ..."""
        return NOID
