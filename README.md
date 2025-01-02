def test_post_message_connection_error(self):
    """Tests handling a connection error to RabbitMQ."""
    original_uri = os.environ.get("FORWARD_RMQ")
    os.environ["FORWARD_RMQ"] = "amqp://guest:guest@localhost:5673/"  # Invalid port

    with self.assertRaises(ConnectionError):
        post_message(uid())

    os.environ["FORWARD_RMQ"] = original_uri  # Restore the original URI
