import unittest
import os
import json
from urlparse import urlparse

# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "posts.config.TestingConfig"

from posts import app
from posts import models
from posts.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the posts API """

    # Setting testing infrastructure up

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)



    # Test client doesn't accept unsupported header

    def testUnsupportedAcceptHeader(self):
        """ Client accepts json response """
        response = self.client.get("/api/posts",
                                   headers=[("Accept", "application/xml")]
        )
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data["message"], "Request must accept application/json data")

        
    # Testing api can return empty response

    def testGetEmptyPosts(self):
        """ Getting empty posts from the database """

        response = self.client.get("/api/posts",
                                   headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data, [])


    # Testing that api can return posts

    def testGetPosts(self):
        """ Getting posts from a populated database """


        # First define test posts and commit them to database
        postA = models.Post(title="Example Post A", body="Just a test")
        postB = models.Post(title="Example Post B", body="Another test")

        session.add_all([postA, postB])
        session.commit()

        
        # Then retrieve the posts using the api endpoint

            # Define response as from the endpoint testing
        response = self.client.get("/api/posts",
                                   headers=[("Accept", "application/json")]
        )
        
            # Test response is successful and mimetype correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
            # Test two posts returned
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
            # Test two posts are same as exist in database
        postA = data[0]
        self.assertEqual(postA["title"], "Example Post A")
        self.assertEqual(postA["body"], "Just a test")

        postB = data[1]
        self.assertEqual(postB["title"], "Example Post B")
        self.assertEqual(postB["body"], "Another test")
        
        
    # Testing that api can return single post

    def testGetPost(self):
        """ Getting single post from database """

        # First define test posts and commit to database
        postA = models.Post(title="Example Post A", body="Just a test")
        postB = models.Post(title="Example Post B", body="Another test")
        
        session.add_all([postA, postB])
        session.commit()

        # Then retrieve from database and test if correct
        response = self.client.get("/api/posts/{}".format(postB.id),
                                   headers=[("Accept", "application/json")]
        )

            # - correct response and correct mimetype
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

            # - correct data in single post
        post = json.loads(response.data)
        self.assertEqual(post["title"],"Example Post B")
        self.assertEqual(post["body"], "Another test")

            
    # Testing correct response for nonexistant post

    def testNonExistantPost(self):
        """ Getting a single post which does not exist """
        response = self.client.get("/api/posts/1",
                                   headers=[("Accept", "application/json")]
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data["message"], "Could not find post with id 1")

        
    # Remove testing infrastructure

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

if __name__ == "__main__":
    unittest.main()
