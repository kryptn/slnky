import unittest

from flask import Flask
from flask.ext.testing import TestCase

from app import db, Links


class SlnkyTest(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class DatabaseTest(SlnkyTest):

    url = 'test_url'

    def test_empty_database(self):
        self.assertEqual(Links.query.count(), 0)

    def test_add_url(self):
        result = Links.get_or_create(self.url)
        self.assertEqual(result.url, self.url) # Adding the first url

        result_dupe = Links.get_or_create(self.url)
        self.assertEqual(result_dupe.id, result.id) # Adding duplicate URL

        

if __name__ == '__main__':
    unittest.main()