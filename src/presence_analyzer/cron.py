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

DAY_IN_SECONDS = 86400  # seconds in one day


def is_file_younger_than_one_day():
    u"""
    Check if data file is present.
    """
    return (
        os.path.exists(BASE_XML_FILE)
        and os.path.getctime(BASE_XML_FILE) >= time.time() - DAY_IN_SECONDS
    )


def update_users_source():
    u"""
    Download remote XML with users data.
    """
    if not is_file_younger_than_one_day():
        source_file = urllib2.urlopen(BASE_XML_URL)
        destination_file = open(BASE_XML_FILE, "w")
        data = source_file.read()
        destination_file.write(data)
        destination_file.close()
        source_file.close()
        return data


if __name__ == '__main__':
    update_users_source()
