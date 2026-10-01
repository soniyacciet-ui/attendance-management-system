"""Django email backend using Brevo HTTP API."""
import base64
import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class BrevoEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        api_key = (getattr(settings, "BREVO_API_KEY", "") or "").strip()
        if not api_key:
            print("[brevo] No API key set")
            return 0

        # Extract just the email from "Name <email>" format
        from_email = settings.DEFAULT_FROM_EMAIL or ""
        if "<" in from_email and ">" in from_email:
            from_email = from_email.split("<")[1].split(">")[0].strip()

        sent = 0
        for message in email_messages:
            try:
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

                payload = {
                    "sender": {
                        "email": from_email,
                        "name": "Attendance System",
                    },
                    "to": [{"email": email} for email in message.to],
                    "subject": message.subject,
                    "textContent": message.body,
                }

                if attachments:
                    payload["attachment"] = attachments

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
                    print(f"[brevo] Failed: {response.status_code} {response.text[:300]}")

            except Exception as e:
                print(f"[brevo] Error: {e}")

        return sent