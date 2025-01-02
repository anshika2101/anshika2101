def test_generate_body():
    smtp = Smtp(
        sender="test@example.com",
        destination="recipient@example.com",
        subject="Test Subject",
        body="This is a test email.",
    )
    expected_body = (
        "Content-type: text/plain; charset=UTF-8\r\n"
        "From: test@example.com\r\n"
        "To: recipient@example.com\r\n"
        "SUBJECT: Test Subject\r\n"
        "\r\n"
        "This is a test email.\r\n"
        "\r\n"
    )
    assert smtp.generate_body() == expected_body
