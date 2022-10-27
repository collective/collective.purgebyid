# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.purgebyid.interfaces import IInvolvedID
import hashlib
import pkg_resources
from plone.resource.interfaces import IResourceDirectory
from plone.uuid.interfaces import IUUID
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

try:
    pkg_resources.get_distribution("Products.ResourceRegistries")
    from Products.ResourceRegistries.interfaces import IResourceRegistry  # pragma: nocover
except pkg_resources.DistributionNotFound:
    HAS_RESOURCEREGISTRY = False
else:
    HAS_RESOURCEREGISTRY = True  # pragma: nocover


@adapter(Interface)
@implementer(IInvolvedID)
def content_adapter(obj):
    """return [uid] for context.

    * the object is a string
    * the object implements IUUID
    * the object has a UID attribute that is a string (e.g. a catalog
      brain, AT object, ...
    """
    uuid = None
    if isinstance(obj, str):
        return [obj]
    obj = aq_base(obj)
    uuid = IUUID(obj, None)
    if uuid is None:
        if hasattr(obj, "UID"):
            uuid = getattr(obj, "UID")
            if callable(uuid):
                uuid = uuid()
            if not isinstance(uuid, str):
                uuid = None
    return [uuid] if uuid else []


@adapter(IResourceDirectory)
@implementer(IInvolvedID)
def resource_directory_adapter(context):
    if hasattr(context, "directory"):
        # file system resources
        return [hashlib.sha1(context.directory.encode("utf-8")).hexdigest()]  # nosec
    else:
        # ZODB persistent resources
        return []


@adapter(ISiteRoot)
@implementer(IInvolvedID)
def site_root_adapter(context):
    return []


if HAS_RESOURCEREGISTRY:

    @adapter(IResourceRegistry)
    @implementer(IInvolvedID)
    def resource_registry_adapter(context):
        """portal_javascript, portal_css, ..."""
        return []
