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
        print(f'{host}: failed to obtain FPGA ID')
        raise

def read_devid(host, opts):
    try:
        shell = SshShell(host, opts.ssh_port, opts.ssh_user, opts.ssh_pass)
        shell.connect()

        cmd = ' | '.join([
            'grep dev_id /config/anthill.json',
            'sed \'s/.*"dev_id":\ "\(.*\)"/\\1/\''
        ])

        output = shell.execute(cmd)

        if output != '':
            print(f'{host}: devid: {output}', end = '')
        else:
            print(f'{host}: no device id')

        shell.disconnect()
    except ShellError:
        print(f'{host}: failed to obtain device id')
        raise

def change_ssh_passwd(host, opts):
    try:
        shell = SshShell(host, opts.ssh_port, opts.ssh_user, opts.ssh_pass)
        shell.connect()

        cmd = ' | '.join([
            f'printf "{opts.ssh_new_pass}\\n{opts.ssh_new_pass}"',
            f'passwd {opts.ssh_user}'
        ])

        shell.execute(cmd)
        shell.execute('mv /etc/shadow /config/shadow')
        shell.execute('ln -s /config/shadow /etc/shadow')
        shell.execute('sync')
        print(f'{host}: Password changed successfully!')
        shell.disconnect()
    except ShellError:
        print(f'{host}: failed to change the password')
        raise

def find_mode_on(host, opts):
    try:
        shell = SshShell(host, opts.ssh_port, opts.ssh_user, opts.ssh_pass)
        shell.connect()

        shell.execute('screen -d -m /usr/sbin/led.sh')
        print(f'{host}: Leds enabled')
        shell.disconnect()
    except ShellError:
        print(f'{host}: failed to enable led blinking')

def find_mode_off(host, opts):
    try:
        shell = SshShell(host, opts.ssh_port, opts.ssh_user, opts.ssh_pass)
        shell.connect()

        shell.execute('killall -9 led.sh')
        print(f'{host}: Leds disabled')
        shell.disconnect()
    except ShellError:
        print(f'{host}: failed to disable led blinking')

def uninstall_anthill(host, opts):
    try:
        shell = SshShell(host, opts.ssh_port, opts.ssh_user, opts.ssh_pass)
        shell.connect()

        path = os.path.join(os.path.dirname(__file__),
                            'resources', 'uninstall.sh')

        with open(path, 'rb') as uninstaller:
            rpath = '/tmp/uninstall.sh'
            shell.upload(uninstaller, rpath)
            shell.execute(f'chmod a+x {rpath}')
            output = shell.execute(rpath)
            print(f'{host}:\n{output}', end = '')
            shell.rm(rpath)

        shell.disconnect()
    except ShellError:
        print(f'{host}: failed to remove Anthill integration')