from telethon.sync import TelegramClient, events
from telethon.tl.patched import Message

from config import API_ID, API_HASH, APP_NAME
from repository import BlockedDataRepo


def run(client: TelegramClient, repo: BlockedDataRepo):
    with client:
        client.send_message('me', "Hello, it's telethon-blocker!")

        @client.on(events.NewMessage(from_users='me', pattern="^//block*", outgoing=True))
        async def block_command_handler(event: events.NewMessage.Event):
            admin_message_obj: Message = event.message
            admin_command: str = admin_message_obj.message
            current_chat_id: int = event.chat_id

            try:
                target_message_id = admin_message_obj.reply_to.reply_to_msg_id
                target_message_obj: Message = await client.get_messages(current_chat_id, ids=target_message_id)
                forwarded_from_channel_id = target_message_obj.fwd_from.from_id.channel_id
                channel_title = target_message_obj.forward.chat.title
            except AttributeError:
                pass
            else:
                try:
                    _, admin_comment = admin_command.split(' ', maxsplit=1)
                except ValueError:
                    admin_comment = None

                repo.add_channel(current_chat_id, forwarded_from_channel_id, channel_title, admin_comment)

        @client.on(events.NewMessage(from_users='me', pattern="^//unblock", outgoing=True))
        async def unblock_command_handler(event: events.NewMessage.Event):
            admin_message_obj: Message = event.message
            current_chat_id: int = event.chat_id

            try:
                target_message_id = admin_message_obj.reply_to.reply_to_msg_id
                target_message_obj: Message = await client.get_messages(current_chat_id, ids=target_message_id)
                forwarded_from_channel_id = target_message_obj.fwd_from.from_id.channel_id
            except AttributeError:
                pass
            else:
                repo.delete_channel(current_chat_id, forwarded_from_channel_id)

        @client.on(events.NewMessage(from_users='me', pattern="^//info", outgoing=True))
        async def info_command_handler(event: events.NewMessage.Event):
            ...

        @client.on(events.NewMessage(incoming=True, forwards=True))
        async def delete_msg_handler(event: events.NewMessage.Event):
            message_obj: Message = event.message
            current_chat_id: int = event.chat_id

            try:
                from_channel_id = message_obj.fwd_from.from_id.channel_id
            except AttributeError:
                pass
            else:

                current_chat_blocked_data = repo.blocked_data.get(current_chat_id)

                if current_chat_blocked_data and from_channel_id in current_chat_blocked_data.keys():
                    await message_obj.delete()
                    channel_blocked_data = current_chat_blocked_data[from_channel_id]
                    channel_title, comment = channel_blocked_data['channelTitle'], channel_blocked_data['adminComment']
                    if channel_title and comment:
                        await client.send_message(
                            current_chat_id,
                            f"Сообщение от канала «{channel_title}» удалено по причине: **\"{comment}\"**"
                        )

        client.run_until_disconnected()


if __name__ == '__main__':
    run(
        client=TelegramClient(APP_NAME, API_ID, API_HASH),
        repo=BlockedDataRepo()
    )
