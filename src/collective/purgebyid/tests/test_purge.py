# -*- coding: utf-8 -*-
import unittest

from Acquisition import Explicit, aq_base
from collective.purgebyid.purge import UuidPurgePath
from collective.purgebyid.testing import \
    COLLECTIVE_PURGEBYID_INTEGRATION_TESTING
from plone.transformchain.zpublisher import applyTransformOnSuccess
from plone.uuid.interfaces import IUUID, IAttributeUUID
from Products.CMFCore.interfaces import IContentish
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
# from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.lifecycleevent import ObjectCreatedEvent
from ZPublisher.pubevents import PubAfterTraversal


@implementer(IContentish)
class FauxNonContent(Explicit):

    def __init__(self, name=None):
        self.__name__ = name
        self.__parent__ = None  # may be overridden by acquisition

    def getId(self):
        return self.__name__

    def virtual_url_path(self):
        parent = aq_base(self.__parent__)
        if parent is not None:
            return parent.virtual_url_path() + '/' + self.__name__
        else:
            return self.__name__

    def getPhysicalPath(self):
        return ('', )

    def getParentNode(self):
        return FauxNonContent('folder')


@implementer(IAttributeUUID)
class FauxContent(FauxNonContent):
    portal_type = 'testtype'


class FauxResponse(object):
    def __init__(self, body='', headers={}):
        self._body = body
        self.headers = headers

    def getBody(self):
        return self._body

    def setBody(self, body):
        self._body = body

    def getHeader(self, name):
        return self.headers.get(name)

    def setHeader(self, name, value):
        self.headers[name] = value


@implementer(IAnnotations)
class FauxRequest(dict):

    def __init__(self, published, response=None):
        if response is None:
            response = FauxResponse('<html/>')

        self['PUBLISHED'] = published
        self['PARENTS'] = [published]
        self.response = response
        self.environ = {}


class FauxPubEvent(object):

    def __init__(self, request):
        self.request = request


class TestContentPurge(unittest.TestCase):

    layer = COLLECTIVE_PURGEBYID_INTEGRATION_TESTING

    def test_publish_content(self):
        context = FauxContent('foo')
        notify(ObjectCreatedEvent(context))
        request = FauxRequest(context)
        notify(PubAfterTraversal(request))
        applyTransformOnSuccess(FauxPubEvent(request))
        self.assertEqual('#{}#'.format(IUUID(context)),
                         request.response.getHeader('X-Ids-Involved'))

    def test_purge_content(self):
        context = FauxContent('foo')
        notify(ObjectCreatedEvent(context))
        purger = UuidPurgePath(context)
        list(purger.getAbsolutePaths())
        self.assertEqual(['/@@purgebyid/{}'.format(IUUID(context))],
                         list(purger.getAbsolutePaths()))
        self.assertEqual([], list(purger.getRelativePaths()))
