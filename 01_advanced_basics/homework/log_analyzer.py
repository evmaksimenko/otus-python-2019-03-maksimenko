#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import configparser
import logging
import sys

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

log_format = '%(filename)s[LINE:%(lineno)3d]# %(levelname)-8s %(message)s'

logging.basicConfig(format=log_format, level=logging.ERROR)

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def parse_cli_args():
    parser = argparse.ArgumentParser(description='nginx log analyzer.')
    parser.add_argument('--config', action='store', help='path to config file')
    return parser.parse_args()


def update_config():
    config_path = parse_cli_args().config
    if config_path:
        if os.path.isfile(config_path):
            config = configparser.ConfigParser()
            try:
                if config.read(config_path)[0] != config_path:
                    logging.error('Error parsing config file')
                    sys.exit(1)
                else:
                    print({c: config['DEFAULT'][c] for c in config['DEFAULT']})
            except configparser.Error as err:
                logging.error('Error parsing config file')
                logging.error(err)
                sys.exit(1)
        else:
            logging.error('Config file not found')
    print(config_path)


def main():
    update_config()
    # print(parse_cli_args())



if __name__ == "__main__":
    main()