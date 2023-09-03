from telethon.sync import TelegramClient
from repository import BlockedDataRepo
import handlers


class Client(TelegramClient):
    def __init__(
            self,
            app_name: str,
            api_id: int,
            api_hash: str,
            repo: BlockedDataRepo,
    ):
        super().__init__(app_name, api_id, api_hash)
        self.repo = repo
        self.app_name = app_name
        self._register_handlers()

    def _register_handlers(self):
        self.add_event_handler(handlers.block_command_handler)
        self.add_event_handler(handlers.unblock_command_handler)
        self.add_event_handler(handlers.info_command_handler)
        self.add_event_handler(handlers.delete_msg_handler)

    def _say_hello(self):
        self.send_message('me', f"Hello, it's {self.app_name}!")

    def run(self):
        with self:
            self._say_hello()
            self.run_until_disconnected()
