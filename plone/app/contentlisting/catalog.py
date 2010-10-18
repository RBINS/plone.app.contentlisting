# Implementation of IContentListing and friends based on queries to
# the portal_catalog.  At the time of writing, this is the only and
# default IContentListing implementation.

from zope.component import queryMultiAdapter
from interfaces import IContentListing, IContentListingObject
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from zope import interface
from zLOG import LOG, INFO
from plone.app.layout.icons.interfaces import IContentIcon
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import queryUtility


class ContentListing:
    """ An IContentListing implementation based on sequences of objects"""
    interface.implements(IContentListing)

    def __init__(self, sequence):
        self._basesequence = sequence

    def __getitem__(self, index):
        """`x.__getitem__(index)` <==> `x[index]`
        """
        return IContentListingObject(self._basesequence[index])

    def __len__(self):
        """ length of the resultset is equal to the lenght of the underlying
            catalog resultset
        """
        return self._basesequence.__len__()

    def __iter__(self):
        """ let the sequence be iterable"""
        for obj in self._basesequence:
            yield IContentListingObject(obj)

    def __contains__(self, item):
        """`x.__contains__(item)` <==> `item in x`"""
        # huhm. How do we check this? Waking all contained objects is not fun
        # A content hash? Perhaps UID?
        for i in self:
            if i == item:
                return True
        return False

    def __lt__(self, other):
        """`x.__lt__(other)` <==> `x < other`"""
        raise NotImplementedError

    def __le__(self, other):
        """`x.__le__(other)` <==> `x <= other`"""
        raise NotImplementedError

    def __eq__(self, other):
        """`x.__eq__(other)` <==> `x == other`"""
        raise NotImplementedError

    def __ne__(self, other):
        """`x.__ne__(other)` <==> `x != other`"""
        raise NotImplementedError

    def __gt__(self, other):
        """`x.__gt__(other)` <==> `x > other`"""
        raise NotImplementedError

    def __ge__(self, other):
        """`x.__ge__(other)` <==> `x >= other`"""
        raise NotImplementedError

    def __add__(self, other):
        """`x.__add__(other)` <==> `x + other`"""
        raise NotImplementedError

    def __mul__(self, n):
        """`x.__mul__(n)` <==> `x * n`"""
        raise NotImplementedError

    def __rmul__(self, n):
        """`x.__rmul__(n)` <==> `n * x`"""
        raise NotImplementedError

    def __getslice__(self, i, j):
        """`x.__getslice__(i, j)` <==> `x[i:j]`
        Use of negative indices is not supported.
        Deprecated since Python 2.0 but still a part of `UserList`.
        """
        return IContentListing(self._basesequence[i:j])


class CatalogContentListingObject:
    """A Catalog-results based content object representation"""

    interface.implements(IContentListingObject)

    def __init__(self, brain):
        self._brain = brain
        self._cached_realobject = None
        self.request = brain.REQUEST

    def __repr__(self):
        return "<plone.app.contentlisting.catalog." + \
               "CatalogContentListingObject instance at %s>" % (
            self.getPath(), )

    __str__ = __repr__

    def __eq__(self, other):
        """For comparing two contentlistingobject"""
        other = IContentListingObject(other)
        # TODO: For object types that don't support UID, we must make it 
        # compare a different attribute.
        return self.UID() == other.UID()

    def __getattr__(self, name):
        """We'll override getattr so that we can defer name lookups
        to the real underlying objects without knowing the names of
        all attributes """
        if name.startswith('_'):
            raise AttributeError(name)
        if hasattr(aq_base(self._brain), name):
            LOG('plone.app.contentlisting', INFO,
                "deferred attribute lookup '%s' to brain %s" % (
                    name, str(self._brain), ))
            return getattr(self._brain, name)
        elif hasattr(aq_base(self.realobject), name):
            LOG('plone.app.contentlisting', INFO,
                "deferred attribute lookup '%s' to the real object %s" % (
                    name, str(self.realobject), ))
            return getattr(aq_base(self.realobject), name)
        else:
            raise AttributeError(name)

    def getDataOrigin(self):
        """ The origin of the data for the object.

        Sometimes we just need to know if we are looking at a brain or
        the real object
        """
        if self._cached_realobject is not None:
            return self._cached_realobject
        else:
            return self._brain

    @property
    def realobject(self):
        """get the real, underlying object

        This is performance intensive compared to just getting the
        catalog brain, so we don't do it until we need to.  We may
        even have to log this to notify the developer that this might
        be an inefficient operation.
        """
        if self._cached_realobject is None:
            self._cached_realobject = self._brain.getObject()
            LOG('plone.app.contentlisting', INFO,
                "fetched real object for %s" % (str(self._brain), ))
        return self._cached_realobject

    # a base set of elements that are needed but not defined in dublin core

    def getId(self):
        return self._brain.getId

    def getPath(self):
        return self._brain.getPath()

    def getURL(self):
        return self._brain.getURL()

    def UID(self):
        # content objects might have UID and might not. Same thing for
        # their brain.
        if hasattr(aq_base(self._brain), 'UID'):
            return self._brain.UID
        else:
            return aq_base(self.realobject).UID()

    def getIcon(self):
        return queryMultiAdapter((self._brain, self.request, self._brain),
                                 interface=IContentIcon)()

    def getSize(self):
        return self._brain.getObjSize

    def review_state(self):
        return self._brain.review_state

    # All the dublin core elements. Most of them should be in the
    # brain for easy access

    def Title(self):
        """title"""
        return self._brain.Title

    def Description(self):
        """description"""
        return self._brain.Description

    def CroppedDescription(self):
        """cropped description"""
        # Let's port Plones description cropping here instead of
        # implementing it all in the templates.
        return self.Description()

    def Type(self):
        return self._brain.Type

    def listCreators(self):
        """ """
        return self._brain.listCreators

    def getUserData(self, username):
        _usercache = self.request.get('usercache', None)
        if _usercache is None:
            self.request.set('usercache', {})
            _usercache = {}
        userdata = _usercache.get(username, None)
        if userdata is None:
            membershiptool = getToolByName(self._brain, 'portal_membership')
            userdata = membershiptool.getMemberInfo(self._brain.Creator)
            if not userdata:
                userdata = {'username': username,
                'description': '',
                'language': '',
                'home_page': '',
                'location': '',
                'fullname': username}
            self.request.usercache[username] = userdata
        return userdata

    def Creator(self):
        """ """
        username = self._brain.Creator
        return self.getUserData(username)

    def Subject(self):
        return self._brain.Subject

    def Publisher(self):
        raise NotImplementedError

    def listContributors(self):
        raise NotImplementedError

    def Contributors(self):
        return self.listContributors()

    def Date(self, zone=None):
        return self._brain.Date

    def CreationDate(self, zone=None):
        return self._brain.CreationDate

    def EffectiveDate(self, zone=None):
        return self._brain.EffectiveDate

    def ExpirationDate(self, zone=None):
        return self._brain.ExpirationDate

    def ModificationDate(self, zone=None):
        return self._brain.ModificationDate

    def Format(self):
        raise NotImplementedError

    def Identifier(self):
        return self.getURL()

    def Language(self):
        """the language of the content"""
        if hasattr(aq_base(self._brain), 'Language'):
            return self._brain.Language
        else:
            return self.realobject.Language()

    def Rights(self):
        raise NotImplementedError

    def appendViewAction(self):
        """decide whether to produce a string /view to append to links
        in results listings"""
        try:
            types = self._brain.portal_properties.site_properties \
                        .typesUseViewActionInListings
        except AttributeError:
            return ''
        if self.Type() in types:
            return "/view"
        return ''

    def ContentTypeClass(self):
        """A normalised type name that identifies the object in listings.
        used for CSS styling"""
        return "contenttype-" + queryUtility(IIDNormalizer).normalize(
            self.Type())


class RealContentListingObject:
    """A content object representation wrapping a real content object"""

    interface.implements(IContentListingObject)

    def __init__(self, obj):
        self.realobject = obj
        self.request = self.realobject.REQUEST

    def __repr__(self):
        return "<plone.app.contentlisting.catalog." + \
               "CatalogContentListingObject instance at %s>" % (
            self.getPath(), )

    __str__ = __repr__

    def __eq__(self, other):
        """For comparing two contentlistingobject"""
        other = IContentListingObject(other)
        return self.UID() == other.UID()

    def __getattr__(self, name):
        """We'll override getattr so that we can defer name lookups to
        the real underlying objects without knowing the names of all
        attributes.
        """
        if name.startswith('_'):
            raise AttributeError(name)
        elif hasattr(aq_base(self.realobject), name):
            LOG('plone.app.contentlisting', INFO,
                "deferred attribute lookup to the real object %s" % (
                    str(self._brain), ))
            return getattr(aq_base(self.realobject), name)
        else:
            raise AttributeError(name)

    def getDataOrigin(self):
        """The origin of the data for the object.

        Sometimes we just need to know if we are looking at a brain or
        the real object.
        """
        return self.realobject

    # a base set of elements that are needed but not defined in dublin core

    def getPath(self):
        return '/'.join(self.realobject.getPhysicalPath())

    def getURL(self):
        return self.realobject.absolute_url()

    def UID(self):
        # content objects might have UID and might not. Same thing for
        # their brain.
        if hasattr(aq_base(self.realobject), 'UID'):
            return self.realobject.UID()
        else:
            raise AttributeError('UID')

    def getIcon(self):
        return queryMultiAdapter(
            (self.realobject, self.request, self.realobject),
            interface=IContentIcon)()

    def review_state(self):
        wftool = getToolByName(self.realobject, "portal_workflow")
        return wftool.getInfoFor(self.realobject, 'review_state')
