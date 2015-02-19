# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
import logging

from lxml import etree
from flask import abort
import flask_mako as fmako  # pylint: disable=unused-import

from presence_analyzer.config import BASE_XML_FILE
from presence_analyzer.main import app
from presence_analyzer.utils import (
    get_data,
    group_by_weekday,
    group_user_avgs_weekday,
    jsonify,
    mean,
)

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def weekday():
    """
    Renders Presence by weekday page.
    """
    return fmako.render_template('presence_weekday.html')


@app.route('/mean-time')
def mean_time():
    """
    Renders Presence mean time page.
    """
    return fmako.render_template('mean_time_weekday.html')


@app.route('/start-end')
def startend():
    """
    Renders Presence start-end page.
    """
    return fmako.render_template('presence_start_end.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    root = {}
    with open(BASE_XML_FILE, 'r') as xmlfile:
        root = etree.fromstring(xmlfile.read())  # pylint: disable=no-member

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
        (calendar.day_abbr[wday], mean(intervals))
        for wday, intervals in enumerate(weekdays)
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
        (calendar.day_abbr[wday], sum(intervals))
        for wday, intervals in enumerate(weekdays)
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
