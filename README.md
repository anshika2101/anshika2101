

from unittest.mock import patch, MagicMock
import smtplib

def test_smtp_error_handling():
    # Mock smtplib.SMTP
    with patch("smtplib.SMTP") as mock_smtp:
        # Create a mock SMTP instance
        mock_instance = MagicMock()
        mock_smtp.return_value = mock_instance

        # Configure the mock to raise an SMTPException
        mock_instance.sendmail.side_effect = smtplib.SMTPException("SMTP Error")

        # Simulate the function that uses smtplib
        payload = {
            "sender": "test@example.com",
            "destination": "test@example.com",
            "subject": "Test Subject",
            "body": "Test Body",
        }
        try:
            smtp = Smtp.create_from_json(payload).instance
            smtp.send()
        except smtplib.SMTPException as e:
            assert str(e) == "SMTP Error"
