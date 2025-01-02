def test_valid_multiple_destinations():
    payload = {
        "sender": "test@example.com",
        "destination": "test1@example.com, test2@example.com",
        "subject": "Test",
        "body": "Test body",
    }
    response = Smtp.create_from_json(payload)
    smtp = response.instance
    assert response.status == ResponseStatus.SUCCESS
    assert smtp.parse_receivers() == ["test1@example.com", "test2@example.com"]


