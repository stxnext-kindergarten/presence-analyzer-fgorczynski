# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
import logging
from flask import redirect, abort
from lxml import etree
from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    mean,
    group_by_weekday,
    group_user_avgs_weekday,
)
from presence_analyzer.config import (
    BASE_XML_FILE,
)
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/static/presence_weekday.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    xmlfile = open(BASE_XML_FILE, 'r')
    root = etree.fromstring(xmlfile.read())  # pylint: disable=no-member
    xmlfile.close()

    def get_username(i):
        """
        Get user ID

        Return user name from XML file or default string.
        """
        user = root[1].xpath("user[@id='{}']".format(i))
        if user:
            return user[0][1].text
        return "User {}".format(i)

    data = get_data()
    return [
        {'user_id': i, 'name': get_username(i)}
        for i in data.keys()
    ]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def start_end_presence_view(user_id):
    """
    Returns average presence time.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)
    result = group_user_avgs_weekday(data[user_id])
    return result
