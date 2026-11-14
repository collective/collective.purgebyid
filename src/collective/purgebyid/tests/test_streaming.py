"""The X-Ids-Involved header must be sent on streamed responses too.

The header is set by a plone.transformchain transform, which runs on
IPubBeforeCommit. These tests check that it still reaches the client when
the response is streamed (``response.write()``, stream iterators, blob
downloads).
"""

from collective.purgebyid.api import mark_involved
from collective.purgebyid.testing import COLLECTIVE_PURGEBYID_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.testing.zope import Browser
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from zope.component import getGlobalSiteManager
from zope.component import provideAdapter
from zope.globalrequest import setRequest
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IHTTPRequest
from ZPublisher.Iterators import IUnboundStreamIterator

import transaction
import unittest


@implementer(IUnboundStreamIterator)
class UnboundIterator:
    def __init__(self, chunks):
        self.chunks = iter(chunks)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.chunks)


class WriteView(BrowserView):
    """Stream the body with response.write()."""

    def __call__(self):
        mark_involved(self.request, "streamed-with-write")
        response = self.request.response
        response.setHeader("Content-Type", "text/plain")
        for _ in range(10):
            response.write(b"x" * 1024)
        return ""


class UnboundIteratorView(BrowserView):
    """Return an IUnboundStreamIterator (no Content-Length)."""

    def __call__(self):
        mark_involved(self.request, "streamed-with-iterator")
        self.request.response.setHeader("Content-Type", "text/plain")
        return UnboundIterator([b"x" * 1024] * 10)


class TestStreamedResponses(unittest.TestCase):

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
        transaction.commit()
        self.browser = Browser(self.app)

    def _register_view(self, factory, name):
        provideAdapter(
            factory,
            adapts=(Interface, IHTTPRequest),
            provides=IBrowserView,
            name=name,
        )
        self.addCleanup(
            getGlobalSiteManager().unregisterAdapter,
            factory=factory,
            required=(Interface, IHTTPRequest),
            provided=IBrowserView,
            name=name,
        )

    def _ids(self):
        self.assertIn("X-Ids-Involved", self.browser.headers)
        return self.browser.headers["X-Ids-Involved"].strip("#").split("#")

    def test_response_write(self):
        self._register_view(WriteView, "stream-write")
        self.browser.open(self.document.absolute_url() + "/@@stream-write")
        self.assertEqual(len(self.browser.contents), 10 * 1024)
        ids = self._ids()
        self.assertIn("streamed-with-write", ids)
        self.assertIn(IUUID(self.document), ids)

    def test_unbound_stream_iterator(self):
        self._register_view(UnboundIteratorView, "stream-iterator")
        self.browser.open(self.document.absolute_url() + "/@@stream-iterator")
        self.assertEqual(len(self.browser.contents), 10 * 1024)
        ids = self._ids()
        self.assertIn("streamed-with-iterator", ids)
        self.assertIn(IUUID(self.document), ids)

    def test_blob_download(self):
        data = b"x" * (2 * 1024 * 1024)
        file = api.content.create(
            type="File",
            id="big-file",
            title="Big file",
            container=self.portal,
            file=NamedBlobFile(
                data=data, contentType="application/octet-stream", filename="big.bin"
            ),
        )
        # Files have no workflow in Plone 6: no transition needed.
        transaction.commit()
        self.browser.open(file.absolute_url() + "/@@download/file")
        self.assertEqual(len(self.browser.contents), len(data))
        self.assertIn(IUUID(file), self._ids())
