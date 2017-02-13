from zope.interface import Interface


class IInvolvedID(Interface):
   """Adapter to find uid involved for the context

   the adapter return:
   * an id (basestring) or 
   * collective.purgebyid.api.NOID (no id for this
     object, used for stoponfirst) or
   * None (no id for this object, try the next) or
   * a list of element above.

   """

