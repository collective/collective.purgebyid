# -*- coding: utf-8 -*-
import logging

from Acquisition import aq_base
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations

KEY = 'collective.purgebyid.involved'
logger = logging.getLogger('collective.purgebyid')


def getInvolvedObjs(request):
    annotations = IAnnotations(request)
    return annotations.get(KEY, None)


def markInvolvedObjs(request, objs, stoponfirst=False):
    """
    Mark the request for involved ids, objs is a list of object that must be:
        * the object is a string
        * the object has a UID attribute that is a string (e.g. a catalog
          brain, AT object, ...
        * the object implements IUUID
    In other cases the object will be ignored.

    If ``stoponfirst`` is True only the first object that respond to below
    rules will be marked as involved.
    """
    if objs:
        for obj in objs:
            uuid = None
            if isinstance(obj, str):
                uuid = obj
            else:
                # obj = getattr(obj, 'aq_base', obj)
                obj = aq_base(obj)
                if hasattr(obj, 'UID'):
                    uuid = getattr(obj, 'UID')
                    if callable(uuid):
                        uuid = uuid()
                    if not isinstance(uuid, str):
                        uuid = None
                if not uuid:
                    uuid = IUUID(obj, None)
            if uuid:
                markInvolved(request, uuid)
                if stoponfirst:
                    break


def markInvolved(request, id):
    logger.debug('mark request %r with %s' % (request, id))
    annotations = IAnnotations(request)
    if annotations.get(KEY, None):
        annotations[KEY].add(id)
    else:
        annotations[KEY] = set([id])
