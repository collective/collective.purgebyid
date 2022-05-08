# -*- coding: utf-8 -*-
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from z3c.caching.interfaces import IPurgePaths
from zope.component import adapter
from zope.interface import implementer


@implementer(IPurgePaths)
@adapter(IUUIDAware)
class UuidPurgePath(object):
    def __init__(self, context):
        self.context = context

    def getRelativePaths(self):
        return []

    def getAbsolutePaths(self):
        uuid = IUUID(self.context, None)
        if uuid:
            yield "/@@purgebyid/%s" % uuid
