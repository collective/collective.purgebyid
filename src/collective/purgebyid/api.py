from collective.purgebyid import logger
from collective.purgebyid.interfaces import IInvolvedID
from zope.annotation.interfaces import IAnnotations

import re

KEY = "collective.purgebyid.involved"
NOID = object()

# Characters allowed in an involved id. Anything else could break the
# X-Ids-Involved header format ("#" separator, whitespace for xkey), the
# regular expression used by Varnish ``ban()``, or the HTTP header itself
# (CR/LF).
VALID_ID = re.compile(r"[A-Za-z0-9._-]+")


def is_valid_id(id):
    """Return True if ``id`` can be safely used as an involved id."""
    return isinstance(id, str) and VALID_ID.fullmatch(id) is not None


def get_involved_objects(request):
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
        if isinstance(obj, str):
            ids = [obj]
        else:
            ids = IInvolvedID(obj, None)
        if ids:
            if ids is NOID:  # pragma: nocover
                logger.warning(
                    "deprecated: the IInvolvedID adapter must return a list of ids"
                )
                ids = []
            if isinstance(ids, str):  # pragma: nocover
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

    Ids must match ``VALID_ID`` (letters, digits, ``.``, ``_``, ``-``);
    invalid ids are logged and ignored.

    :param request: request
    :param id: single involved id
    :type id: str
    """
    logger.debug("mark request %r with %s", request, id)
    if id is NOID:  # pragma: nocover
        return
    if not is_valid_id(id):
        logger.warning("ignoring invalid involved id %r", id)
        return
    annotations = IAnnotations(request)
    if annotations.get(KEY, None):
        annotations[KEY].add(id)
    else:
        annotations[KEY] = {id}


# BBB: renamed api
getInvolvedObjs = get_involved_objects
markInvolvedObjs = mark_involved_objects
markInvolved = mark_involved
