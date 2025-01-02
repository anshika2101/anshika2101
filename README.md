import os
import unittest
from kombu import Connection, Exchange, Queue
from kombu.exceptions import ConnectionError

from utils import uid  # Assuming uid() is the function generating the message content

class TestUtils(unittest.TestCase):

    def setUp(self):
        # Set up a test environment for RabbitMQ (if needed)

    def test_post_message_valid_uri(self):
        """Tests posting a message with a valid RabbitMQ URI."""
        os.environ["FORWARD_RMQ"] = "amqp://guest:guest@localhost:5672//"  # Replace with your test RabbitMQ URI

        try:
            post_message(uid())  # Call the function to post the message
        except Exception as e:
            self.fail(f"Posting message failed with error: {e}")

    def test_post_message_invalid_uri(self):
        """Tests handling an invalid RabbitMQ URI."""
        os.environ["FORWARD_RMQ"] = "invalid_uri"

        with self.assertRaises(ConnectionError):
            post_message(uid())

    def test_post_message_missing_uri(self):
        """Tests handling the case where FORWARD_RMQ is not set."""
        if "FORWARD_RMQ" in os.environ:
            del os.environ["FORWARD_RMQ"]

        with self.assertRaises(KeyError):  # Or another appropriate exception
            post_message(uid())

    def test_post_message_connection_error(self):
        """Tests handling a connection error to RabbitMQ."""
        # Simulate a network error (e.g., by temporarily stopping RabbitMQ)
        # ...

        with self.assertRaises(ConnectionError):
            post_message(uid())

    def tearDown(self):
        # Clean up the test environment (if needed)

if __name__ == '__main__':
    unittest.main()
