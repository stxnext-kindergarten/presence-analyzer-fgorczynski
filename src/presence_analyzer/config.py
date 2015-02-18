"""
Application configuration file.
"""
import os.path

BASE_XML_URL = 'http://sargo.bolt.stxnext.pl/users.xml'
BASE_XML_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data',
)
BASE_XML_FILE = os.path.join(
    BASE_XML_DIR, 'users_data.xml'
)
TEST_XML_FILE = os.path.join(
    BASE_XML_DIR, 'test_users_data.xml'
)
