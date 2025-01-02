def test_quotas_exceeded():
    class MockQuotaServer(SmtpServer):
        def send(self, email):
            raise QuotaExceededException("Quota exceeded")

    Smtp.set_smtp_server(MockQuotaServer("mock_address"))
    payload = {
        "sender": "test@example.com",
        "destination": "test@example.com",
        "subject": "Test Subject",
        "body": "Test Body",
    }
    smtp = Smtp.create_from_json(payload).instance
    response = smtp.send()
    assert response.status == ResponseStatus.QUOTAS
    assert "Quota exceeded" in response.human_readable_response
