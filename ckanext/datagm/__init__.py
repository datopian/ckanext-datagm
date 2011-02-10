import os
from logging import getLogger

from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IRoutes, IConfigurer

log = getLogger(__name__)


class DataGMPlugin(SingletonPlugin):
    implements(IRoutes, inherit=True)
    implements(IConfigurer, inherit=True)

    def before_map(self, map):
        map.connect('home', '/',
                    controller='ckanext.datagm.controller:DataGMHomeController',
                    action='index')
        return map

    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        our_public_dir = os.path.join(rootdir, 'ckanext',
                                      'datagm', 'theme', 'public')
        template_dir = os.path.join(rootdir, 'ckanext',
                                    'datagm', 'theme', 'templates')
        config['extra_public_paths'] = ','.join([our_public_dir,
                config.get('extra_public_paths', '')])
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])
