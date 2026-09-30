"""
Custom Django email backend using Resend HTTP API.
Works on Render free tier (uses HTTPS port 443, not SMTP port 587).
"""

import base64
import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class ResendEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not settings.RESEND_API_KEY:
            print("[resend] No API key set")
            return 0

        sent = 0
        for message in email_messages:
            try:
                from_email = message.from_email or settings.DEFAULT_FROM_EMAIL

                if "gmail.com" in from_email or "@" not in from_email:
                    from_email = "onboarding@resend.dev"

                payload = {
                    "from": from_email,
                    "to": list(message.to),
                    "subject": message.subject,
                    "text": message.body,
                }

                if hasattr(message, "alternatives"):
                    for alt_content, alt_mimetype in message.alternatives:
                        if alt_mimetype == "text/html":
                            payload["html"] = alt_content

                attachments = []
                for attachment in message.attachments:
                    try:
                        if isinstance(attachment, tuple):
                            filename, content, mimetype = attachment
                        else:
                            filename = attachment[0]
                            content = attachment[1]

                        if isinstance(content, str):
                            content = content.encode("utf-8")

                        attachments.append({
                            "filename": filename,
                            "content": base64.b64encode(content).decode("ascii"),
                        })
                    except Exception as e:
                        print(f"[resend] Attachment error: {e}")

                if attachments:
                    payload["attachments"] = attachments

                response = requests.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=20,
                )

                if response.status_code in (200, 201):
                    print(f"[resend] Sent to {list(message.to)}")
                    sent += 1
                else:
                    print(f"[resend] Failed: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"[resend] Error: {e}")

        return sent
