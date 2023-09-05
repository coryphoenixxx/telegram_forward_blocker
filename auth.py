from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from src.config import API_ID, API_HASH


def auth(api_id, api_hash):
    with TelegramClient(StringSession(), api_id, api_hash) as client:
        with open('./data/session.txt', 'w', encoding='utf-8') as f:
            f.write(client.session.save())


if __name__ == '__main__':
    auth(API_ID, API_HASH)

