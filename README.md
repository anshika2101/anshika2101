## Hi there 👋

<!--
**anshika2101/anshika2101** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->
import pytest
from unittest.mock import patch, MagicMock, call
from your_module import Worker, EventConsumerManager  # Replace with your actual module name
import json

@pytest.fixture
def mock_engine():
    """Mock database engine."""
    return MagicMock()

@pytest.fixture
def mock_broker_connection():
    """Mock broker connection."""
    with patch("your_module.BrokerConnection") as broker:
        yield broker

@pytest.fixture
def mock_logger():
    """Mock logger."""
    with patch("your_module.sgl.get_sg_logger") as logger:
        yield logger

@pytest.fixture
def worker(mock_engine):
    """Initialize Worker with mocked dependencies."""
    queues = MagicMock()
    return Worker(MagicMock(), queues, "mock_rabbit_url")

def test_worker_initialization(worker):
    assert worker.connection is not None
    assert worker.queues is not None
    assert worker.rabbit_url == "mock_rabbit_url"
    assert worker.engine is not None

def test_on_message_valid(worker, mock_logger):
    """Test valid message processing."""
    body = json.dumps({"sms": {"destination": "1234567890", "body": "Test", "account_id": 1}})
    message = MagicMock()
    with patch("your_module.SmsSender.create_sms") as mock_sms, \
         patch("your_module.ResponseStatus") as mock_status, \
         patch("your_module.mark_as_success") as mock_success:
        # Mock SMS success scenario
        mock_sms.return_value.instance.send.return_value.status = mock_status.SUCCESS
        worker.on_message(body, message)
        mock_success.assert_called_once()

def test_on_message_invalid(worker, mock_logger):
    """Test invalid message handling."""
    body = "Invalid JSON"
    message = MagicMock()
    worker.on_message(body, message)
    mock_logger.error.assert_called()

def test_publish_notification(worker, mock_logger):
    """Test publish_notification."""
    body = {"action": {"some": "data"}}
    with patch("your_module.post_in_queue") as mock_post:
        worker.publish_notification(body, 1)
        mock_post.assert_called_once()

def test_republish(worker, mock_logger):
    """Test republish logic."""
    body = {"test": "data"}
    message = MagicMock(headers={"x-redelivered-count": 0})
    with patch("your_module.Publisher") as mock_publisher:
        worker.republish(body, message)
        assert message.ack.called
        mock_publisher.assert_called_once()

def test_republish_max_retries(worker, mock_logger):
    """Test republish max retry scenario."""
    body = {"test": "data"}
    message = MagicMock(headers={"x-redelivered-count": 3})
    worker.republish(body, message)
    assert "Max number of retry reached" in str(mock_logger.debug.call_args)

def test_event_consumer_manager_run(mock_broker_connection, mock_logger):
    """Test EventConsumerManager.run."""
    app = MagicMock()
    manager = EventConsumerManager(app)
    with patch("your_module.Worker") as mock_worker:
        manager.run()
        mock_worker.assert_called_once()
