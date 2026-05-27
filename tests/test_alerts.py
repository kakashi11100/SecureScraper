import pytest
from unittest.mock import patch
from alerts.slack import send_slack_alert
from alerts.email_alert import send_email_alert

@patch('alerts.slack.os.getenv')
@patch('alerts.slack.requests.post')
def test_slack_alert_success(mock_post, mock_getenv):
    """Asserts that if the Slack webhook is set up right, the alert sends perfectly."""
    # Mocking out the env variable check and API network response
    mock_getenv.return_value = "https://hooks.slack.com/services/test/webhook"
    mock_post.return_value.status_code = 200

    success = send_slack_alert("https://test.com", "Test Label")
    assert success is True
    mock_post.assert_called_once()

@patch('alerts.email_alert.os.getenv')
@patch('alerts.email_alert.smtplib.SMTP')
def test_email_alert_success(mock_smtp, mock_getenv):
    """Asserts that if SMTP config is populated, email dispatch executes smoothly."""
    def env_side_effect(key, default=None):
        env_vars = {
            "SMTP_HOST": "smtp.test.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "me@test.com",
            "SMTP_PASS": "secretpass",
            "ALERT_EMAIL_TO": "alerts@test.com"
        }
        return env_vars.get(key, default)
        
    mock_getenv.side_effect = env_side_effect

    success = send_email_alert("https://test.com", "Test Label")
    assert success is True
    mock_smtp.assert_called_once()