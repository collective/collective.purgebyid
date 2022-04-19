# -*- coding: utf-8 -*-
import hashlib
import pkg_resources

from Acquisition import aq_base
from collective.purgebyid.api import NOID
from collective.purgebyid.interfaces import IInvolvedID
from plone.resource.interfaces import IResourceDirectory
from plone.uuid.interfaces import IUUID
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

try:
    pkg_resources.get_distribution('Products.ResourceRegistries')
    from Products.ResourceRegistries.interfaces import IResourceRegistry  # pragma: nocover
except pkg_resources.DistributionNotFound:
    HAS_RESOURCEREGISTRY = False
else:
    HAS_RESOURCEREGISTRY = True  # pragma: nocover


@adapter(Interface)
@implementer(IInvolvedID)
def contentAdapter(obj):
    """return uid for context.

    * the object is a string
    * the object has a UID attribute that is a string (e.g. a catalog
      brain, AT object, ...
    * the object implements IUUID
    """
    uuid = None
    if isinstance(obj, str):
        return obj
    obj = aq_base(obj)
    if hasattr(obj, 'UID'):
        uuid = getattr(obj, 'UID')
        if callable(uuid):
            uuid = uuid()
        if not isinstance(uuid, str):
            uuid = None
    if not uuid:
        uuid = IUUID(obj, None)
    return uuid


@adapter(IResourceDirectory)
@implementer(IInvolvedID)
def resourceDirectoryAdapter(context):
    if hasattr(context, 'directory'):
        # file system resources
        return hashlib.sha1(context.directory.encode('utf-8')).hexdigest()  # nosec
    else:
        # ZODB persistent resources
        return NOID


if HAS_RESOURCEREGISTRY:
    @adapter(IResourceRegistry)
    @implementer(IInvolvedID)
    def resourceRegistryAdapter(context):
        """portal_javascript, portal_css, ..."""
        return NOID
