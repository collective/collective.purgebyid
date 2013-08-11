from plone.uuid.interfaces import IUUID


def markInvolvedObjs(request, objs):
    if objs:
        for obj in objs:
            uuid = IUUID(obj, None)
            if uuid:
                markInvolved(request, uuid)


def markInvolved(request, id):
    involved = getattr(request, 'involved', set())
    involved.add(id)
    request.involved = involved
