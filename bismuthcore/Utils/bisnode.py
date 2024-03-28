"""
A Node test script to be used for dev
"""

import sys
import argparse
import logging
import tornado.log
from os import path
from concurrent_log_handler import (
    ConcurrentRotatingFileHandler,
)  # pip install concurrent-log-handler

sys.path.append(
    "../"
)  # This is a hack in dev context to use the local bismuthcore code.
from bismuthcore.bismuthconfig import BismuthConfig
from bismuthcore.bismuthcore import BismuthNode


__version__ = "0.0.3"


def get_logger():
    """Setup and tune the application logger"""
    app_log = logging.getLogger("tornado.application")
    tornado.log.enable_pretty_logging()
    # TODO: user dir
    logfile = path.abspath("node.log")
    # Rotate log after reaching 512K, keep 5 old copies.
    rotate_handler = ConcurrentRotatingFileHandler(logfile, "a", 512 * 1024, 5)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    rotate_handler.setFormatter(formatter)
    app_log.addHandler(rotate_handler)
    return app_log


if __name__ == "__main__":
    # Handle command line arguments
    parser = argparse.ArgumentParser(description="Bismuth Dev Node")
    parser.add_argument(
        "-v", "--verbose", action="count", default=False, help="Force to be verbose."
    )
    parser.add_argument(
        "-l",
        "--level",
        type=str,
        default="WARNING",
        help="Force Log level: DEBUG, INFO, WARNING, ERROR",
    )
    parser.add_argument(
        "-c", "--config", type=str, default="", help="Use that specific config file"
    )
    args = parser.parse_args()

    app_log = get_logger()

    # Init config instance
    config = BismuthConfig(args.config, app_log=app_log, verbose=args.verbose)
    # And override with command line arguments
    if args.level:
        config.log_level = args.level
    logging.basicConfig(level=config.get("log_level"))
    app_log.setLevel(config.get("log_level"))

    # Create and run the node.
    node = BismuthNode(
        app_log=app_log,
        verbose=args.verbose,
        config=config,
        com_backend_class_name="TornadoBackend",
    )
    node.run()
