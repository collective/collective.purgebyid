import logging
from plone.uuid.interfaces import IUUID
from Acquisition import aq_base


logger = logging.getLogger('collective.purgebyid')


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
    if not hasattr(request, 'involved'):
        request.involved = set()
    logger.debug('mark request %r with %s' % (request, id))
    request.involved.add(id)
