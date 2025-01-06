import unittest
from unittest.mock import patch, MagicMock
from your_module_name import SmtpServer, Response, ResponseStatus, QuotaExceededException


class TestSmtpServer(unittest.TestCase):

    @patch('your_module_name.smtplib.SMTP')
    @patch('your_module_name.app.config.get')
    @patch('your_module_name.check_quotas')
    @patch('your_module_name.update_quotas')
    def test_send_successful_email(self, mock_update_quotas, mock_check_quotas, mock_config_get, mock_smtp):
        # Setup
        mock_config_get.return_value = 'DEV'
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        mock_check_quotas.return_value = None
        
        smtp_server = SmtpServer()
        email = MagicMock()
        email.sender = "test@example.com"
        email.account_id = "12345"
        email.generate_body.return_value = "Email body"
        email.parse_receivers.return_value = ["receiver@example.com"]

        # Execute
        response = smtp_server.send(email)

        # Verify
        mock_smtp_instance.connect.assert_called_with('applications.hermes.si.socgen', 25)
        mock_smtp_instance.sendmail.assert_called_with(
            email.sender,
            ["receiver@example.com"],
            "Email body".encode("utf-8")
        )
        mock_update_quotas.assert_any_call('sms', '12345')
        mock_update_quotas.assert_any_call('sms', 'global')
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertIn("Email correctly delivered to SMTP server", response.human_readable_response)

    @patch('your_module_name.smtplib.SMTP')
    @patch('your_module_name.app.config.get')
    @patch('your_module_name.check_quotas')
    def test_send_quota_exceeded(self, mock_check_quotas, mock_config_get, mock_smtp):
        # Setup
        mock_config_get.return_value = 'PRD'
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        mock_check_quotas.side_effect = QuotaExceededException("Quota exceeded for user")

        smtp_server = SmtpServer()
        email = MagicMock()
        email.account_id = "12345"

        # Execute
        response = smtp_server.send(email)

        # Verify
        self.assertEqual(response.status, ResponseStatus.QUOTAS)
        self.assertIn("Quotas exceeded for user", response.human_readable_response)

    @patch('your_module_name.smtplib.SMTP')
    @patch('your_module_name.app.config.get')
    @patch('your_module_name.check_quotas')
    def test_send_smtp_exception(self, mock_check_quotas, mock_config_get, mock_smtp):
        # Setup
        mock_config_get.return_value = 'PRD'
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        mock_smtp_instance.sendmail.side_effect = Exception("SMTP error")

        smtp_server = SmtpServer()
        email = MagicMock()
        email.sender = "test@example.com"
        email.account_id = "12345"
        email.generate_body.return_value = "Email body"
        email.parse_receivers.return_value = ["receiver@example.com"]

        # Execute
        response = smtp_server.send(email)

        # Verify
        self.assertEqual(response.status, ResponseStatus.FAILURE)
        self.assertIn("SMTP error", response.human_readable_response)

    @patch('your_module_name.smtplib.SMTP')
    @patch('your_module_name.app.config.get')
    def test_debug_mode_enabled_in_local_env(self, mock_config_get, mock_smtp):
        # Setup
        mock_config_get.return_value = 'LOCAL'
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        smtp_server = SmtpServer()
        email = MagicMock()

        # Execute
        smtp_server.send(email)

        # Verify
        mock_smtp_instance.set_debuglevel.assert_called_with(1)


if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, MagicMock
from your_module_name import SmtpServer, Response, ResponseStatus, QuotaExceededException
import inspect


class TestQuotaExceededExceptionHandling(unittest.TestCase):

    @patch('your_module_name.smtplib.SMTP')
    @patch('your_module_name.app.config.get')
    @patch('your_module_name.check_quotas')
    def test_quota_exceeded_exception_handling(self, mock_check_quotas, mock_config_get, mock_smtp):
        # Setup
        mock_config_get.return_value = 'PRD'
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        mock_check_quotas.side_effect = QuotaExceededException("Quota exceeded for user")

        smtp_server = SmtpServer()
        email = MagicMock()
        email.account_id = "12345"

        # Redirect print to capture the output
        with patch('builtins.print') as mock_print:
            response = smtp_server.send(email)

        # Verify
        # Ensure the exception was caught and handled
        self.assertEqual(response.status, ResponseStatus.QUOTAS)
        self.assertIn("Quotas exceeded for user", response.human_readable_response)

        # Check if the file name and line number were printed correctly
        f = inspect.currentframe()
        expected_message = f"{f.f_code.co_filename}#{f.f_lineno - 4}:"  # Adjusted for relative line offset
        mock_print.assert_any_call(expected_message, "Quota exceeded for user")


if __name__ == '__main__':
    unittest.main()

