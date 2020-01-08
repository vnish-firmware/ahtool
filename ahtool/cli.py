import concurrent.futures
import traceback

import click
import netaddr

from ahtool.tool import read_fpgaid, read_devid, change_ssh_passwd


class Options:
    def __init__(self):
        self.miners = []


def load_miners_from_file(path):
    miners = []
    with open(path, 'r') as f:
        for addr in f:
            if len(addr) < 6 or addr.startswith('#'):
                continue
            miners.append(addr)
    return miners


pass_options = click.make_pass_decorator(Options, ensure=True)


@click.group()
@click.option('--tasks', default=10, metavar='TASKS',
              help='Number of parallel tasks')
@click.option('--ssh-user', default='root', metavar='USER',
              help='The user name used for SSH authentication')
@click.option('--ssh-pass', default='admin', metavar='PASS',
              help='The password used for SSH authentication')
@click.option('--ssh-port', default=22, metavar='PORT',
              help='The port used for SSH connections')
@click.option('--ssh-new-pass', default='s3cr3t', metavar='NEW_PASS',
              help='New SSH password (default is s3cr3t)')
@click.option('--ip', metavar='MINER',
              help='The miner IP address or range of IP addresses')
@click.option('--ip-list', metavar='MINERS',
              help='The file containing a list of miner IP addresses')
@pass_options
def cli(opts, tasks, ssh_user, ssh_pass, ssh_port, ssh_new_pass, ip, ip_list):
    """Anthill Farm Tool"""
    opts.tasks = tasks
    opts.ssh_user = ssh_user
    opts.ssh_pass = ssh_pass
    opts.ssh_port = ssh_port
    opts.ssh_new_pass = ssh_new_pass

    if ip_list is not None:
        opts.miners = load_miners_from_file(ip_list)

    if ip is not None:
        if '-' in ip:
            ip_range = ip.split('-', 1)
            for _ip in netaddr.iter_iprange(ip_range[0], ip_range[1]):
                opts.miners.append(str(_ip))
        else:
            opts.miners.append(ip)

    if len(opts.miners) == 0:
        click.get_current_context().fail(
            'You need to specify at least one miner!')


def process(miners, opts, func):
    print('----------------------------------------')
    print('    Anthill Tool v1.0.0                 ')
    print('----------------------------------------')

    total = len(miners)
    succeeded = 0
    failed = 0

    with open('anthill-tool.log', 'w') as log:
        with concurrent.futures.ThreadPoolExecutor(opts.tasks) as executor:
            tasks = [executor.submit(func, m, opts) for m in miners]
            try:
                for task in concurrent.futures.as_completed(tasks):
                    try:
                        result = task.result()
                        succeeded += 1
                    except:
                        traceback.print_exc(file=log)
                        failed += 1
            except KeyboardInterrupt:
                executor._threads.clear()
                concurrent.futures.thread._threads_queues.clear()
                print('\nAborted!')

    print('----------------------------------------')
    print('    Summary                             ')
    print('----------------------------------------')
    print(f'Total: {total}')
    print(f'Succeeded: {succeeded}')
    print(f'Failed: {failed}')
    print('----------------------------------------')

    if failed > 0:
        print('Please review anthill-tool.log file to find the problems')


@cli.command()
@pass_options
def fpgaid(opts):
    """Obtain FPGA ID from the miner(s)"""
    process(opts.miners, opts, read_fpgaid)

@cli.command()
@pass_options
def devid(opts):
    """Obtain device unique id from the miner(s)"""
    process(opts.miners, opts, read_devid)

@cli.command()
@pass_options
def change_passwd(opts):
    """Change the current SSH password"""
    process(opts.miners, opts, change_ssh_passwd)

if __name__ == '__main__':
    cli()

