def test_smtp_connection_error():
    class MockFailingServer(SmtpServer):
        def send(self, email):
            raise smtplib.SMTPException("Connection error")

    Smtp.set_smtp_server(MockFailingServer("mock_address"))
    payload = {
        "sender": "test@example.com",
        "destination": "test@example.com",
        "subject": "Test Subject",
        "body": "Test Body",
    }
    smtp = Smtp.create_from_json(payload).instance
    response = smtp.send()
    assert response.status == ResponseStatus.SMTP
    assert "Connection error" in response.human_readable_response
