# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import datetime
import json
from lxml import etree
import os.path
import unittest
from presence_analyzer import (  # pylint: disable=unused-import
    main,
    utils,
    views,
)
from presence_analyzer.main import app
from presence_analyzer.utils import jsonify

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)
TEST_WRONG_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data',
    'test_wrong_data.csv'
)
TEST_EMPTY_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data',
    'test_empty_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'Maciej Z.'})

    def test_start_end_presence_correct(self):
        """
        Test average user presence by weekday - correct data.
        """
        # test for user with ID - user exists
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(
            resp.status_code,
            200,
            msg="Average user presence - Correct HTTP return."
        )
        self.assertEqual(
            resp.content_type,
            'application/json',
            msg="Average user presence - Wrong content type."
        )

    def test_start_end_presence_wrong(self):
        """
        Test average user presence by weekday - incorrect data.
        """
        resp = self.client.get('/api/v1/presence_start_end')
        self.assertEqual(
            resp.status_code,
            404,
            msg="Average user presence - Page not found."
        )
        self.assertEqual(
            resp.content_type,
            'text/html',
            msg="Average user presence - Wrong content type."
        )

        # test for user with ID - user not exists
        resp = self.client.get('/api/v1/presence_start_end/9999')
        self.assertEqual(
            resp.status_code,
            404,
            msg="Average user presence - User with specified ID not found."
        )
        self.assertEqual(
            resp.content_type,
            'text/html',
            msg="Average user presence - Wrong content type."
        )

    def test_mean_time_weekday_view(self):
        """
        JSON response of mean time weekday for specified user.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')

        # user with specified user_id - wrong param type - does not exist
        resp = self.client.get('/api/v1/mean_time_weekday/some-text')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')

        # user with specified user_id does not exist
        resp = self.client.get('/api/v1/mean_time_weekday/999')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')

        # user with specified user_id exist
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertEqual(data[0][0], u'Mon')
        self.assertTrue(isinstance(data[1][0], basestring))

    def test_presence_weekday_view(self):
        """
        JSON response of presence weekday for specified user.
        """
        # no user_id parameter defined
        resp = self.client.get('/api/v1/presence_weekday/')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')

        # user with specified user_id - wrong param type - does not exist
        resp = self.client.get('/api/v1/presence_weekday/some-text')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')

        # user with specified user_id does not exist
        resp = self.client.get('/api/v1/presence_weekday/999')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')

        # user with specified user_id exist
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertEqual(data[0], [u'Weekday', u'Presence (s)'])
        self.assertTrue(isinstance(data[1][0], basestring))
        self.assertTrue(isinstance(data[1][1], int))


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    @classmethod
    def _sample_data(cls):
        """
        Return sample data object:

        {
            'user_id': {
                datetime.date(2013, 10, 1): {
                    'start': datetime.time(9, 0),
                    'end': datetime.time(17, 30)
                }
            }
        }
        """
        return {
            'user_id': {
                str(datetime.date(2013, 10, 1)): {
                    'start': str(datetime.time(9, 0, 0)),
                    'end': str(datetime.time(17, 30, 0)),
                },
            }
        }

    @classmethod
    @jsonify
    def _sample_data_jsonified(cls):  # pylint disable=no-self-use
        """
        Return sample data object:

        {
            'user_id':{
                datetime.date(2013, 10, 1): {
                    'start': datetime.time(9, 0),
                    'end': datetime.time(17, 30)
                }
            }
        }
        """
        return {
            'user_id': {
                str(datetime.date(2013, 10, 1)): {
                    'start': str(datetime.time(9, 0, 0)),
                    'end': str(datetime.time(17, 30, 0)),
                },
            }
        }

    @classmethod
    def _sample_user_data(cls):
        """
        Return sample user fixture data.
        """
        return {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }

    def test_jsonify(self):
        """
        Test for valid JSON return.
        """
        fixture = self._sample_data()
        self.assertIsInstance(fixture, dict)
        self.assertGreater(len(fixture), 0)

        jsonified = self._sample_data_jsonified()
        self.assertIsInstance(jsonified.data, str)
        self.assertEqual(jsonified.status_code, 200)
        self.assertEqual(jsonified.content_type, 'application/json')

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        # correcy portion of data
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_group_user_avgs_weekday(self):
        """
        Test valid object return with user average working hours for whole
        week.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        result = utils.group_user_avgs_weekday(data[10])
        expected = [
            ('Tue', '0001-01-01 09:39:05', '0001-01-01 17:59:52'),
            ('Wed', '0001-01-01 09:19:52', '0001-01-01 16:07:37'),
            ('Thu', '0001-01-01 10:48:46', '0001-01-01 17:23:51'),
        ]
        self.assertItemsEqual(result, expected, msg="Wrong dates for user 10.")

    def test_seconds_to_time(self):
        """
        Test seconds since midnight to time conversion.
        """
        self.assertItemsEqual(
            utils.seconds_to_time(37230),
            (10, 20, 30),
            msg="Incorrect conversion from seconds to time representation."
        )

        tmp_data = app.config['DATA_CSV']

        # empty data
        app.config.update({'DATA_CSV': TEST_EMPTY_DATA_CSV})
        data = utils.get_data()
        self.assertEqual(len(data[10]), 3)
        self.assertEqual(len(data[11]), 4)

        # wrong data fixtures
        app.config.update({'DATA_CSV': TEST_WRONG_DATA_CSV})
        data = utils.get_data()
        self.assertEqual(len(data[10]), 2)
        self.assertEqual(len(data[11]), 5)

        # recover valid data
        main.app.config.update({'DATA_CSV': tmp_data})

    def test_group_by_weekday(self):
        """
        Test grouping by weekday.
        """
        self.assertTrue(
            utils.group_by_weekday([]),
            msg="Wrong list or type for empty parameter."
        )
        self.assertEquals(
            len(utils.group_by_weekday([])),
            7,
            msg="Wrong empty item list elements."
        )

        data = self._sample_user_data()
        self.assertEquals(
            len(utils.group_by_weekday(data)),
            7,
            msg="Wrong item list elements."
        )
        self.assertEquals(
            utils.group_by_weekday(data),
            [[], [30600], [29700], [], [], [], []],
            msg="Wrong weekday values."
        )

    def test_seconds_since_midnight(self):
        """
        Test seconds since midnight.
        """
        time_fixture = datetime.time(14, 30)
        self.assertEqual(utils.seconds_since_midnight(time_fixture), 52200)
        time_fixture = datetime.time(0, 0)
        self.assertEqual(utils.seconds_since_midnight(time_fixture), 0)

    def test_interval(self):
        """
        Test time interval.
        """
        # start < end
        start = datetime.time(9, 30)
        end = datetime.time(12, 30)
        self.assertEqual(utils.interval(start, end), 10800)  # 3 hours

        # start == end
        start = datetime.time(10, 45)
        end = datetime.time(10, 45)
        self.assertEqual(utils.interval(start, end), 0)  # 0 hours

        # start > end
        start = datetime.time(14, 45)
        end = datetime.time(10, 45)
        self.assertEqual(utils.interval(start, end), - 14400)  # -4 hours

    def test_mean(self):
        """
        Test mean.
        """
        self.assertEqual(utils.mean([]), 0)
        self.assertEqual(utils.mean([1.7, 2, 3.0, 4, 5.99999]), 3.339998)
        self.assertEqual(utils.mean([0.1, 0.3]), 0.2)

    @classmethod
    def _get_users_xml(cls):
        """
        :return: String with sample XML data.
        """
        return etree.fromstring(
            """
            <intranet>
                <server>
                    <host>intranet.stxnext.pl</host>
                    <port>443</port>
                    <protocol>https</protocol>
                </server>
                <users>
                    <user id="141">
                        <avatar>/api/images/users/141</avatar>
                        <name>Adam P.</name>
                    </user>
                    <user id="176">
                        <avatar>/api/images/users/176</avatar>
                        <name>Adrian K.</name>
                    </user>
                </users>
            </intranet>
            """
        )

    def test_update_users_source(self):
        """
        Check if remote XML exists and content type is XML.
        """
        data = self._get_users_xml()
        self.assertTrue(
            isinstance(
                data,
                etree._Element  # pylint: disable=protected-access
            ),
            msg="Wrong XML returned."
        )

    def test_cache_method(self):
        """
        Test if cache decorator return valid cache.
        """
        pass


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite

if __name__ == '__main__':
    unittest.main()
