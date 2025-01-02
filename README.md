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

def test_missing_destination():
    payload = {"sender": "test@example.com", "subject": "Test", "body": "Test body", "destination": ""}
    response = Smtp.create_from_json(payload)
    assert response.status == ResponseStatus.SMTP
    assert "destination" in response.human_readable_response

def test_invalid_email_address():
    payload = {
        "sender": "invalid-email",
        "destination": "not-an-email",
        "subject": "Test",
        "body": "Test body",
    }
    response = Smtp.create_from_json(payload)
    assert response.status == ResponseStatus.SMTP
    assert "destination" in response.human_readable_response
def test_missing_subject():
    payload = {"sender": "test@example.com", "destination": "test@example.com", "body": "Test body", "subject": ""}
    response = Smtp.create_from_json(payload)
    assert response.status == ResponseStatus.SMTP
    assert "subject" in response.human_readable_response

