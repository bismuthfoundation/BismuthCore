"""
A Node test script to be used for dev
"""

import sys
import argparse
import logging
import tornado.log
from os import path
# pip install ConcurrentLogHandler
from cloghandler import ConcurrentRotatingFileHandler


sys.path.append('../')
from bismuthcore.bismuthconfig import BismuthConfig
from bismuthcore.bismuthcore import BismuthNode


__version__ = '0.0.1'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bismuth Dev Node')
    parser.add_argument("-v", "--verbose", action="count", default=False, help='Force to be verbose.')
    parser.add_argument("-l", "--level", type=str, default='WARNING', help='Force Log level: DEBUG, INFO, WARNING, ERROR')
    args = parser.parse_args()
    app_log = logging.getLogger("tornado.application")
    tornado.log.enable_pretty_logging()
    # TODO: user dir
    logfile = path.abspath('node.log')
    # Rotate log after reaching 512K, keep 5 old copies.
    rotate_handler = ConcurrentRotatingFileHandler(logfile, 'a', 512 * 1024, 5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    rotate_handler.setFormatter(formatter)
    app_log.addHandler(rotate_handler)

    config = BismuthConfig(app_log=app_log, verbose=args.verbose)
    if args.level:
        config.log_level = args.level
    logging.basicConfig(level=config.get('log_level'))
    app_log.setLevel(config.get('log_level'))

    node = BismuthNode(app_log=app_log, verbose=True, config=config, com_backend_class_name='TornadoBackend')
    node.run()
