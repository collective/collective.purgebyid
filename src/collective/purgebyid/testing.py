import collective.purgebyid
import plone.app.contenttypes
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2


class CollectivepurgebyidLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Install products that use an old-style initialize() function
        z2.installProduct(app, 'Products.DateRecurringIndex')
        self.loadZCML(package=plone.app.contenttypes)
        self.loadZCML(package=collective.purgebyid)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.app.contenttypes:default")
        portal["portal_workflow"].setDefaultChain("simple_publication_workflow")


COLLECTIVE_PURGEBYID_FIXTURE = CollectivepurgebyidLayer()
COLLECTIVE_PURGEBYID_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PURGEBYID_FIXTURE,), name="CollectivepurgebyidLayer:Integration"
)
COLLECTIVE_PURGEBYID_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PURGEBYID_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectivepurgebyidLayer:Functional",
)
