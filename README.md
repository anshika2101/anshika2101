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
 
 @patch('alerting_sms.consumer.mark_as_failed')
@patch('alerting_sms.consumer.mark_as_success')
@patch('alerting_sms.consumer.SmsSender.create_sms')
def test_on_message_failure(mock_create_sms, mock_mark_as_success, mock_mark_as_failed, worker):
    body = {
        "sms": {
            "destination": "1234567890",
            "body": "Test message",
            "account_id": "test_account",
            "notification_id": "test_notification",
        }
    }
    message = MagicMock()
    sms_instance = MagicMock()
    sms_instance.send.return_value.status = ResponseStatus.FAILURE
    mock_create_sms.return_value = sms_instance

    worker.on_message(body, message)

    # Assertions
    mock_create_sms.assert_called_once()
    mock_mark_as_success.assert_not_called()
    mock_mark_as_failed.assert_called_once_with(worker.engine, "test_notification")
    message.ack.assert_called_once()
