"""
A Node test script to be used for dev
"""

import sys
import logging
import tornado.log
from os import path
# pip install ConcurrentLogHandler
from cloghandler import ConcurrentRotatingFileHandler


sys.path.append('../bismuthcore')
from bismuthconfig import BismuthConfig
from bismuthcore import BismuthNode


__version__ = '0.0.1'


if __name__ == "__main__":
    app_log = logging.getLogger("tornado.application")
    tornado.log.enable_pretty_logging()
    # TODO: user dir
    logfile = path.abspath('node.log')
    # Rotate log after reaching 512K, keep 5 old copies.
    rotate_handler = ConcurrentRotatingFileHandler(logfile, 'a', 512 * 1024, 5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    rotate_handler.setFormatter(formatter)
    app_log.addHandler(rotate_handler)

    config = BismuthConfig(app_log=app_log, verbose=True)
    logging.basicConfig(level=config.get('log_level'))

    node = BismuthNode(app_log=app_log, verbose=True, config=config)

    node.run()
