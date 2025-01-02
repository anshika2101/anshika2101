def test_empty_payload():
    payload = {}
    response = Smtp.create_from_json(payload)
    assert response.status == ResponseStatus.SMTP
    assert "destination" in response.human_readable_response


