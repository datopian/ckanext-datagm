from ckan.lib.base import *
import ckan.authz as authz
from ckan.controllers.home import HomeController


class DataGMHomeController(HomeController):
    def index(self):
        c.groups = authz.Authorizer().authorized_query(c.user,
                                                       model.Group)
        return super(DataGMHomeController, self).index()
