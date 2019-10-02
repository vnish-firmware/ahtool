import time
import socket

import paramiko
from paramiko import AuthenticationException, SSHException
import scp

class ShellError(Exception):
    def __init__(self, host, message, e):
        super().__init__(f'{host}: {message}', e)


class SshShell:
    """Allows to execute remote commands and upload
    files with the help of SSH protocol"""

    def __init__(self, host, port, user, passwd):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd

    def connect(self):
        """Connects the shell to the remote host."""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            self.ssh.connect(self.host, self.port,
                             self.user, self.passwd, timeout = 20)
            self.scp = scp.SCPClient(self.ssh.get_transport())
        except (AuthenticationException, SSHException) as e:
            raise ShellError(self.host, 'Failed to connect the shell', e)

    def execute(self, cmd):
        """Executes a command on the remote host."""
        if self.ssh is None:
            raise ShellError(self.host, 'Shell not connected!', None)

        try:
            _, stdout, stderr = self.ssh.exec_command(cmd)
            return str(stdout.read(), 'utf-8')
        except SSHException as e:
            raise ShellError(
                self.host, 'Failed to execute remote command', e)

    def upload(self, file, path):
        """Uploads and stores the file under the specified path."""
        if self.scp is None:
            raise ShellError(self.host, 'Shell not connected!', None)

        self.scp.putfo(file, path)

    def rm(self, path):
        """Remotes the specified file."""
        self.execute(f'rm -f {path}')

    def disconnect(self):
        """Frees any allocated resources."""
        if self.scp is not None:
            self.scp.close()
        if self.ssh is not None:
            self.ssh.close()