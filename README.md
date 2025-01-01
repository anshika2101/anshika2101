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
 class TestSmtpServer(object):
    def test_send_should_return_success_when_email_is_sent(self):
        # Setup
        server_address = "test.smtp.server"
        smtp_server = SmtpServer(server_address)

        # Mock email object
        class MockEmail:
            sender = "test@example.com"
            def parse_receivers(self):
                return ["receiver@example.com"]
            def generate_body(self):
                return "Test email body"
            account_id = "test_account"

        email = MockEmail()

        # Act
        response = smtp_server.send(email)

        # Assert
        assert response.status == ResponseStatus.SUCCESS
        assert response.message == "Email correctly delivered to SMTP server"

    def test_send_should_return_failure_when_quota_exceeded(self):
        # Setup
        server_address = "test.smtp.server"
        smtp_server = SmtpServer(server_address)

        # Mock email object
        class MockEmail:
            sender = "test@example.com"
            def parse_receivers(self):
                return ["receiver@example.com"]
            def generate_body(self):
                return "Test email body"
            account_id = "test_account"

        email = MockEmail()

        # Simulate quota exceeded by modifying behavior
        def mock_check_quotas(*args, **kwargs):
            return "Quota exceeded"

        SmtpServer.check_quotas = mock_check_quotas  # Overwrite the method

        # Act
        response = smtp_server.send(email)

        # Assert
        assert response.status == ResponseStatus.QUOTAS
        assert "Error: unable to send email." in response.message
