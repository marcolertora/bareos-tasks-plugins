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
from StringIO import StringIO
from BareosFdTaskClass import BareosFdTaskClass, TaskException, TaskStringIO
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



class TaskEdgeSwitchBackup(TaskStringIO):
    task_name = 'edgeswitch-backup'
    file_extension = 'tgz'

    def __init__(self, host, username, password):
        if not host:
            raise TaskException('host is required')

        if not username:
            raise TaskException('host is required')

        if not password:
            raise TaskException('host is required')

        self.host = host
        data = EdgeSwitch.get_backup(host, username, password)
        super(TaskEdgeSwitchBackup, self).__init__(self.task_name, StringIO(data))

    def get_name(self):
        return '{0}-{1}'.format(self.task_name, self.host)


class BareosFdEdgeSwitchClass(BareosFdTaskClass):
    plugin_name = 'edgeswitch'

    def prepare_tasks(self):
        self.tasks = list()

        task = TaskEdgeSwitchBackup(
            self.config.get('host'),
            self.config.get('username'),
            self.config.get('password'),
        )

        self.tasks.append(task)
