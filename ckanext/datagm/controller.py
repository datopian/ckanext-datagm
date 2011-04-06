import sys
from ckan.lib.base import request
from ckan.lib.base import c, g, h
from ckan.lib.base import model
from ckan.lib.base import etag_cache, cache
from ckan.lib.base import render
from ckan.lib.base import _
import random
from ckan.lib.search import query_for
import ckan.lib.stats
import ckan.authz as authz
from ckan.authz import Authorizer
from ckanext.googleanalytics.controller import GAController
from ckanext.googleanalytics import dbutil
from ckan.controllers.user import UserController
from ckan.lib.cache import proxy_cache, get_cache_expires

cache_expires = get_cache_expires(sys.modules[__name__])


class DataGMUserController(UserController):
    def datagm_register(self):
        if request.method == 'POST':
            # custom validation for DataGM
            error = False
            c.email = request.params.getone('email')
            c.login = request.params.getone('login')
            if not model.User.check_name_available(c.login):
                error = True
                h.flash_error(_("That username is not available."))
            if not c.email:
                error = True
                h.flash_error(_("You must supply an email address."))
            try:
                self._get_form_password()
            except ValueError, ve:
                h.flash_error(ve)
                error = True
            if error:
                return render('user/register.html')
        # now delegate to core CKAN register method
        return self.register()


class DataGMHomeController(GAController):

    authorizer = Authorizer()

    @proxy_cache(expires=cache_expires)
    def index(self):
        c.groups = authz.Authorizer()\
                   .authorized_query(c.user,
                                     model.Group)\
                   .order_by(model.Group.title)
        c.top_packages = dbutil.get_top_packages(limit=5)
        c.body_class = "home"
        query = query_for(model.Package)
        query.run(query='*:*', facet_by=g.facets,
                  limit=0, offset=0, username=c.user)
        c.facets = query.facets
        c.fields = []
        c.package_count = query.count
        c.latest_packages = self.authorizer.authorized_query(
            c.user, model.Package)\
            .join('revision').order_by(model.Revision.timestamp.desc())\
            .limit(5).all()

        if len(c.latest_packages):
            cache_key = str(hash((c.latest_packages[0].id, c.user)))
        else:
            cache_key = "fresh-install"

        etag_cache(cache_key)

        def tag_counts():
            '''Top 50 tags (by package counts) in random order (to make cloud
            look nice).
            '''
            tag_counts = ckan.lib.stats.Stats().top_tags(limit=50,
                                            returned_tag_info='name')
            tag_counts = [tuple(row) for row in tag_counts]
            random.shuffle(tag_counts)
            return tag_counts
        mycache = cache.get_cache('tag_counts', type='dbm')
        c.tag_counts = mycache.get_value(key='tag_counts_home_page',
                createfunc=tag_counts, expiretime=cache_expires)
        return render('home/index.html', cache_key=cache_key,
                cache_expire=cache_expires)
