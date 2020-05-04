#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import subprocess
import sys

DB_DIR = '/home/bar/dbs'
LOG_DIR = '/home/bar/logs'
TMP_DIR = '/home/bar/tmp'

DOWNLOAD_CMD = 'curl %%(link)s --output %s/%%(dbname)s' % DB_DIR
RESTORE_CMD = 'db_restore.py +f %s/%%(dbname)s +d %%(dbname)s' % DB_DIR
MIGRATE_CMD = 'upgrade.py --contract=%%(contract)s --target=%%(target)s --dbname=%%(dbname)s 2>&1 | tee %s/log_%%(dbname)s.txt' % LOG_DIR
MIGRATE__WITH_CONTRACT_CMD = 'upgrade.py --contract=%%(contract)s --target=%%(target)s --dbname=%%(dbname)s 2>&1 | tee %s/log_%%(dbname)s.txt' % LOG_DIR

def parse_command_line():
    """
    Parse command-line arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-l', '--http-link',
        help="HTTP database link",
        action='store',
        dest="db_link",
        default=None)

    parser.add_argument(
        '-r', '--request-id',
        help=("The request ID"),
        action='store',
        dest="request_id",
        required=True)

    parser.add_argument(
        '-c', '--contract-id',
        help=("The contract ID"),
        action='store',
        dest="contract",
        default=None)

    parser.add_argument(
        '-t', '--target',
        help=("The target version"),
        action='store',
        dest="target",
        default=None)

    return parser.parse_args()

def _cmd(command):
    """ launch a command using subprocess """
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as err:
        print(str(err))
        return False

    return True

def download_db(link, name, request_id):
    """ download the database archive from the web """

    print('Downloading database for request %s ...' % request_id)
    return _cmd(DOWNLOAD_CMD % {'link': link, 'dbname': name})

def restore_db(name):
    """ load the database archive into a PostgreSQL database """

    print('Restoring the database ...')
    return _cmd(RESTORE_CMD % {'dbname': name})

def migrate(name, target, contract):
    """ start the migration of the database to the target version """

    infos = {
        'contract': contract,
        'target': target,
        'dbname': name
    }

    print('Migrating the database (name: %(dbname)s target: %(target)s contract:%(contract)s)' % infos)

    if contract:
        return _cmd(MIGRATE__WITH_CONTRACT_CMD % infos)
    return _cmd(MIGRATE_CMD % infos)

def main():
    args = parse_command_line()

    dbname = "bar_%s" % args.request_id

    if args.db_link:
        if not download_db(args.db_link, dbname, args.request_id):
            return -1

        if not restore_db(dbname):
            return -2

    if args.target:
        if not migrate(dbname, args.target, args.contract):
            return -3

    return 0

if __name__ == "__main__":
    sys.exit(main())
