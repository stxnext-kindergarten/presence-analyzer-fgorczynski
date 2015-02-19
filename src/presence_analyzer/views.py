# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import abort
import flask_mako as fmako  # pylint: disable=unused-import
from flask_mako import render_template
from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    mean,
    group_by_weekday,
    group_user_avgs_weekday,
)

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def weekday():
    """
    Renders Presence by weekday page.
    """
    return render_template('presence_weekday.html')


@app.route('/mean-time')
def mean_time():
    """
    Renders Presence mean time page.
    """
    return render_template('mean_time_weekday.html')


@app.route('/start-end')
def startend():
    """
    Renders Presence start-end page.
    """
    return render_template('presence_start_end.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
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
