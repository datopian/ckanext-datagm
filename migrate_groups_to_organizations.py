#!/usr/bin/env python
'''
A script for migrating a CKAN site's groups to organizations.

Note that this currently requires the group_purge() API action, which is only
available on a feature branch and not in CKAN master. This is because you can't
have an organization and a group with the same name in CKAN even if the group
has been deleted (because deleted groups still remain in the database), so it's
necessary to purge a group from the db before creating an organization with the
same name.

An alternative approach would be to transform the group into an organization
"in place", but purging seemed more generally useful.

'''
import urlparse
import urllib2
import urllib
import json


GROUPS_FILE = 'cached_groups.json'


def post_to_ckan_api(base_url, action, data=None, apikey=None):
    '''Post a data dict to one of the actions of the CKAN action API.

    See the documentation of the action API, including each of the available
    actions and the data dicts they accept, here:
    http://docs.ckan.org/en/ckan-1.8/apiv3.html

    :param base_url: the base URL of the CKAN instance to post to,
        e.g. "http://datahub.io/"
    :type base_url: string

    :param action: the action to post to, e.g. "package_create"
    :type action: string

    :param data: the data to post (optional, default: {})
    :type data: dictionary

    :param apikey: the CKAN API key to put in the 'Authorization' header of
        the HTTP request (optional, default: None)
    :type apikey: string

    :returns: the dictionary returned by the CKAN API, a dictionary with three
        keys 'success' (True or False), 'help' (the docstring for the action
        posted to) and 'result' in the case of a successful request or 'error'
        in the case of an unsuccessful request
    :rtype: dictionary

    '''
    if data is None:
        # Even if you don't want to post any data to the CKAN API, you still
        # have to send an empty dict.
        data = {}
    path = '/api/action/{action}'.format(action=action)
    url = urlparse.urljoin(base_url, path)
    request = urllib2.Request(url)
    if apikey is not None:
        request.add_header('Authorization', apikey)
    try:
        response = urllib2.urlopen(request, urllib.quote(json.dumps(data)))
        # The CKAN API returns a dictionary (in the form of a JSON string)
        # with three keys 'success' (True or False), 'result' and 'help'.
        d = json.loads(response.read())
        assert d['success'] is True, d
        return d
    except urllib2.HTTPError, e:
        # For errors, the CKAN API also returns a dictionary with three
        # keys 'success', 'error' and 'help'.
        error_string = e.read()
        try:
            d = json.loads(error_string)
            if type(d) is unicode:
                # Sometimes CKAN returns an error as a JSON string not a dict,
                # gloss over it here.
                return {'success': False, 'help': '', 'error': d}
            assert d['success'] is False
            return d
        except ValueError:
            # Sometimes CKAN returns a string that is not JSON, lets gloss
            # over it.
            return {'success': False, 'error': error_string, 'help': ''}


def _get_groups_from_site(base_url):
    print "Getting group list from site {0}".format(base_url)
    response = post_to_ckan_api(base_url, 'group_list')
    assert response['success'] is True
    group_names = response['result']
    groups = []
    for group_name in group_names:
        print "Getting group {0} from site {1}".format(group_name, base_url)
        response = post_to_ckan_api(base_url, 'group_show',
                data={'id': group_name})
        assert response['success'] is True
        group = response['result']
        groups.append(group)
    print "Writing {0} groups to file {1}".format(len(groups), GROUPS_FILE)
    open(GROUPS_FILE, 'w').write(json.dumps(groups))
    print "{0} groups written to file {1}".format(len(groups), GROUPS_FILE)
    return groups


def get_groups(base_url):
    try:
        print "Reading groups from file {0}".format(GROUPS_FILE)
        groups = json.loads(open(GROUPS_FILE, 'r').read())
        print "{0} groups read from file {1}".format(len(groups), GROUPS_FILE)
    except Exception:
        print "Reading groups from file {0} failed".format(GROUPS_FILE)
        groups = _get_groups_from_site(base_url)
    return groups


def purge_group(base_url, group, apikey):
    print "Purging group {0} from site {1}".format(group['name'], base_url)
    response = post_to_ckan_api(base_url, 'group_purge',
            data={'id': group['id']}, apikey=apikey)
    if response['success'] is not True:
        assert response['success'] is False
        error = response['error']
        if error.get('__type') == 'Not Found Error':
            print "Looks like group {0} has already been purged".format(
                    group['name'])
        else:
            raise Exception(error)


def create_org(base_url, org, apikey):
    print "Creating organization {0} on site {1}".format(
            org['name'], base_url)
    response = post_to_ckan_api(base_url, 'organization_create', data=org,
            apikey=apikey)
    if response['success'] is not True:
        assert response['success'] is False
        error = response['error']
        if error.get('__type') == 'Validation Error':
            if error.get('name') == ['Group name already exists in database']:
                print "Looks like org {0} has already been created".format(
                        org['name'])
                return
        raise Exception(error)


def organization_dict_from_group_dict(group_dict):
    organization_dict = {
        'name': group_dict['name'],
        'title': group_dict['title'],
        'description': group_dict['description'],
    }
    return organization_dict


def get_packages_from_datagm():
    '''Fetch all the package dicts from the old (CKAN 1.3) datagm.org.uk site.

    '''
    base_url = 'http://www.datagm.org.uk'

    print "Getting package list from {0}".format(base_url)
    path = '/api/rest/package'
    url = urlparse.urljoin(base_url, path)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    package_names = json.loads(response.read())

    packages = []
    for package_name in package_names:
        print "Getting package {0} from {1}".format(package_name, base_url)
        path = '/api/rest/package/{0}'.format(package_name)
        url = urlparse.urljoin(base_url, path)
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        package = json.loads(response.read())
        packages.append(package)
    print "Got {0} packages from {1}".format(len(packages), base_url)
    return packages


def move_package_into_organization(base_url, package, apikey):

    # First get the current package dict from the target site.
    # This is to avoid any problems with partial updates deleting fields
    # from the package.
    print "Getting package {0} from site {1}".format(package['name'],
            base_url)
    response = post_to_ckan_api(base_url, 'package_show',
            data={'id': package['name']})
    if response['success'] is not True:
        assert response['success'] is False
        error = response['error']
        if error.get('__type') == 'Not Found Error':
            print "Package {0} does not exist on site {1}".format(
                    package['name'], base_url)
            return
        raise Exception(error)
    package_dict = response['result']

    # Decide which org to add the package to depending on the groups it
    # belongs to on the old site.
    if len(package['groups']) > 1:
        # A package can belong to multiple groups, but only one organization.
        # If a package belongs to multiple groups then we put it in the
        # 'greater-manchester' organization.
        package_dict['owner_org'] = 'greater-manchester'
    elif len(package['groups']) == 1:
        package_dict['owner_org'] = package['groups'][0]
    else:
        assert len(package['groups']) == 0
        print "Package {0} does not belong to any groups".format(
                package['name'])
        return

    # Add the package to the org.
    print "Adding package {0} to org {1}".format(
            package_dict['name'], package_dict['owner_org'])
    response = post_to_ckan_api(base_url, 'package_update',
            data=package_dict, apikey=apikey)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--apikey', required=True)
    args = parser.parse_args()

    groups = get_groups(args.base_url)
    for group in groups:
        purge_group(args.base_url, group, args.apikey)
        create_org(args.base_url, organization_dict_from_group_dict(group),
                args.apikey)

        create_org(args.base_url,
            {'name': 'greater-manchester', 'title': 'Greater Manchester'},
            args.apikey)

    # There's a bug in the new CKAN 2.0 DataGM site, caused by the database
    # migration from CKAN 1.3 -> 2,0, which means that group_show() and
    # package_show() will not correctly report which groups a package belongs
    # to. So we have to get the list of packages and their groups from the
    # old CKAN 1.3 DataGM site instead.
    packages = get_packages_from_datagm()
    for package in packages:
        move_package_into_organization(args.base_url, package, args.apikey)


if __name__ == '__main__':
    main()
