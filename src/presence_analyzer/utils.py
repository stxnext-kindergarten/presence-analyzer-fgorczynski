# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
from json import dumps
from functools import wraps
from datetime import datetime
from flask import Response
from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name

DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
DEFAULT_DATETIME = str(datetime(1, 1, 1, 0, 0, 0))


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}
    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_user_avgs_weekday(items):
    """
    Get items collection.
    Return averages for every week days.
    """
    def create_datetime(hours, minutes, seconds):
        """
        Create datetime object for specified hours/minutes/seconds.

        :hours int
        :minutes int
        :seconds int
        """
        return datetime(1, 1, 1, hours, minutes, seconds)

    def build_days():
        """
        Build days dictionary with start/end statistics.
        """
        days = {day: {'starts': 0, 'ends': 0, 'count': 0} for day in DAYS}
        for date in items:
            start = items[date]['start']
            end = items[date]['end']
            weekday = date.weekday()
            days[DAYS[weekday]]['starts'] += seconds_since_midnight(start)
            days[DAYS[weekday]]['ends'] += seconds_since_midnight(end)
            days[DAYS[weekday]]['count'] += 1
        return days

    def build_result(days):
        """
        Build result list using days dictionary.

        :days Dictrionary with user specified working hours.
        """
        result = [[], [], [], [], [], [], []]
        for day, stats in days.iteritems():
            index = DAYS.index(day)
            result[index].append(day)
            if stats.get('count'):
                start = int(round(stats.get('starts')) / stats.get('count'))
                end = int(round(stats.get('ends')) / stats.get('count'))
                start_hour, start_minute, start_second = seconds_to_time(start)
                end_hour, end_minute, end_second = seconds_to_time(end)
                start = create_datetime(start_hour, start_minute, start_second)
                end = create_datetime(end_hour, end_minute, end_second)
                result[index].append(str(start))
                result[index].append(str(end))
            else:
                result[index].append(DEFAULT_DATETIME)
                result[index].append(DEFAULT_DATETIME)
        # remove empty days (working and nonworking days)
        result = [day for day in result if day[1] != day[2]]
        return result
    days = build_days()
    result = build_result(days)
    return result


def seconds_to_time(seconds):
    """
    Get number of seconts since midnight.
    Return hours, minute, seconds representation.
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return (hours, minutes, seconds)


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
