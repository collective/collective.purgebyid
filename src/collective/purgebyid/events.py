from collective.purgebyid import logger
from collective.purgebyid.api import get_involved_objects
from collective.purgebyid.api import mark_involved_objects
from plone.transformchain.interfaces import ITransform
from ZODB.POSException import ConflictError
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from ZPublisher.interfaces import IPubAfterTraversal

import os

HEADER_NAME = "X-Ids-Involved"
MAX_HEADER_LENGTH_ENV = "COLLECTIVE_PURGEBYID_MAX_HEADER_LENGTH"
# Varnish (http_resp_hdr_len) and Apache default to 8 KB per header line,
# nginx (proxy_buffer_size) to 4 KB for the whole response header block.
DEFAULT_MAX_HEADER_LENGTH = 4096


def get_max_header_length():
    """Maximum length of the X-Ids-Involved header value, in bytes.

    Read from the COLLECTIVE_PURGEBYID_MAX_HEADER_LENGTH environment
    variable; 0 or a negative value disables the limit.
    """
    value = os.environ.get(MAX_HEADER_LENGTH_ENV)
    if value is None:
        return DEFAULT_MAX_HEADER_LENGTH
    try:
        return int(value)
    except ValueError:
        logger.warning(
            "invalid %s=%r, using default %d",
            MAX_HEADER_LENGTH_ENV,
            value,
            DEFAULT_MAX_HEADER_LENGTH,
        )
        return DEFAULT_MAX_HEADER_LENGTH


def build_header(ids, max_length=None):
    """Build the X-Ids-Involved header value ("#id1#id2#").

    Ids are sorted, so the value is stable across requests. If the value
    would exceed ``max_length``, ids that do not fit are dropped and a
    warning is logged. Return None when no id fits.
    """
    ids = sorted(ids)
    value = "#" + "#".join(ids) + "#"
    if max_length is None or max_length <= 0 or len(value) <= max_length:
        return value
    kept = []
    length = 1  # leading "#"
    for id in ids:
        if length + len(id) + 1 > max_length:
            continue
        kept.append(id)
        length += len(id) + 1
    logger.warning(
        "%s header too long (%d > %d bytes): dropped %d of %d ids",
        HEADER_NAME,
        len(value),
        max_length,
        len(ids) - len(kept),
        len(ids),
    )
    if not kept:
        return None
    return "#" + "#".join(kept) + "#"


@implementer(ITransform)
@adapter(Interface, Interface)
class MutatorTransform:
    """Transformation using plone.transformchain.
    This is registered at order 11000, i.e. "late". A typical transform

    chain order may include:
    * lxml transforms (e.g. plone.app.blocks, collectivexdv) => 8000-8999
    * gzip => 10000
    * mark ids involved => 11000
    * caching => 12000

    This transformer is uncommon in that it doesn't actually change the
    response body. Instead, we look up caching operations which can modify
    response headers and perform other caching functions.

    The header value is capped at ``get_max_header_length()`` bytes
    (4096 by default, about 120 UUIDs): see ``build_header``.
    """

    order = 11000

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def transformUnicode(self, result, encoding):  # pragma: nocover
        self.mutate()
        return None

    def transformBytes(self, result, encoding):  # pragma: nocover
        self.mutate()
        return None

    def transformIterable(self, result, encoding):
        self.mutate()
        return None

    def mutate(self):
        request = self.request
        involved = get_involved_objects(request)
        if not involved:
            return
        value = build_header(involved, get_max_header_length())
        if value:
            request.response.setHeader(HEADER_NAME, value)


@adapter(IPubAfterTraversal)
def handle_request_after_traversal(event):
    """handle "IPubAfterTraversal"."""
    try:
        mark_involved_objects(
            event.request, event.request.get("PARENTS", []), stoponfirst=True
        )
        # published = event.request.get('PUBLISHED', None)
        # if published:
        #     context = getattr(published, 'context', None)
        #     if context:
        #         mark_involved_objects(event.request, [context, ])
    except ConflictError:  # pragma: nocover
        raise
    except Exception:  # pragma: nocover
        logger.exception("Swallowed exception in IPubAfterTraversal event handler")
