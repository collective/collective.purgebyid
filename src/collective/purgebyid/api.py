from plone.uuid.interfaces import IUUID
# from Acquisition import aq_base


def markInvolvedObjs(request, objs):
    if objs:
        for obj in objs:
            # aq_base ?
            uuid = IUUID(obj)
            if uuid:
                markInvolved(request, uuid)


def markInvolved(request, id):
    involved = getattr(request, 'involved', set())
    involved.add(id)
    request.involved = involved
