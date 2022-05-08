from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig


class CollectivepurgebyidLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.purgebyid

        xmlconfig.file(
            "configure.zcml", collective.purgebyid, context=configurationContext
        )


COLLECTIVE_PURGEBYID_FIXTURE = CollectivepurgebyidLayer()
COLLECTIVE_PURGEBYID_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PURGEBYID_FIXTURE,), name="CollectivepurgebyidLayer:Integration"
)
COLLECTIVE_PURGEBYID_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PURGEBYID_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectivepurgebyidLayer:Functional",
)
