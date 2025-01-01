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
from alerting_sms.resources.smtp import SmtpServer, ResponseStatus, QuotaExceededException

def test_smtp_server_send_quota_exceeded(mocker):
    # Arrange
    mocker.patch("alerting_sms.utils.check_quotas", side_effect=QuotaExceededException("Quota exceeded"))

    smtp_server = SmtpServer("test.smtp.server")
    
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
    assert response.status == ResponseStatus.QUOTAS
    assert "Error: unable to send email." in response.message
