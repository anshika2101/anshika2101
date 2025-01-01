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
 
import unittest
from unittest.mock import patch, MagicMock
from your_module import SmtpServer, Response, ResponseStatus  # Replace 'your_module' with the actual module name

class TestSmtpServer(unittest.TestCase):

    @patch("your_module.smtplib.SMTP")
    @patch("your_module.check_quotas")
    @patch("your_module.email.generate_body")
    @patch("your_module.update_quotas")
    def test_send_email_success(self, mock_update_quotas, mock_generate_body, mock_check_quotas, mock_smtp):
        # Mock inputs and outputs
        mock_check_quotas.return_value = None
        mock_generate_body.return_value = "Email body"
        smtp_instance = MagicMock()
        mock_smtp.return_value = smtp_instance

        # Create instance of SmtpServer
        server_address = "test.smtp.server"
        smtp_server = SmtpServer(server_address)

        # Mock email object
        email = MagicMock()
        email.sender = "test@example.com"
        email.parse_receivers.return_value = ["receiver@example.com"]
        email.account_id = "test_account"

        # Call the method
        response = smtp_server.send(email)

        # Assertions
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.message, "Email correctly delivered to SMTP server")
        smtp_instance.connect.assert_called_once_with(server_address, 25)
        smtp_instance.sendmail.assert_called_once_with(
            email.sender,
            ["receiver@example.com"],
            "Email body".encode("utf-8"),
        )
        mock_update_quotas.assert_any_call("sms", "test_account")
        mock_update_quotas.assert_any_call("sms", "global")

    @patch("your_module.check_quotas")
    def test_send_email_quota_exceeded(self, mock_check_quotas):
        # Mock quota exceeded
        mock_check_quotas.return_value = "Quota e
