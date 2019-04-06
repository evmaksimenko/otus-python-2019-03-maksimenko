#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import re
import sys

from collections import namedtuple
from datetime import datetime

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

LOG_RE = re.compile("^nginx-access-ui\.log-([0-9]{8})(\.gz)?$")

LogFile = namedtuple('LogFile', ['path', 'name', 'date', 'ext'])


def update_config(config, config_path):
    if not config_path:
        return False
    try:
        f = open(config_path, 'r')
        for line in f:
            arr = line.split()
            if len(arr) < 2:
                continue
            config[arr[0]] = arr[1]
        return True
    except FileNotFoundError:
        return False


def cli_config_path():
    if len(sys.argv) < 3:
        return None
    if sys.argv[1] == '--config':
        return sys.argv[2]


def get_last_log(log_dir):
    file_list = os.listdir(log_dir)
    if not file_list:
        return None
    logs = list(filter(lambda s: LOG_RE.match(s), file_list))
    logs.sort(reverse=True)
    if logs != []:
        log_name = logs[0]
        m = LOG_RE.match(log_name)
        log_ext = m.group(2) if m.group(2) else ''
        log_date = datetime.strptime(m.group(1), '%Y%m%d')
        return LogFile(log_dir, log_name, log_date, log_ext)
    else:
        return None


def main():
    config_path = cli_config_path()
    if config_path:
        if not update_config(config, config_path):
            print('Error updating config from file')
            sys.exit(1)

    log_dir = config.get('LOG_DIR', '')
    if not log_dir or not os.path.isdir(log_dir):
        print("Logs directory doesn't exists")
        sys.exit(1)

    log_file = get_last_log(log_dir)
    if not log_file:
        print('Log files not found in log directory')
        sys.exit(1)

    # report_dir = config.get('REPORT_DIR', '')
    # if not report_dir:
    #     pass
    # elif not os.path.isdir(report_dir):
    #     print("Report directory doesn't exists")
    #     sys.exit(1)

    # os.listdir()
    # logging.basicConfig(format='', level=logging.INFO)


if __name__ == "__main__":
    main()
