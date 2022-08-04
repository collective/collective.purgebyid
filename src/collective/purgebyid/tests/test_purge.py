# -*- coding: utf-8 -*-
from collective.purgebyid.api import mark_involved
from collective.purgebyid.api import mark_involved_objects
from collective.purgebyid.interfaces import IInvolvedID
from collective.purgebyid.purge import UuidPurgePath
from collective.purgebyid.testing import COLLECTIVE_PURGEBYID_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing.z2 import Browser
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.component import getGlobalSiteManager
from zope.component import provideAdapter
from zope.globalrequest import setRequest
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IHTTPRequest

import transaction
import unittest


class MarkerInterface(Interface):
    """A marker interface"""


class TestContentPurge(unittest.TestCase):

    layer = COLLECTIVE_PURGEBYID_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        setRequest(self.portal.REQUEST)
        setRoles(self.portal, TEST_USER_ID, ("Manager",))

    def test_header_published(self):
        """Test if the headers are published."""
        setRoles(self.portal, TEST_USER_ID, ("Manager",))
        document = api.content.create(
            title="Document", id="document", type="Document", container=self.portal
        )
        api.content.transition(document, to_state="published")
        transaction.commit()
        browser = Browser(self.app)
        browser.open(document.absolute_url())
        self.assertTrue("X-Ids-Involved" in browser.headers)
        ids = browser.headers["X-Ids-Involved"].strip("#").split("#")
        self.assertIn(IUUID(document), ids)

    def test_involved_adapter(self):
        """Test if the headers are published."""
        setRoles(self.portal, TEST_USER_ID, ("Manager",))
        document = api.content.create(
            title="Document", id="document", type="Document", container=self.portal
        )
        api.content.transition(document, to_state="published")
        alsoProvides(document, MarkerInterface)
        transaction.commit()

        # prepare a dummy adapter
        @adapter(MarkerInterface)
        @implementer(IInvolvedID)
        def document_adapter(obj):
            uuid = IUUID(obj)
            return [uuid, "custom-tag-from-adapter"]

        provideAdapter(document_adapter)

        browser = Browser(self.app)
        browser.open(document.absolute_url())
        self.assertTrue("X-Ids-Involved" in browser.headers)
        ids = browser.headers["X-Ids-Involved"].strip("#").split("#")
        self.assertIn(IUUID(document), ids)
        self.assertIn("custom-tag-from-adapter", ids)

        # cleanup
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(
            factory=document_adapter,
            provided=IInvolvedID,
        )

    def test_resource(self):
        browser = Browser(self.app)
        browser.open(self.portal.absolute_url() + "/favicon.ico")
        self.assertFalse("X-Ids-Involved" in browser.headers)

    def test_purge_content(self):
        document = api.content.create(
            title="Document", id="document", type="Document", container=self.portal
        )
        # notify(ObjectCreatedEvent(context))
        purger = UuidPurgePath(document)
        self.assertTrue(
            "/@@purgebyid/{}".format(IUUID(document)) in list(purger.getAbsolutePaths())
        )
        self.assertEqual([], list(purger.getRelativePaths()))


class TestHelperView(unittest.TestCase):

    layer = COLLECTIVE_PURGEBYID_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        setRequest(self.portal.REQUEST)
        setRoles(self.portal, TEST_USER_ID, ("Manager",))
        self.document = api.content.create(
            title="Document", id="document", type="Document", container=self.portal
        )
        api.content.transition(self.document, to_state="published")
        # create a bunch of auxiliary objects
        self.auxiliary_document = api.content.create(
            title="Auxiliary document",
            id="auxiliary-document",
            type="Document",
            container=self.portal,
        )
        api.content.transition(self.auxiliary_document, to_state="published")
        self.auxiliary_document2 = api.content.create(
            title="Auxiliary document",
            id="auxiliary-document2",
            type="Document",
            container=self.portal,
        )
        api.content.transition(self.auxiliary_document2, to_state="published")
        transaction.commit()

    def test_helper_view_pt(self):
        # prepare a specialized view
        @adapter(Interface, IHTTPRequest)
        class CustomDocumentView(BrowserView):
            index = ViewPageTemplateFile("document_with_dependencies.pt")

            def __call__(self):
                self.auxiliary_document = self.context.aq_parent["auxiliary-document"]
                self.auxiliary_document2 = self.context.aq_parent["auxiliary-document2"]
                mark_involved_objects(
                    self.request,
                    [
                        self.auxiliary_document,
                    ],
                )
                mark_involved(self.request, "custom-tag-from-view")
                return self.index()

        # register the view
        provideAdapter(
            CustomDocumentView,
            adapts=(Interface, IHTTPRequest),
            provides=IBrowserView,
            name="special-view",
        )
        browser = Browser(self.app)
        browser.open(self.document.absolute_url() + "/@@special-view")

        self.assertTrue("X-Ids-Involved" in browser.headers)
        ids = browser.headers["X-Ids-Involved"].strip("#").split("#")
        self.assertIn(IUUID(self.document), ids)
        self.assertIn(IUUID(self.auxiliary_document), ids)
        # auxiliary_document2 is marked in the template
        self.assertIn(IUUID(self.auxiliary_document2), ids)
        self.assertIn("custom-tag-from-view", ids)
        self.assertIn("custom-tag-from-template", ids)

        # cleanup
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(
            factory=CustomDocumentView,
            provided=IBrowserView,
        )

    def test_helper_view_catalog(self):
        # prepare a specialized view
        @adapter(Interface, IHTTPRequest)
        class CustomDocumentView(BrowserView):
            def __call__(self):
                mark_involved_objects(
                    self.request, api.content.find(portal_type="Document")
                )
                return "OK"

        # register the view
        provideAdapter(
            CustomDocumentView,
            adapts=(Interface, IHTTPRequest),
            provides=IBrowserView,
            name="special-view",
        )
        browser = Browser(self.app)
        browser.open(self.document.absolute_url() + "/@@special-view")

        self.assertTrue("X-Ids-Involved" in browser.headers)
        ids = browser.headers["X-Ids-Involved"].strip("#").split("#")
        self.assertIn(IUUID(self.document), ids)
        self.assertIn(IUUID(self.auxiliary_document), ids)
        self.assertIn(IUUID(self.auxiliary_document2), ids)

        # cleanup
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(
            factory=CustomDocumentView,
            provided=IBrowserView,
        )
