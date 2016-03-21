#!/usr/bin/env python
"""
The main pyTransmission-RSS application with all the bells and whistles.
"""

import logging
import signal
import time

# Local modules
import transmissionrss.modules.config
import transmissionrss.modules.rpc
import transmissionrss.modules.rss

def transmissionrss_start():
    """
     This function starts pyTransmission-RSS. Please use responsibly.
    """
    logger = logging.getLogger('pyTransmission-RSS')
    logging.basicConfig(level=logging.INFO)

    logger.info("Starting up pyTransmission-RSS")

    logger.info("Reading configuration")
    conf = transmissionrss.modules.config.Config()

    if conf.is_default:
        logger.warning("The configuration file was not found")
        logger.warning("A default one has been written to ~/.transmission-rss.conf")
        logger.info("Shutting down")
        exit(0)

    # Set up signal handling
    def usr1_interrupt_handler(signum, frame):
        """
        Interrupt handler that is run when SIGUSR1 is recieved. Updates RSS feeds.
        """
        logger.info("SIGUSR1 recieved (%s, 0x%08X), updating feeds", signum, id(frame))
        for feed in feeds:
            did_update = feed.update(force=True)
            if did_update is True:
                items = feed.get_entries()
                logger.info("Feed for %s forcefully updated, %d new items", feed.url, len(items))
                for item in items:
                    worked, item_name = client.add_torrent(item['link'], folder=feed.folder)
                    if worked is True:
                        logger.info("Added item %s", item_name)
    signal.signal(signal.SIGUSR1, usr1_interrupt_handler)

    client = transmissionrss.modules.rpc.RPCClient(conf.connection['host'], conf.connection['port'],
                                                   conf.connection['path'],
                                                   conf.connection['login'])

    feeds = []
    for item in conf.feeds:
        feed = transmissionrss.modules.rss.Feed(**item)
        logger.info("Added feed %s", feed.url)
        feeds.append(feed)

    try:
        while True:
            for feed in feeds:
                did_update = feed.update()
                if did_update is True:
                    items = feed.get_entries()
                    logger.info("Feed for %s updated, %d new items", feed.url, len(items))
                    for item in items:
                        worked, item_name = client.add_torrent(item['link'], folder=feed.folder)
                        if worked is True:
                            logger.info("Added item %s", item_name)
            time.sleep(60*30)
    except (SystemExit, KeyboardInterrupt):
        logger.info("Shutting down")

if __name__ == '__main__':
    transmissionrss_start()
