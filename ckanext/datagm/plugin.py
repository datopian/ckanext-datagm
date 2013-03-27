import routes.mapper

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckan.lib.base as base
import pylons.i18n


def organization_show(name):
    '''Return the organization dict for the given organization.'''
    return tk.get_action('organization_show')(data_dict={'id': name})


def organization_list():
    '''Return a list of the names of all of the site's organizations.'''
    return tk.get_action('organization_list')(data_dict={})


def popular_datasets(limit=4):
    '''Return a list of the most popular datasets on the site.'''
    response = tk.get_action('package_search')(
            data_dict={'sort': 'views_recent desc', 'rows': limit})
    return response['results']


def latest_datasets(limit=4):
    '''Return a list of the most popular datasets on the site.'''
    response = tk.get_action('package_search')(
            data_dict={'sort': 'metadata_modified desc', 'rows': limit})
    return response['results']

# This overrides the default resource_display_name() template helper, and
# changes it to say "Unnamed resource" instead of the resource's URL if the
# resource has no name.
def resource_display_name(resource_dict):
    name = resource_dict.get('name', None)
    description = resource_dict.get('description', None)
    if name:
        return name
    elif description:
        description = description.split('.')[0]
        max_len = 60
        if len(description) > max_len:
            description = description[:max_len] + '...'
        return description
    else:
        return pylons.i18n._("Unnamed resource")


class DataGMPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_public_directory(config, 'public')

        config['ckan.site_logo'] = '/logo.png'
        config['ckan.site_custom_css'] = '''
            .header-image { margin: 10px 0; }
            .masthead { top: 20px; }
            '''

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

    def get_helpers(self):
        return {
                'organization_show': organization_show,
                'organization_list': organization_list,
                'popular_datasets': popular_datasets,
                'latest_datasets': latest_datasets,
                'resource_display_name': resource_display_name,
                }


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
