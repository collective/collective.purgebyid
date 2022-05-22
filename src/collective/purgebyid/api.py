# -*- coding: utf-8 -*-
from collective.purgebyid.interfaces import IInvolvedID
from collective.purgebyid import logger
from past.builtins import basestring
from zope.annotation.interfaces import IAnnotations


KEY = "collective.purgebyid.involved"
NOID = object()


def getInvolvedObjs(request):
    annotations = IAnnotations(request)
    return annotations.get(KEY, None)


def mark_involved_objects(request, objs, stoponfirst=False):
    """Retrieve the involved ids by the given objects. Objects might be
    ordinary strings, Plone content objects having UID attributes, IUUID.

    :param request: request
    :param objs: list
    :type objs: object (string or object that implements IInvolvedID)
    :param stoponfirst: True only the first object that respond to below rules will be marked as involved.
    :type stoponfirst: bool, optional
    """
    for obj in objs:
        if isinstance(obj, basestring):
            ids = [obj]
        else:
            ids = IInvolvedID(obj, None)
        if ids:
            if ids is NOID:  # pragma: nocover
                logger.warning(
                    "deprecated: the IInvolvedID adapter must return a list of ids"
                )
                ids = []
            if isinstance(ids, basestring):  # pragma: nocover
                logger.warning(
                    "deprecated: the IInvolvedID adapter must return a list of ids"
                )
                ids = [ids]
            for id in ids:
                mark_involved(request, id)
            if stoponfirst:
                break


def mark_involved(request, id):
    """Mark an id as being involved for this request.

    :param request: request
    :param single_id: single involved id
    :type single_id: basestring
    """
    logger.debug("mark request %r with %s", request, id)
    if id is NOID:  # pragma: nocover
        return
    annotations = IAnnotations(request)
    if annotations.get(KEY, None):
        annotations[KEY].add(id)
    else:
        annotations[KEY] = set([id])


# BBB: renamed api
markInvolvedObjs = mark_involved_objects
markInvolved = mark_involved
