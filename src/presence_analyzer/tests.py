# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import datetime
import json
import os.path
import unittest
from presence_analyzer import (  # pylint: disable=unused-import
    main,
    utils,
    views,
)

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
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
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

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


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
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
            ['Tue', '0001-01-01 09:39:05', '0001-01-01 17:59:52'],
            ['Wed', '0001-01-01 09:19:52', '0001-01-01 16:07:37'],
            ['Thu', '0001-01-01 10:48:46', '0001-01-01 17:23:51']
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
