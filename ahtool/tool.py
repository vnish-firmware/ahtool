import os
import sys
import time

from ahtool.shells import SshShell, ShellError

def read_fpgaid(host, opts):
    try:
        shell = SshShell(host, opts.ssh_port, opts.ssh_user, opts.ssh_pass)
        shell.connect()

        path = os.path.join(os.path.dirname(__file__),
                            'resources', 'fpgaid')

        with open(path, 'rb') as fpgaid:
            rpath = '/tmp/fpgaid'
            shell.upload(fpgaid, rpath)
            shell.execute(f'chmod a+x {rpath}')
            output = shell.execute(rpath)
            print(f'{host}: {output}', end = '')
            shell.rm(rpath)

        shell.disconnect()
    except ShellError:
        pint(f'{host}: failed to obtain FPGA ID')

def read_devid(host, opts):
    try:
        shell = SshShell(host, opts.ssh_port, opts.ssh_user, opts.ssh_pass)
        shell.connect()

        cmd = ' | '.join([
            'grep dev_id /config/anthill.json',
            'sed \'s/.*"dev_id":\ "\(.*\)"/\\1/\''
        ])

        output = shell.execute(cmd)
        print(f'{host}: devid: {output}', end = '')
        shell.disconnect()
    except ShellError:
        printf(f'{host}: failed to obtain device id')