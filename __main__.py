import os
from logging.handlers import TimedRotatingFileHandler

from telethon.sync import TelegramClient, events
from telethon.events.newmessage import NewMessage

import json
from cachetools.func import ttl_cache
from dotenv import load_dotenv
import logging

from telethon.tl.patched import Message

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
TTL_SECS = int(os.getenv('TTL_SECS'))


def create_timed_rotating_log(path):
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)

    handler = TimedRotatingFileHandler(
        path,
        when="d",
        interval=1,
        backupCount=0,
        encoding='utf-8'
    )
    logger.addHandler(handler)


@ttl_cache(ttl=TTL_SECS)
def load_blocked_ids():
    with open('blocked_data.json', 'r') as json_file:
        blocked_data = json.load(json_file)
        return blocked_data['blocked_chat_ids'], blocked_data['blocked_from_channels_ids']


if __name__ == '__main__':
    create_timed_rotating_log('logs.log')

    with TelegramClient('telethonblocker', API_ID, API_HASH) as client:  # type: TelegramClient
        client.send_message('me', "Hello, it's telethonblocker!")


        @client.on(events.NewMessage(incoming=True, forwards=True))
        async def handler(event: NewMessage.Event):
            blocked_chat_ids, blocked_from_channels_ids = load_blocked_ids()

            if event.chat_id in blocked_chat_ids:
                message: Message = event.message
                try:
                    from_channel_id = message.fwd_from.from_id.channel_id
                except AttributeError:
                    ...
                else:
                    if from_channel_id in blocked_from_channels_ids:
                        await message.delete()
                    else:
                        print(f"{event.chat_id} {message.message}")
                        logging.info(f"{event.chat_id} {message.message}")


        client.run_until_disconnected()
