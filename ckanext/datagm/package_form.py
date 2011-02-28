from sqlalchemy.util import OrderedDict
from pylons.i18n import _

from ckan.forms import common
from ckan.forms import package 

# Setup the fieldset
def build_package_gov_form(is_admin=False,
                           user_editable_groups=None,
                           **kwargs):
    # Restrict fields
    builder = package.build_package_form(
        user_editable_groups=user_editable_groups)

    # Extra fields
    builder.add_field(common.DateRangeExtraField('temporal_coverage'))

    # Layout
    field_groups = OrderedDict([
        (_('Basic information'), ['title', 'name', 'url',
                                  'notes', 'tags']),
        (_('Details'), ['author', 'author_email',
                        'maintainer', 'maintainer_email',
                        'license_id', 'temporal_coverage' ]),
        (_('Resources'), ['resources']),
        ])
    builder.set_displayed_fields(field_groups)
    return builder


def get_datagm_fieldset(is_admin=False, user_editable_groups=None, **kwargs):
    return build_package_gov_form(is_admin=is_admin,
                                  user_editable_groups=user_editable_groups,
                                  **kwargs).get_fieldset()
