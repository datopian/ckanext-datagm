import os
from logging import getLogger

from genshi.filters.transform import Transformer
from genshi.input import HTML

from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IRoutes, IConfigurer
from ckan.plugins import IGenshiStreamFilter

log = getLogger(__name__)


class DataGMPlugin(SingletonPlugin):
    implements(IRoutes, inherit=True)
    implements(IConfigurer, inherit=True)
    implements(IGenshiStreamFilter, inherit=True)

    def before_map(self, map):
        map.connect('home', '/',
                    controller='ckanext.datagm.controller:DataGMHomeController',
                    action='index')
        map.connect('/user/register',
                    controller='ckanext.datagm.controller:DataGMUserController',
                    action='datagm_register')
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
        config['googleanalytics.id'] = 'UA-26856027-1'
        config['ckan.site_title'] = "DataGM - Data Greater Manchester"
        config['ckan.site_logo'] = "/img/datagm-beta.png"
        config['ckan.default_roles.Package'] = \
                 ('{"visitor": ["reader"], '
                  '"logged_in": ["reader"]} ')

    def filter(self, stream):
        text_containers = ["p", "a", "h1", "h2", "h3", "h4", "em",
                           "strong"]
        text_xpath = "|".join(["//%s/text()" % x \
                               for x in text_containers])
        stream = stream | Transformer(text_xpath)\
                 .substitute(r'([^/])[pP]ackage', r'\1dataset')
        return stream
