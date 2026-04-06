import logging
import os

logger = logging.getLogger(__name__)


class TwilioClient:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self._client = None

    @property
    def is_configured(self) -> bool:
        return bool(self.account_sid and self.auth_token and self.phone_number)

    def _get_client(self):
        if self._client is None:
            if not self.is_configured:
                logger.warning("Twilio not configured. SMS will not be sent.")
                return None
            try:
                from twilio.rest import Client
                self._client = Client(self.account_sid, self.auth_token)
            except ImportError:
                logger.warning("twilio package not installed. SMS will not be sent.")
                return None
        return self._client

    def send(self, to: str, body: str) -> str | None:
        client = self._get_client()
        if not client:
            logger.info(f"[DEV MODE] SMS to {to}: {body}")
            return None
        message = client.messages.create(
            body=body,
            from_=self.phone_number,
            to=to,
        )
        return message.sid


twilio_client = TwilioClient()
