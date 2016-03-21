#!/usr/bin/env python
"""
The main pyTransmission-RSS application with all the bells and whistles.
"""

import logging
from transmissionrss.modules import config, rpc, rss

LOGGER = logging.getLogger('pyTransmission-RSS')
logging.basicConfig(level=logging.INFO)

LOGGER.info("Starting up.")
