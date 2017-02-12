# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.purgebyid.api import NOID
from collective.purgebyid.interfaces import IInvolvedID
import hashlib
from plone.resource.interfaces import IResourceDirectory
from plone.uuid.interfaces import IUUID
from Products.ResourceRegistries.interfaces import IResourceRegistry
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


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
        return hashlib.sha1(context.directory).hexdigest()
    else:
        # ZODB persistent resources
        return NOID


@adapter(IResourceRegistry)
@implementer(IInvolvedID)
def resourceRegistryAdapter(context):
    """portal_javascript, portal_css, ..."""
    return NOID
