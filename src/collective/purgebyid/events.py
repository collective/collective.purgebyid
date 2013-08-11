from ZPublisher.interfaces import IPubSuccess
from ZPublisher.interfaces import IPubAfterTraversal
from ZODB.POSException import ConflictError
from zope.component import adapter
# import collections
import logging
from collective.purgebyid.api import markInvolvedObjs


logger = logging.getLogger('collective.purgebyid')


@adapter(IPubSuccess)
def handle_request_success(event):
    """handle "IPubSuccess".
    TODO: max header size
    """
    request = event.request
    involved = getattr(request, 'involved', None)
    if involved:  # isinstance(involved, collections.Iterable):
        event.request.response.setHeader(
            'X-Ids-Involved', '#' + '#'.join(involved) + '#')


@adapter(IPubAfterTraversal)
def handle_request_after_traversal(event):
    """handle "IPubAfterTraversal".
    """
    try:
        markInvolvedObjs(event.request, event.request.get('PARENTS', []))
        # published = event.request.get('PUBLISHED', None)
        # if published:
        #     context = getattr(published, 'context', None)
        #     if context:
        #         markInvolvedObjs(event.request, [context, ])
    except ConflictError:
        raise
    except:
        logger.exception(
            "Swallowed exception in IPubAfterTraversal event handler")
