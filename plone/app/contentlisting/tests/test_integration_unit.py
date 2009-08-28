"""This is an integration "unit" test. It uses PloneTestCase, but does not
use doctest syntax.

You will find lots of examples of this type of test in CMFPlone/tests, for 
example.
"""

import unittest
from base import ContentlistingTestCase, ContentlistingFunctionalTestCase
from Products.CMFCore.utils import getToolByName
from zope.interface.verify import verifyObject 
from plone.app.contentlisting.interfaces import IContentListing, IContentListingObject
from Products.Five.testbrowser import Browser
        

class TestSetup(ContentlistingFunctionalTestCase):
    """The name of the class should be meaningful. This may be a class that
    tests the installation of a particular product.
    """
    
    def afterSetUp(self):
        """This method is called before each single test. It can be used to
        set up common state. Setup that is specific to a particular test 
        should be done in that test method.
        """
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        
    def beforeTearDown(self):
        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """
    
    def test_portal_title(self):
        
        # This is a simple test. The method needs to start with the name
        # 'test'. 

        # Look at the Python unittest documentation to learn more about hte
        # kinds of assertion methods which are available.

        # PloneTestCase has some methods and attributes to help with Plone.
        # Look at the PloneTestCase documentation, but briefly:
        # 
        #   - self.portal is the portal root
        #   - self.folder is the current user's folder
        #   - self.logout() "logs out" so that the user is Anonymous
        #   - self.setRoles(['Manager', 'Member']) adjusts the roles of the current user
        
        self.assertEquals("Plone site", self.portal.getProperty('title'))

    def test_able_to_add_document(self):
        #just a dummy test to see that the basics are running
        new_id = self.folder.invokeFactory('Document', 'my-page')
        self.assertEquals('my-page', new_id)
        
    def test_empty_folder_contents(self):
        folderlisting = self.folder.restrictedTraverse('@@folderListing')()
        self.assertEqual(len(folderlisting), 0)
        
    def test_item_in_folder_contents(self):
        new_id = self.folder.invokeFactory('Document', 'my-page')
        folderlisting = self.folder.restrictedTraverse('@@folderListing')()
        self.assertEqual(len(folderlisting), 1)
        
    def testListingImplementsInterface(self):
        # Check that IContentListing conforms to its interface
        self.failUnless(verifyObject(IContentListing, IContentListing(self.catalog())))

    def testListingObjectsImplementsInterface(self):
        # Check that IContentListingObject conforms to its interface        
        self.failUnless(verifyObject(IContentListingObject, IContentListing(self.catalog())[0]))


    
    

    #  Having tests in multiple files makes
    #  it possible to run tests from just one package:
    #   
    #   ./bin/instance test -s example.tests -t test_integration_unit


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
