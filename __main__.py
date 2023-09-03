import os
import json

from telethon.sync import TelegramClient, events
from telethon.events.newmessage import NewMessage
from telethon.tl.patched import Message

from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')


def keytoint(d: dict):
    return {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()}


def load_blocked_data():
    try:
        with open('blocked_data.json', 'r', encoding='utf-8') as json_file:
            return json.load(json_file, object_hook=keytoint)
    except (FileNotFoundError, json.JSONDecodeError):
        with open('blocked_data.json', 'w', encoding='utf-8') as json_file:
            json.dump({}, json_file, ensure_ascii=False, indent=4)
        return {}


def dump_blocked_data(data: dict):
    with open('blocked_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def add_blocked_channel(
        blocked_data: dict,
        current_chat_id: int,
        forwarded_from_channel_id: int,
        title: str,
        comment: str
):
    channel_desc = {
        'ChannelTitle': title.strip(),
        'AdminComment': comment.strip()
    }

    current_chat_info = blocked_data.get(current_chat_id)
    if current_chat_info:
        current_chat_info[forwarded_from_channel_id] = channel_desc
    else:
        current_chat_info = {forwarded_from_channel_id: channel_desc}
    blocked_data[current_chat_id] = current_chat_info
    return blocked_data


def remove_blocked_channel(blocked_data: dict, current_chat_id: int, forwarded_from_channel_id: int):
    current_chat_info = blocked_data.get(current_chat_id)
    if current_chat_info:
        current_chat_info.pop(forwarded_from_channel_id, None)
        if current_chat_info == {}:
            blocked_data.pop(current_chat_id)
        elif current_chat_info:
            blocked_data[current_chat_id] = current_chat_info
    return blocked_data


if __name__ == '__main__':
    with TelegramClient('telethonblocker', API_ID, API_HASH) as client:  # type: TelegramClient

        client.send_message('me', "Hello, it's telethonblocker!")


        @client.on(events.NewMessage(from_users='me', pattern="^//*", outgoing=True))
        async def block_handler(event: NewMessage.Event):
            admin_message_obj: Message = event.message
            current_chat_id = admin_message_obj.chat_id
            admin_command: str = admin_message_obj.message

            if admin_command.startswith('//block') or admin_command == '//unblock':
                try:
                    target_message_id = admin_message_obj.reply_to.reply_to_msg_id
                except AttributeError:
                    pass
                else:
                    target_message_obj: Message = await client.get_messages(current_chat_id, ids=target_message_id)

                    try:
                        forwarded_from_channel_id = target_message_obj.fwd_from.from_id.channel_id
                    except AttributeError:
                        pass
                    else:
                        blocked_data = load_blocked_data()
                        if admin_command.startswith('//block'):
                            try:
                                _, title, comment = admin_command.split(':')
                            except ValueError:
                                title, comment = '', ''
                            blocked_data = add_blocked_channel(
                                blocked_data, current_chat_id, forwarded_from_channel_id, title, comment
                            )

                        elif admin_command == '//unblock':
                            blocked_data = remove_blocked_channel(
                                blocked_data, current_chat_id, forwarded_from_channel_id
                            )

                        dump_blocked_data(blocked_data)


        @client.on(events.NewMessage(incoming=True, forwards=True))
        async def delete_msg_handler(event: NewMessage.Event):
            message_obj: Message = event.message
            current_chat_id: int = event.chat_id

            blocked_data = load_blocked_data()

            try:
                from_channel_id = message_obj.fwd_from.from_id.channel_id
            except AttributeError:
                pass
            else:
                current_chat_blocked_data = blocked_data.get(current_chat_id)

                if current_chat_blocked_data and from_channel_id in current_chat_blocked_data.keys():
                    await message_obj.delete()
                    title = current_chat_blocked_data[from_channel_id]['ChannelTitle']
                    comment = current_chat_blocked_data[from_channel_id]['AdminComment']
                    if title and comment:
                        await client.send_message(
                            current_chat_id,
                            f"Сообщение от канала «{title}» удалено по причине: **\"{comment}\"**"
                        )


        client.run_until_disconnected()
