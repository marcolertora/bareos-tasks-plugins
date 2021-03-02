#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4 -*-
#
# Bareos FileDaemon Task plugin
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

import socket
from BareosFdTaskClass import TaskProcess, BareosFdTaskClass


class TaskHostBackup(TaskProcess):
    task_name = 'host-backup'

    def __init__(self, hostname):
        self.command = ['xe', 'host-backup', 'hostname=' + hostname, 'file-name=']


class TaskPoolDumpDatabase(TaskProcess):
    task_name = 'pool-dump-database'
    file_extension = 'xml'

    def __init__(self):
        self.command = ['xe', 'pool-dump-database', 'file-name=']


class TaskVmExport(TaskProcess):
    task_name = 'vm-export'
    file_extension = 'xva'

    def __init__(self, vm_name):
        self.vm_name = vm_name
        self.command = ['xe', 'vm-export', 'vm=' + self.vm_name, 'filename=']
        super(TaskVmExport, self).__init__()

    def get_name(self):
        return '{0}-{1}'.format(self.task_name, self.vm_name)


class TaskSnapshotExport(TaskVmExport):
    task_name = 'snapshot-export'
    file_extension = 'xva'

    def __init__(self, vm_name):
        self.vm_name = vm_name
        self.command = []
        self.snapshot_uuid = None
        self.snapshot_name = self.vm_name + '_temporary_backup'
        super(TaskVmExport, self).__init__()

    def task_open(self, command=None):
        self.snapshot_uuid = self.execute_command(
            ['xe', 'vm-snapshot', 'vm=' + self.vm_name, 'new-name-label=' + self.snapshot_name]
        )
        super(TaskVmExport, self).task_open(
            ['xe', 'snapshot-export-to-template', 'snapshot-uuid=' + self.snapshot_uuid, 'filename=']
        )

    def task_wait(self):
        assert self.snapshot_uuid
        value = super(TaskVmExport, self).task_wait()
        self.execute_command(['xe', 'snapshot-uninstall', 'force=true', 'uuid=' + self.snapshot_uuid])
        return value

    def get_name(self):
        return '{0}-{1}'.format(self.task_name, self.vm_name)


class BareosFdXenServerClass(BareosFdTaskClass):
    plugin_name = 'xenserver'
    pool_conf_path = '/etc/xensource/pool.conf'

    @staticmethod
    def get_hostname():
        return socket.gethostname()

    def is_pool_master(self):
        with open(self.pool_conf_path, 'r') as fin:
            data = fin.read()
        return data == 'master'

    def prepare_tasks(self):
        self.tasks = list()

        if self.config.get_boolean('host_backup', True):
            self.tasks.append(TaskHostBackup(BareosFdXenServerClass.get_hostname()))

        if self.config.get_boolean('pool_dump_database', True) and self.is_pool_master():
            self.tasks.append(TaskPoolDumpDatabase())

        for vm in self.config.get_list('vms'):
            task = TaskSnapshotExport(vm) if self.config.get_boolean('use_snapshot', True) else TaskVmExport(vm)
            self.tasks.append(task)
