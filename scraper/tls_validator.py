import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse

def verify_tls_health(url: str, min_days_valid: int = 7) -> tuple[bool, str]:
    """
    Performs a low-level secure socket handshake to inspect the target's TLS certificate.
    Verifies expiration timelines and ensures the connection is using a secure configuration.
    Returns (is_healthy, reason_or_error_message).
    """
    try:
        # 1. Parse the hostname and handle default ports
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        if not hostname:
            return False, "Could not extract hostname from URL"
        
        port = parsed_url.port if parsed_url.port else 443

        # 2. Configure a strict SSL Context enforcing high security standards
        context = ssl.create_default_context()
        # Enforce TLS 1.2 or TLS 1.3 explicitly (disable older insecure versions like SSLv3, TLS 1.0, 1.1)
        context.minimum_version = ssl.TLSVersion.TLSv1_2 

        # 3. Establish the connection and perform the handshake
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                if not cert:
                    return False, "Server failed to provide a peer certificate"

                # 4. Extract and parse the 'notAfter' expiration date
                # Format example: 'May 27 15:10:00 2026 GMT'
                expire_str = cert.get('notAfter')
                if not expire_str:
                    return False, "Certificate is missing expiration metadata"
                
                expire_date = datetime.strptime(expire_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                remaining_time = expire_date - datetime.now(timezone.utc)
                
                # 5. Safety boundary check
                if remaining_time.days < 0:
                    return False, f"Certificate EXPIRED on {expire_str}"
                elif remaining_time.days < min_days_valid:
                    return False, f"Certificate warning: Expires in {remaining_time.days} days (Threshold: {min_days_valid})"
                
                return True, f"TLS verified. Protocol: {ssock.version()} | Valid until: {expire_str}"

    except ssl.SSLCertVerificationError as e:
        return False, f"SSL/TLS Verification Failure (Possible MitM or Untrusted CA): {str(e)}"
    except Exception as e:
        return False, f"Network/Handshake connection failure: {str(e)}"