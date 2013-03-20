import routes.mapper

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckan.lib.base as base


class DataGMPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')

    def before_map(self, route_map):
        with routes.mapper.SubMapper(route_map,
                controller='ckanext.datagm.plugin:DataGMController') as m:
            m.connect('privacy', '/privacy', action='privacy')
            m.connect('codeofconduct', '/codeofconduct',
                    action='codeofconduct')
            m.connect('accessibility', '/accessibility',
                    action='accessibility')
            m.connect('licence', '/licence', action='licence')
            m.connect('faq', '/faq', action='faq')
        return route_map

    def after_map(self, route_map):
        return route_map

class DataGMController(base.BaseController):

    def privacy(self):
        return base.render('privacy.html')

    def codeofconduct(self):
        return base.render('codeofconduct.html')

    def accessibility(self):
        return base.render('accessibility.html')

    def licence(self):
        return base.render('licence.html')

    def faq(self):
        return base.render('faq.html')
