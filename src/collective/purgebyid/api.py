# -*- coding: utf-8 -*-
import logging

from collective.purgebyid.interfaces import IInvolvedID
from zope.annotation.interfaces import IAnnotations

KEY = 'collective.purgebyid.involved'
NOID = object()
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
            ids = IInvolvedID(obj, None)
            if ids:
                if isinstance(ids, basestring) or ids is NOID:
                    ids = [ids]
                for id in ids:
                    markInvolved(request, id)
                if stoponfirst:
                    break


def markInvolved(request, id):
    logger.debug('mark request %r with %s' % (request, id))
    if id is not NOID:
        annotations = IAnnotations(request)
        if annotations.get(KEY, None):
            annotations[KEY].add(id)
        else:
            annotations[KEY] = set([id])
