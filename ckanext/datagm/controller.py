from ckan.lib.base import *
import ckan.authz as authz
from ckan.controllers.home import HomeController
from ckanext.googleanalytics.controller import GAController


class DataGMHomeController(HomeController, GAController):
    def index(self):
        c.groups = authz.Authorizer()\
                   .authorized_query(c.user,
                                     model.Group)\
                   .order_by(model.Group.title)
        c.top_packages = [x[0] for x in self.get_top_packages()][:5]
        c.body_class = "home"
        return super(DataGMHomeController, self).index()
