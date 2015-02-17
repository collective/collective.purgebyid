import unittest2 as unittest

# from Products.CMFCore.utils import getToolByName

from collective.purgebyid.testing import \
    COLLECTIVE_PURGEBYID_INTEGRATION_TESTING


class TestExample(unittest.TestCase):

    layer = COLLECTIVE_PURGEBYID_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_api(self):
        pass
