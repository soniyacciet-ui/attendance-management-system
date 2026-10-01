"""Django email backend using Brevo HTTP API (works on Render)."""
import base64
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


class BrevoEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not settings.BREVO_API_KEY:
            print("[brevo] No API key set")
            return 0

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.BREVO_API_KEY.strip()        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

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

                to_list = [{"email": email} for email in message.to]

                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to_list,
                    sender={
                        "email": settings.DEFAULT_FROM_EMAIL,
                        "name": "Attendance System",
                    },
                    subject=message.subject,
                    text_content=message.body,
                    attachment=attachments if attachments else None,
                )

                api_response = api_instance.send_transac_email(send_smtp_email)
                print(f"[brevo] Sent to {message.to} (ID: {api_response.message_id})")
                sent += 1

            except ApiException as e:
                print(f"[brevo] API error: {e}")
            except Exception as e:
                print(f"[brevo] Error: {e}")

        return sent
