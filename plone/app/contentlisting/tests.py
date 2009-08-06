import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

from interfaces import IContentListing, IContentListingObject
import plone.app.contentlisting
import plone.app.layout
from zope.interface.verify import verifyObject 

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             plone.app.contentlisting)
            zcml.load_config('configure.zcml',
                             plone.app.layout)

            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

class TestCatalogInterface(TestCase):
        #   - self.portal is the portal root
        #   - self.folder is the current user's folder
        #   - self.logout() "logs out" so that the user is Anonymous
        #   - self.setRoles(['Manager', 'Member']) adjusts the roles of the current user
    
#    def makeTestObject(self): 
#        """Returns an ISample instance""" 
#        return IContentListingFactory(self.folder)()
#    
#    def test_portal_title(self):
#        # testing that my tests run
#        self.assertEquals("Plone site", self.portal.getProperty('title'))
#
#    def testListingImplementsInterface(self):
#        self.failUnless(verifyObject(IContentListing, self.makeTestObject()))
#
#    def testListingObjectsImplementsInterface(self):
#        self.failUnless(verifyObject( IContentListingObject, self.makeTestObject()[0]))
#        
#    def testFolderContents(self):
#        listing = self.portal.folderListing()
#        self.failUnless(verifyObject( IContentListing, listing))
#        print listing
    pass
        
        
def test_suite():
    """ testing  """
    suite = unittest.TestSuite([
    # Unit tests
    #doctestunit.DocFileSuite(
    #    'README.txt', package='plone.app.contentlisting',
    #    setUp=testing.setUp, tearDown=testing.tearDown),

    #doctestunit.DocTestSuite(
    #    module='plone.app.contentlisting.mymodule',
    #    setUp=testing.setUp, tearDown=testing.tearDown),


    # Integration tests that use PloneTestCase
    ztc.ZopeDocFileSuite(
        'README.txt', package='plone.app.contentlisting',
        test_class=TestCase),

    #ztc.FunctionalDocFileSuite(
    #    'browser.txt', package='plone.app.contentlisting',
    #    test_class=TestCase),

    ])
    suite.addTest(unittest.makeSuite(TestCatalogInterface))
    return suite 
    
    
        
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
