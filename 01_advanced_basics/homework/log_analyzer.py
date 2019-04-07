#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
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

LogFile = namedtuple('LogFile', ['path', 'name', 'date', 'ext'])

LOG_RE = re.compile("^nginx-access-ui[.]log-([0-9]{8})([.]gz)?$")

LOG_FORMAT = '[%(asctime)s] %(levelname).1s %(message)s'

REP_NAME_TMP = 'report-{:4d}.{:02d}.{:02d}.html'


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
    logs = [f for f in file_list if LOG_RE.match(f)]
    logs.sort(reverse=True)
    if logs != []:
        log_name = logs[0]
        log_path = os.path.join(log_dir, log_name)
        m = LOG_RE.match(log_name)
        log_ext = m.group(2) if m.group(2) else ''
        log_date = datetime.strptime(m.group(1), '%Y%m%d')
        return LogFile(log_path, log_name, log_date, log_ext)
    else:
        return None


def parse_line(line):
    return '1'


def read_log(log_file, parse_fn=parse_line):
    open_fn = gzip.open if log_file.ext == '.gz' else open
    total = processed = 0
    with open_fn(log_file.path, 'rt') as log:
        for line in log:
            parsed_line = parse_fn(line)
            total += 1
            if parsed_line:
                processed += 1
                yield parsed_line
    print("%s of %s lines processed" % (processed, total))


def main():
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    config_path = cli_config_path()
    if config_path:
        if not update_config(config, config_path):
            logging.error('Error updating config from file')
            sys.exit(1)

    log_dir = config.get('LOG_DIR', '')
    if not log_dir or not os.path.isdir(log_dir):
        logging.error("Logs directory doesn't exists")
        sys.exit(1)

    log_file = get_last_log(log_dir)
    if not log_file:
        logging.info('Log files not found in log directory')
        sys.exit(0)
    logging.info('Found last log file ' + log_file.name)

    report_dir = config.get('REPORT_DIR', '')
    if report_dir != '':
        if not os.path.isdir(report_dir):
            logging.error("Report directory doesn't exists")
            sys.exit(1)
        ldate = log_file.date
        report_file = REP_NAME_TMP.format(ldate.year, ldate.month, ldate.day)
        if os.path.exists(os.path.join(report_dir, report_file):
            logging.info('Report already exists')
            sys.exit(0)

    fname = None if report_dir == '' else report_dir
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO, filename=fname)


if __name__ == "__main__":
    main()
