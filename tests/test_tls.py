import pytest
from unittest.mock import patch, MagicMock
import ssl
from scraper.tls_validator import verify_tls_health

def test_tls_verification_success():
    """Validates that a live, highly secure domain (like example.com) passes cleanly."""
    success, message = verify_tls_health("https://example.com")
    assert success is True
    assert "TLS verified" in message

@patch('socket.create_connection')
@patch('ssl.create_default_context')
def test_tls_verification_expired_mock(mock_context_class, mock_connect):
    """Asserts that if a peer certificate date is in the past, it triggers a security block."""
    # Build a mock structure matching a real wrapped socket certificate dict
    mock_context = MagicMock()
    mock_ssock = MagicMock()
    
    # Fake an expired date payload
    mock_ssock.getpeercert.return_value = {'notAfter': 'Jan 01 00:00:00 2020 GMT'}
    mock_ssock.version.return_value = 'TLSv1.3'
    
    mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssock
    mock_context_class.return_value = mock_context

    success, message = verify_tls_health("https://expired-test.com")
    assert success is False
    assert "EXPIRED" in message

@patch('socket.create_connection')
@patch('ssl.create_default_context')
def test_tls_verification_bad_ca_mock(mock_context_class, mock_connect):
    """Asserts that a standard SSLCertVerificationError is caught and handled elegantly."""
    mock_context = MagicMock()
    # Force the wrap_socket operation to raise an explicit SSL verification exception
    mock_context.wrap_socket.side_effect = ssl.SSLCertVerificationError(1, "CERT_HAS_EXPIRED")
    mock_context_class.return_value = mock_context

    success, message = verify_tls_health("https://untrusted-test.com")
    assert success is False
    assert "SSL/TLS Verification Failure" in message