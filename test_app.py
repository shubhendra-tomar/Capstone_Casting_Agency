import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import db, db_drop_and_create_all, setup_db, Movie, Actor
from auth import AuthError, requires_auth
from sqlalchemy import Column, String, Integer, DateTime
import logging

# define the global vars
database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

casting_assistant_token = os.getenv('CASTING_ASSISTANT_JWT')
casting_director_token = os.getenv('CASTING_DIRECTOR_JWT')
executive_producer_token = os.getenv('EXECUTIVE_PRODUCER_JWT')



# set authetification method to set headers
def setup_auth(role):
    if role == 'casting_assistant':
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(casting_assistant_token)
        }
    elif role == 'casting_director':
        return {
            "Content-Type": "application/json",
            'Authorization': 'Bearer {}'.format(casting_director_token)
        }
    elif role == 'executive_producer':
        return {
            "Content-Type": "application/json",
            'Authorization': 'Bearer {}'.format(executive_producer_token)
        }

# Test case class for the application
class CastingTestCase(unittest.TestCase):
    '''
        the setUp function.
        It will be executed before each test and is
        where you should initialize the app and test
        client, as well as any other context your tests
        will need. The Flask library provides a test
        client for the application, accessed as shown below.
    '''
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        # add TESTING to fix postgres freeze error
        self.app.config['TESTING'] = True  
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['DEBUG'] = True
        self.client = self.app.test_client
        self.database_path = database_path
        setup_db(self.app, self.database_path)

        self.new_actor1 = {
            "name": "Test Actor 1",
            "age": 24,
            "gender": "male"
        }
        self.new_actor2 = {
            "name": "Test Actor 2",
            "age": 24,
            "gender": "male"
        }
        self.new_movie1 = {
            "title": "The Tes Movie 1",
            "release_date": "2021-02-10"
        }
        self.new_movie2 = {
            "title": "The Tes Movie 2",
            "release_date": "2021-02-10"
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            db_drop_and_create_all()
            # Create some date to use it in the test
            self.client().post('/actors', json=self.new_actor1,
                            headers=setup_auth('executive_producer'))
            self.client().post('/movies', json=self.new_movie1,
                            headers=setup_auth('executive_producer'))


    #  This will run as long as setUp executes successfully,
    # regardless of test success.
    def tearDown(self):
        """ Executed after each test """
        pass


    # 1. Get the response by having the client make a request
    # 2. Use self.assertEqual to check the status code and all other
    # relevant operations.

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Actor Tests

    # test get actors end point
    def test_get_actors_casting_assistant(self):
        print("test 1")
        res = self.client().get('/actors',
                            headers=setup_auth("casting_assistant"))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actors']))

    def test_get_actors_casting_director(self):
        print("test 2")
        res = self.client().get('/actors',
                            headers=setup_auth("casting_director"))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actors']))

    def test_get_actors_executive_producer(self):
        print("test 3")
        res = self.client().get('/actors',
                            headers=setup_auth("executive_producer"))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actors']))

    def test_401_get_actor_fail(self):
        print("test 4")
        res = self.client().get('/actors', headers=setup_auth(''))
        self.assertEqual(res.status_code, 401)

    # test post actors end point
    def test_post_actor_casting_assistant(self):
        print("test 5")
        res = self.client().post('/actors', json=self.new_actor2,
                            headers=setup_auth('casting_assistant'))
        self.assertEqual(res.status_code, 403)

    def test_post_actor_casting_director(self):
        print("test 6")
        res = self.client().post('/actors', json=self.new_actor2,
                            headers=setup_auth('casting_director'))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actor']))

    def test_post_actor_executive_producer(self):
        print("test 7")
        res = self.client().post('/actors', json=self.new_actor2,
                            headers=setup_auth('executive_producer'))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actor']))

    def test_400_post_actors_fail(self):
        print("test 8")
        res = self.client().post('/actors', json={},
                            headers=setup_auth('casting_director'))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    # test patch actors end point
    def test_patch_actor_casting_assistant(self):
        print("test 9")
        res = self.client().patch('/actors/1', json={'age': 25},
                            headers=setup_auth('casting_assistant'))
        self.assertEqual(res.status_code, 403)

    def test_patch_actor_casting_director(self):
        print("test 10")
        res = self.client().post('/actors', json=self.new_actor2,
                            headers=setup_auth('executive_producer'))
        res = self.client().patch('/actors/2', json={'age': 25},
                            headers=setup_auth('casting_director'))
        data = json.loads(res.data)
        actor = Actor.query.filter_by(id=2).first()
        actor_age = actor.age
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(actor_age, 25)

    def test_patch_actor_executive_producer(self):
        print("test 11")
        res = self.client().post('/actors', json=self.new_actor2,
                            headers=setup_auth('executive_producer'))
        res = self.client().patch('/actors/2', json={'age': 26},
                            headers=setup_auth('executive_producer'))
        data = json.loads(res.data)
        actor = Actor.query.filter_by(id=2).first()
        actor_age = actor.age
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(actor_age, 26)

    def test_404_patch_actor_fail(self):
        print("test 12")
        res = self.client().patch('/actors/100', json={},
                            headers=setup_auth('executive_producer'))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # test delete actors end point
    def test_delete_actor_casting_assistant(self):
        print("test 13")
        res = self.client().delete('/actors/2',
                            headers=setup_auth('casting_assistant'))
        self.assertEqual(res.status_code, 403)

    def test_delete_actor_casting_director(self):
        print("test 14")
        res = self.client().post('/actors', json=self.new_actor2,
                            headers=setup_auth('executive_producer'))
        res = self.client().delete('/actors/2',
                            headers=setup_auth('casting_director'))
        data = json.loads(res.data)

        actor = Actor.query.filter_by(id=2).first()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        #self.assertEqual(int(data['deleted']), 2)

    def test_delete_actor_executive_producer(self):
        print("test 15")
        res = self.client().post('/actors', json=self.new_actor2,
                            headers=setup_auth('executive_producer'))
        res = self.client().delete('/actors/2',
                            headers=setup_auth('executive_producer'))
        data = json.loads(res.data)
        actor = Actor.query.filter_by(id=2).first()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        #self.assertEqual(int(data['deleted']), 2)

    def test_401_delete_actor_fail(self):
        print("test 16")
        res = self.client().delete('/actors/1', headers=setup_auth(''))
        self.assertEqual(res.status_code, 401)


    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Movie Tests

    # test get movies end point
    def test_get_movies_casting_assistant(self):
        print("test 17")
        res = self.client().get('/movies',
                            headers=setup_auth("casting_assistant"))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movies']))

    def test_get_movies_casting_director(self):
        print("test 18")
        res = self.client().get('/movies',
                            headers=setup_auth("casting_director"))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movies']))

    def test_get_movies_executive_producer(self):
        print("test 19")
        res = self.client().get('/movies',
                            headers=setup_auth("executive_producer"))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movies']))

    def test_401_get_movie_fail(self):
        print("test 20")
        res = self.client().get('/movies',
                            headers=setup_auth(''))
        self.assertEqual(res.status_code, 401)

    # test post movies end point
    def test_post_movie_casting_assistant(self):
        print("test 21")
        res = self.client().post('/movies', json=self.new_movie2,
                             headers=setup_auth('casting_assistant'))
        self.assertEqual(res.status_code, 403)

    def test_post_movie_casting_director(self):
        print("test 22")
        res = self.client().post('/movies', json=self.new_movie2,
                            headers=setup_auth('casting_director'))

        self.assertEqual(res.status_code, 403)

    def test_post_movie_executive_producer(self):
        print("test 23")
        res = self.client().post('/movies', json=self.new_movie2,
                            headers=setup_auth('executive_producer'))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movie']))

    def test_400_post_movies_fail(self):
        print("test 24")
        res = self.client().post('/movies', json={},
                            headers=setup_auth('executive_producer'))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    
    def test_409_post_movies_fail(self):
        print("test 25")
        res = self.client().post('/movies', json=self.new_movie1,
                            headers=setup_auth('executive_producer'))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 409)
        self.assertEqual(data['success'], False)

    # test patch movies end points
    def test_patch_movie_casting_assistant(self):
        print("test 26")
        res = self.client().patch('/movies/1', 
                            json={'title': 'updated_movie'},
                            headers=setup_auth('casting_assistant'))
        self.assertEqual(res.status_code, 403)

    def test_patch_movie_casting_director(self):
        print("test 27")
        res = self.client().patch('/movies/1',
                            json={'title': 'updated_movie1'},
                            headers=setup_auth('casting_director'))
        data = json.loads(res.data)
        movie = Movie.query.filter_by(id=1).first()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(movie.title, 'updated_movie1')

    def test_patch_movie_executive_producer(self):
        print("test 28")
        res = self.client().patch('/movies/1',
                            json={'title': 'updated_movie2'},
                            headers=setup_auth('executive_producer'))
        data = json.loads(res.data)
        movie = Movie.query.filter_by(id=1).first()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(movie.title, 'updated_movie2')

    def test_404_patch_movie_fail(self):
        print("test 29")
        res = self.client().patch('/movies/500', json={},
                            headers=setup_auth('executive_producer'))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # test delete movies end point
    def test_delete_movie_casting_assistant(self):
        print("test 30")
        res = self.client().delete('/movies/1',
                            headers=setup_auth('casting_assistant'))
        self.assertEqual(res.status_code, 403)

    def test_delete_movie_casting_director(self):
        print("test 31")
        res = self.client().delete('/movies/1',
                            headers=setup_auth('casting_director'))
        self.assertEqual(res.status_code, 403)

    def test_delete_movie_executive_producer(self):
        print("test 31")
        res = self.client().delete('/movies/1',
                            headers=setup_auth('executive_producer'))
        data = json.loads(res.data)
        movie = Movie.query.filter_by(id=1).first()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        #self.assertEqual(int(data['deleted']), 1)
        self.assertEqual(movie, None)

    def test_401_delete_movie_fail(self):
        print("test 32")
        res = self.client().delete('/movies/1', headers=setup_auth(''))
        self.assertEqual(res.status_code, 401)


# Run the test suite, by running python
# test_app.py from the command line.


if __name__ == "__main__":
    unittest.main()