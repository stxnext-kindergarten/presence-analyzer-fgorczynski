# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils

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

    def test_mean_time_weekday_view(self):
        """
        JSON response of mean time weekday for specified user
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
        #import pdb; pdb.set_trace()
        self.assertEqual(len(data), 8)
        self.assertEqual(data[0], [u'Weekday', u'Presence (s)'])
        self.assertEqual(str(type(data[1][0])), "<type 'unicode'>")
        self.assertEqual(str(type(data[1][1])), "<type 'int'>")

    def test_presence_weekday_view(self):
        """
        JSON response of presence weekday for specified user
        """
        pass


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

    def test_jsonify(self):
        """
        Test for valid JSON return
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

    def test_group_by_weekday(self):
        """
        Grouping by weekday
        """
        pass

    def test_seconds_since_midnight(self):
        pass

    def test_interval(self):
        pass

    def test_mean(self):
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
