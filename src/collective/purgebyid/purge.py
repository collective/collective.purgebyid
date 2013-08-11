from zope.interface import implements
from zope.component import adapts
from plone.uuid.interfaces import IUUIDAware
from z3c.caching.interfaces import IPurgePaths
from plone.uuid.interfaces import IUUID


class UuidPurgePath(object):
    implements(IPurgePaths)
    adapts(IUUIDAware)

    def __init__(self, context):
        self.context = context

    def getRelativePaths(self):
        return []

    def getAbsolutePaths(self):
        uuid = IUUID(self.context)
        if uuid:
            yield '/@@purgebyid/%s' % uuid
