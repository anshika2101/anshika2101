from alerting_sms.resources.sms_sender import SmsSender
from alerting_sms.resources.smtp import ResponseStatus

class TestSmsSender:
    def test_create_sms_valid_french_number(self):
        phone_number = "+33600000000"
        message = "Hello, world!"
        response = SmsSender.create_sms(phone_number, message, "1234")
        
        assert ResponseStatus.SUCCESS == response.status
        sms = response.instance
        assert sms.subject == phone_number
        assert sms.body == message
        assert sms.sender == SmsSender.sender
        assert sms.destination == SmsSender.receiver

    def test_create_sms_valid_uk_number(self):
        phone_number = "+447911123456"
        message = "Hello, world!"
        response = SmsSender.create_sms(phone_number, message, "1234")
        
        assert ResponseStatus.SUCCESS == response.status
        sms = response.instance
        assert sms.subject == phone_number
        assert sms.body == message
        assert sms.sender == SmsSender.sender
        assert sms.destination == SmsSender.receiver

    def test_create_sms_invalid_number(self):
        wrong_number = "01453"
        message = "Hello, world!"
        response = SmsSender.create_sms(wrong_number, message, "1234")
        
        assert ResponseStatus.INVALID_PHONE_NUMBER == response.status
        assert response.instance is None

    def test_check_phone_number_valid(self):
        assert SmsSender.check_phone_number("+33600000000") is True
        assert SmsSender.check_phone_number("+447911123456") is True

    def test_check_phone_number_invalid(self):
        assert SmsSender.check_phone_number("01453") is False
        assert SmsSender.check_phone_number("+44123") is False

    def test_check_phone_number_exception(self):
        # Test with a malformed phone number to trigger NumberParseException
        assert SmsSender.check_phone_number("INVALID_NUMBER") is False
