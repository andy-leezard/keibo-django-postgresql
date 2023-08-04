import logging
from channels.generic.websocket import WebsocketConsumer
from .utils import safely_load_json
import json

logger = logging.getLogger(__name__)


class PingWSConsumer(WebsocketConsumer):
    def connect(self):
        kwargs = self.scope["url_route"]["kwargs"]
        self.user_id = kwargs["user_id"]
        # log
        logger.info("PingWSConsumer: connect user for ping %s", self.user_id)
        self.accept()

    def receive(self, text_data):
        loaded_data = safely_load_json(text_data, text_data)
        if loaded_data == "ping":
            self.send(json.dumps({"message": "pong"}))

    def disconnect(self, close_code):
        pass
