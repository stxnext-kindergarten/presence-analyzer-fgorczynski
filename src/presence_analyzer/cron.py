# -*- encoding: utf-8 -*-
"""
Cron tasks
"""
import os.path
import time
import urllib2

from presence_analyzer.config import (
    BASE_XML_FILE,
    BASE_XML_URL,
)

SECOND_IN_DAY = 86400  # seconds in one day


def file_is_present():
    u"""
    Check if data file is present.
    """
    return (
        os.path.exists(BASE_XML_FILE)
        and os.path.getctime(BASE_XML_FILE) >= time.time() - SECOND_IN_DAY
    )


def update_users_source():
    u"""
    Download remote XML with users data.
    """
    # update only if local file is older than 1 day
    if not file_is_present():
        source_file = urllib2.urlopen(BASE_XML_URL)
        destination_file = open(BASE_XML_FILE, "w")
        data = source_file.read()
        destination_file.write(data)
        destination_file.close()
        source_file.close()
        return data


if __name__ == '__main__':
    update_users_source()
