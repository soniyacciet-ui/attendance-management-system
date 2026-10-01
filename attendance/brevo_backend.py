"""Django email backend using Brevo HTTP API (with failsafe)."""
import base64
import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class BrevoEmailBackend(BaseEmailBackend):
    """
    Uses Brevo HTTP API directly via requests (no sib-api-v3-sdk needed).
    This avoids Python 3.13 compatibility issues with the SDK.
    """

    def send_messages(self, email_messages):
        api_key = (getattr(settings, "BREVO_API_KEY", "") or "").strip()
        if not api_key:
            print("[brevo] No API key set")
            return 0

        sent = 0
        for message in email_messages:
            try:
                # Build attachments list
                attachments = []
                for attachment in message.attachments:
                    if isinstance(attachment, tuple):
                        filename, content, mimetype = attachment
                    else:
                        filename = attachment[0]
                        content = attachment[1]

                    if isinstance(content, str):
                        content = content.encode("utf-8")

                    attachments.append({
                        "content": base64.b64encode(content).decode("ascii"),
                        "name": filename,
                    })

                # Build the payload
                payload = {
                    "sender": {
                        "email": settings.DEFAULT_FROM_EMAIL,
                        "name": "Attendance System",
                    },
                    "to": [{"email": email} for email in message.to],
                    "subject": message.subject,
                    "textContent": message.body,
                }

                if attachments:
                    payload["attachment"] = attachments

                # Send via Brevo HTTP API
                response = requests.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={
                        "accept": "application/json",
                        "api-key": api_key,
                        "content-type": "application/json",
                    },
                    json=payload,
                    timeout=20,
                )

                if response.status_code in (200, 201):
                    print(f"[brevo] Sent to {list(message.to)}")
                    sent += 1
                else:
                    print(f"[brevo] Failed: {response.status_code} {response.text[:200]}")

            except Exception as e:
                print(f"[brevo] Error: {e}")

        return sent