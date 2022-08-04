from zope.interface import Interface


class IInvolvedID(Interface):
    """Adapter to find uids involved for the context."""

    def __call__():
        """Return the involved ids.

        :returns: involved ids
        :rtype: list
        """
