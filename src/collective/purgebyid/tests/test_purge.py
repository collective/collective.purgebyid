from collective.purgebyid.api import get_involved_objects
from collective.purgebyid.api import KEY
from collective.purgebyid.api import mark_involved
from collective.purgebyid.api import mark_involved_objects
from collective.purgebyid.events import build_header
from collective.purgebyid.events import get_max_header_length
from collective.purgebyid.events import MAX_HEADER_LENGTH_ENV
from collective.purgebyid.events import MutatorTransform
from collective.purgebyid.interfaces import IInvolvedID
from collective.purgebyid.purge import UuidPurgePath
from collective.purgebyid.testing import COLLECTIVE_PURGEBYID_FUNCTIONAL_TESTING
from collective.purgebyid.testing import COLLECTIVE_PURGEBYID_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import Browser
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from unittest import mock
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getGlobalSiteManager
from zope.component import provideAdapter
from zope.globalrequest import setRequest
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IHTTPRequest

import os
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

    def test_header_published_on_site_root(self):
        """Test if the headers are published on site root too."""
        setRoles(self.portal, TEST_USER_ID, ("Manager",))
        browser = Browser(self.app)
        browser.open(self.portal.absolute_url())
        self.assertTrue("X-Ids-Involved" in browser.headers)
        ids = browser.headers["X-Ids-Involved"].strip("#").split("#")
        self.assertIn(IUUID(self.portal), ids)

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
        self.assertTrue("X-Ids-Involved" in browser.headers)

    def test_purge_content(self):
        document = api.content.create(
            title="Document", id="document", type="Document", container=self.portal
        )
        # notify(ObjectCreatedEvent(context))
        purger = UuidPurgePath(document)
        self.assertTrue(
            f"/@@purgebyid/{IUUID(document)}" in list(purger.getAbsolutePaths())
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


class TestInvolvedIdsValidation(unittest.TestCase):

    layer = COLLECTIVE_PURGEBYID_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        IAnnotations(self.request).pop(KEY, None)

    def test_valid_ids(self):
        mark_involved(self.request, "c8d7c0bc2b794325b916d990de91d7ee")
        mark_involved(self.request, "custom-tag_1.2")
        self.assertEqual(
            get_involved_objects(self.request),
            {"c8d7c0bc2b794325b916d990de91d7ee", "custom-tag_1.2"},
        )

    def test_invalid_ids_are_ignored(self):
        invalid = [
            "",
            "with space",
            "with#hash",
            "trailing-newline\n",
            "header\r\nX-Injected: 1",
            "regex+meta",
            "non-ascii-ü",
            None,
            42,
        ]
        with self.assertLogs("collective.purgebyid", level="WARNING") as logs:
            for id in invalid:
                mark_involved(self.request, id)
        self.assertEqual(len(logs.records), len(invalid))
        self.assertFalse(get_involved_objects(self.request))

    def test_mark_involved_objects_skips_invalid(self):
        with self.assertLogs("collective.purgebyid", level="WARNING"):
            mark_involved_objects(self.request, ["valid-id", "invalid id"])
        self.assertEqual(get_involved_objects(self.request), {"valid-id"})


class TestHeaderLength(unittest.TestCase):

    layer = COLLECTIVE_PURGEBYID_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        IAnnotations(self.request).pop(KEY, None)
        self.uuids = [f"{i:032x}" for i in range(500)]

    def test_build_header_is_sorted(self):
        self.assertEqual(build_header({"b", "c", "a"}), "#a#b#c#")

    def test_build_header_without_limit(self):
        self.assertEqual(len(build_header(self.uuids, 0)), 1 + 500 * 33)
        self.assertEqual(len(build_header(self.uuids, None)), 1 + 500 * 33)

    def test_build_header_with_limit(self):
        with self.assertLogs("collective.purgebyid", level="WARNING"):
            value = build_header(self.uuids, 4096)
        self.assertLessEqual(len(value), 4096)
        kept = value.strip("#").split("#")
        # "#" + n * (32 + len("#")) <= 4096
        self.assertEqual(len(kept), 124)
        self.assertEqual(kept, sorted(self.uuids)[:124])

    def test_build_header_nothing_fits(self):
        with self.assertLogs("collective.purgebyid", level="WARNING"):
            self.assertIsNone(build_header(["a" * 50], 10))

    def test_max_header_length_env(self):
        with mock.patch.dict(os.environ):
            os.environ.pop(MAX_HEADER_LENGTH_ENV, None)
            self.assertEqual(get_max_header_length(), 4096)
            os.environ[MAX_HEADER_LENGTH_ENV] = "100"
            self.assertEqual(get_max_header_length(), 100)
            os.environ[MAX_HEADER_LENGTH_ENV] = "0"
            self.assertEqual(get_max_header_length(), 0)
            os.environ[MAX_HEADER_LENGTH_ENV] = "not-a-number"
            with self.assertLogs("collective.purgebyid", level="WARNING"):
                self.assertEqual(get_max_header_length(), 4096)

    def test_mutator_caps_header(self):
        for uuid in self.uuids:
            mark_involved(self.request, uuid)
        with mock.patch.dict(os.environ, {MAX_HEADER_LENGTH_ENV: "1000"}):
            with self.assertLogs("collective.purgebyid", level="WARNING"):
                MutatorTransform(None, self.request).transformIterable([], "utf-8")
        value = self.request.response.getHeader("X-Ids-Involved")
        self.assertTrue(value.startswith("#"))
        self.assertLessEqual(len(value), 1000)

    def test_mutator_default_limit(self):
        for uuid in self.uuids:
            mark_involved(self.request, uuid)
        with mock.patch.dict(os.environ):
            os.environ.pop(MAX_HEADER_LENGTH_ENV, None)
            with self.assertLogs("collective.purgebyid", level="WARNING"):
                MutatorTransform(None, self.request).transformIterable([], "utf-8")
        value = self.request.response.getHeader("X-Ids-Involved")
        self.assertLessEqual(len(value), 4096)
