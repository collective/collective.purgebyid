from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class CollectivepurgebyidLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.purgebyid
        xmlconfig.file(
            'configure.zcml',
            collective.purgebyid,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    # def setUpPloneSite(self, portal):
    #     applyProfile(portal, 'collective.purgebyid:default')

COLLECTIVE_PURGEBYID_FIXTURE = CollectivepurgebyidLayer()
COLLECTIVE_PURGEBYID_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PURGEBYID_FIXTURE,),
    name="CollectivepurgebyidLayer:Integration"
)
COLLECTIVE_PURGEBYID_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PURGEBYID_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectivepurgebyidLayer:Functional"
)
