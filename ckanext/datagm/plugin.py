import ckan.plugins as plugins
import ckan.plugins.toolkit as tk


class DataGMPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer, inherit=False)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')
