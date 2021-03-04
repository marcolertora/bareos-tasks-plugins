#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4 -*-
#
# Copyright (C) 2021 Marco Lertora <marco.lertora@gmail.com>
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
import argparse
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
            raise Exception('Invalid HTTP status code')

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
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'host',
        type=str,
        help='host of device'
    )
    parser.add_argument(
        '--filename',
        type=str,
        default='backup.tgz',
        help='output filename (default: %(default))'
    )
    parser.add_argument(
        '--username',
        type=str,
        default='admin',
        help='username of device (default: %(default))'
    )
    parser.add_argument(
        '--password',
        type=str,
        default='secret',
        help='password of device (default: %(default))'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        dest='safe_mode',
        help='verbose mode (default: %(default))'
    )

    args = parser.parse_args()

    print('backup edge switch: {0} to {1}...'.format(args.host, args.filename ))
    EdgeSwitch.save_backup(args.host, args.username, args.password, args.filename)
