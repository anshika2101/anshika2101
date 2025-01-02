def post_message(content):
    """
    Posts a message to the RabbitMQ queue.

    Args:
        content: The message content to be posted.
    """
    uri = os.environ.get("FORWARD_RMQ")
    with Connection(uri) as connection:
        connection.SimpleQueue('your_queue_name').put(content)
