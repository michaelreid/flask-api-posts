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
    # ---------------------------------------------
    def test_unsupported_accept_header(self):
        """ Client accepts json response """
        response = self.client.get("/api/posts",
                                   headers=[("Accept", "application/xml")]
        )
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data["message"], "Request must accept application/json data")

        
    # Testing api can return empty response
    # -------------------------------------
    def test_get_empty_posts(self):
        """ Getting empty posts from the database """

        response = self.client.get("/api/posts",
                                   headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data, [])


        
    # Testing that api can return posts
    #----------------------------------
    def test_get_posts(self):
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
    #----------------------------------------
    def test_get_post(self):
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
    #----------------------------------------------
    def test_non_existant_post(self):
        """ Getting a single post which does not exist """
        response = self.client.get("/api/posts/1",
                                   headers=[("Accept", "application/json")]
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data["message"], "Could not find post with id 1")

        

    # Testing api can delete post
    #----------------------------
    def test_delete_single_post(self):
        """ Deleting a single post from the database """

        # Define test posts and commit to database
        postA = models.Post(title="Example Post A", body="Just a test")
        postB = models.Post(title="Example Post B", body="Another test")
        
        session.add_all([postA, postB])
        session.commit()

        # Test post is in database
        self.test_get_post()

        
        # Test connection to delete posts endpoint
        response = self.client.delete("/api/post/1",
                                   headers=[("Accept", "application/json")]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        # Test response message is correct
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Deleted post with id 1 from the database")
                
        # Confirm deletion by testing GETting the same post
        self.test_non_existant_post()




    # Testing api returns with query strings
    #---------------------------------------
    def test_get_posts_with_title(self):
        """ Filtering posts by title """

        # First create number of posts
        postA = models.Post(title="Post with bells", body="Just a test")
        postB = models.Post(title="Post with whistles", body="Another test")
        postC = models.Post(title="Post with whistles", body="More tests")

        # Add posts to database
        session.add_all([postA, postB, postC])
        session.commit()

        # Test for posts containing 'whistles' in title
            # - Header is correct
        response = self.client.get("/api/posts?title_like=whistles",
                                   headers=[("Accept", "application/json")]
                               )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

           # - Number of posts is correct
        posts = json.loads(response.data)
        self.assertEqual(len(posts), 2)

            # - Individual post's title and body are correct
        post = posts[0]
        self.assertEqual(post["title"], "Post with whistles" )
        self.assertEqual(post["body"], "Another test" )

        post = posts[1]
        self.assertEqual(post["title"], "Post with whistles" )
        self.assertEqual(post["body"], "More tests" )


    
    def test_get_posts_with_body(self):
        """ Filtering posts by body """

        # First create number of posts
        postA = models.Post(title="Post with bells", body="Just a test")
        postB = models.Post(title="Post with whistles", body="Another test")
        postC = models.Post(title="Post with whistles", body="More tests")

        # Add posts to database
        session.add_all([postA, postB, postC])
        session.commit()


        # Test for posts containing 'Another' in body
            # - Header is correct
        response = self.client.get("/api/posts?body_like=Another",
                                   headers=[("Accept", "application/json")]
                               )
        print response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

           # - Number of posts is correct
        posts = json.loads(response.data)
        print posts
        self.assertEqual(len(posts), 1)

            # - Individual post's title and body are correct
        post = posts[0]
        self.assertEqual(post["title"], "Post with whistles" )
        self.assertEqual(post["body"], "Another test" )



    def test_get_posts_with_title_and_body(self):
        """ Filtering posts by title and body """

        # First create number of posts
        postA = models.Post(title="Post with bells", body="Just a test")
        postB = models.Post(title="Post with whistles", body="Another test")
        postC = models.Post(title="Post with whistles", body="More tests")

        # Add posts to database
        session.add_all([postA, postB, postC])
        session.commit()
        
        
        # Test for posts containing 'Whistle' in title and 'test' in body
            # - Header is correct
        response = self.client.get("/api/posts?title_like=whistles&body_like=test",
                                   headers=[("Accept", "application/json")]
                               )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

           # - Number of posts is correct
        posts = json.loads(response.data)
        print posts
        self.assertEqual(len(posts), 2)

            # - Individual post's title and body are correct
        post = posts[0]
        self.assertEqual(post["title"], "Post with whistles" )
        self.assertEqual(post["body"], "Another test" )

        post = posts[1]
        self.assertEqual(post["title"], "Post with whistles" )
        self.assertEqual(post["body"], "More tests" )

  
        
    # Remove testing infrastructure

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

if __name__ == "__main__":
    unittest.main()
