import json

from utils import keytoint


class BlockedDataRepo:
    def __init__(self):
        self._json_file = 'blocked_data.json'
        self._blocked_data = self._load_from_json(self._json_file)

    def add_channel(
            self,
            current_chat_id: int,
            forwarded_from_channel_id: int,
            title: str,
            comment: str | None
    ):
        channel_desc = {
            'channelTitle': title.strip(),
            'adminComment': comment.strip() if comment else None
        }

        current_chat_info = self._blocked_data.get(current_chat_id)
        if current_chat_info:
            current_chat_info[forwarded_from_channel_id] = channel_desc
        else:
            current_chat_info = {forwarded_from_channel_id: channel_desc}
        self._blocked_data[current_chat_id] = current_chat_info
        self._dump_to_json(self._blocked_data, self._json_file)

    def delete_channel(self, current_chat_id: int, forwarded_from_channel_id: int):
        current_chat_info = self._blocked_data.get(current_chat_id)
        if current_chat_info:
            current_chat_info.pop(forwarded_from_channel_id, None)
            if current_chat_info == {}:
                self._blocked_data.pop(current_chat_id)
            elif current_chat_info:
                self._blocked_data[current_chat_id] = current_chat_info
        self._dump_to_json(self._blocked_data, self._json_file)

    def get_channel_data(self, channel_id: int):
        return self._blocked_data.get(channel_id)

    def _load_from_json(self, json_file: str):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f, object_hook=keytoint)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        return {}

    def _dump_to_json(self, data: dict, json_file: str):
        with open(json_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
