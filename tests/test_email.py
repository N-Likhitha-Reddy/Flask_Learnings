import pytest
from api.auth_apis import send_otp_email


@pytest.fixture
def mock_smtp(mocker):
    return mocker.patch('smtplib.SMTP')


def test_send_otp_email(mock_smtp):
    # Setup mock
    mock_smtp_instance = mock_smtp.return_value
    mock_smtp_instance.sendmail.return_value = None

    # Call function
    send_otp_email('test@example.com', 123456)

    # Assertions
    mock_smtp_instance.sendmail.assert_called_once()
    assert mock_smtp_instance.sendmail.call_args[0][0] == 'defaultmail@gmail.com'
