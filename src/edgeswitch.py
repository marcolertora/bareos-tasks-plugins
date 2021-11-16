#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4 -*-
#
# BareOS FileDaemon Task plugin
# Copyright (C) 2018 Marco Lertora <marco.lertora@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from datetime import datetime

import requests
import urllib3
urllib3.disable_warnings()


class EdgeSwitch:

    @staticmethod
    def save_backup(host, username, password, filename):
        content = EdgeSwitch.get_backup(host, username, password)
        open(filename, 'wb').write(content)

    @staticmethod
    def get_backup(host, username, password):
        device = EdgeSwitch(host)
        device.login(username, password)
        content = device.backup()
        device.logout()
        return content

    def __init__(self, host):
        self.host = host
        self.token = None

    def get_base_url(self):
        return 'https://{0}/'.format(self.host)

    def login(self, username, password):

        data = {
            'username': username,
            'password': password,
        }

        headers = {
            'Referer': self.get_base_url(),
        }

        r = requests.post(self.get_base_url() + 'api/v1.0/user/login', json=data, headers=headers, verify=False)

        if r.status_code != 200:
            raise Exception('Invalid HTTP status code: {0}'.format(r.status_code))

        if r.json()['statusCode'] != 200:
            raise Exception('Invalid payload status code')

        self.token = r.headers['x-auth-token']

    def logout(self):
        headers = {
            'x-auth-token': self.token,
            'Referer': self.get_base_url(),
        }

        r = requests.post(self.get_base_url() + 'api/v1.0/user/logout', headers=headers, verify=False)

        if r.status_code != 200:
            raise Exception('Invalid HTTP status code')

        if r.json()['statusCode'] != 200:
            raise Exception('Invalid payload status code')

        self.token = None

    def backup(self):
        assert self.token, 'auth token is required'

        headers = {
            'x-auth-token': self.token,
            'Referer': self.get_base_url(),
        }

        r = requests.get(self.get_base_url() + 'api/v1.0/system/backup', headers=headers, verify=False)

        if r.status_code != 200:
            raise Exception('Invalid HTTP status code')

        return r.content


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'host',
        type=str,
        help='host of the edgeswitch: 192.168.1.1'
    )
    parser.add_argument(
        '--username',
        type=str,
        default='ubnt',
        metavar='username',
        help='username of the edgeswitch (default: %(default)s)'
    )
    parser.add_argument(
        '--password',
        type=str,
        default='ubnt',
        metavar='password',
        help='password of the edgeswitch (default: %(default)s)'
    )
    parser.add_argument(
        '--filename',
        type=str,
        required=False,
        metavar='filename',
        default='backup_{host}_{timestamp}.tgz',
        help='output filename of the backup (default: %(default)s)'
    )

    args = parser.parse_args()

    try:
        filename = args.filename.format(
            host=args.host,
            timestamp=datetime.now().strftime('%Y%m%d%H%M%S')
        )
    except Exception as e:
        sys.exit('invalid filename format: {0}'.format(args.filename))

    print('host {0} saving backup to {1}...'.format(args.host, filename))
    backup = EdgeSwitch.get_backup(args.host, args.username, args.password)
    output = open(filename, 'wb')
    output.write(backup)
    output.close()
