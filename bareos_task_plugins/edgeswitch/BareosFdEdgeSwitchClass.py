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
from commons.BareosFdTaskClass import BareosFdTaskClass, TaskException, TaskStringIO
from edgeswitch import EdgeSwitch


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
