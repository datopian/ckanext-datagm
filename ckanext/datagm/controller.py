import sys
from ckan.lib.base import *
from ckan.lib.search import query_for
import ckan.authz as authz
from ckanext.googleanalytics.controller import GAController
from ckan.lib.cache import proxy_cache, get_cache_expires

cache_expires = get_cache_expires(sys.modules[__name__])


class DataGMHomeController(GAController):
    @proxy_cache(expires=cache_expires)
    def index(self):
        c.groups = authz.Authorizer()\
                   .authorized_query(c.user,
                                     model.Group)\
                   .order_by(model.Group.title)
        c.top_packages = [x[0] for x in self.get_top_packages()][:5]
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
        return render('home/index.html', cache_key=cache_key,
                cache_expire=cache_expires)
