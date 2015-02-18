"""
Cron tasks
"""
import os.path
import urllib2
import time
from presence_analyzer.config import (
    BASE_XML_FILE,
    BASE_XML_URL,
)

DAY = 86400  # seconds in one day


def update_users_source():
    """
    Download remote XML with users data.
    """
    # update only if local file is older than 1 day
    if not os.path.exists(BASE_XML_FILE) \
            or os.path.getctime(BASE_XML_FILE) < time.time() - DAY:
        source_file = urllib2.urlopen(BASE_XML_URL)
        destination_file = open(BASE_XML_FILE, "w")
        data = source_file.read()
        destination_file.write(data)
        destination_file.close()
        source_file.close()
        return data


# def get_user_avatar_url():
#     """
#     Get unique user ID
#
#     Return URL for user avatar
#     """
#     source = open(BASE_XML_FILE, 'r')
#     users = etree.fromstring(source.read())
#     source.close()
#     server = users[0]
#     server = server[2].text + "://" + server[0].text + ":" + server[1].text
#     for user in users[1]:
#         return server + user[0].text
#     return ""

if __name__ == '__main__':
    update_users_source()
