from telethon.sync import events
from telethon.tl.patched import Message


@events.register(events.NewMessage(from_users='me', pattern="^//block*", outgoing=True))
async def block_command_handler(event: events.NewMessage.Event):
    try:
        target_message_id: int = event.message.reply_to.reply_to_msg_id
        target_message_obj: Message = await event.client.get_messages(event.chat_id, ids=target_message_id)
        forwarded_from_channel_id: int = target_message_obj.fwd_from.from_id.channel_id
        channel_title: str = target_message_obj.forward.chat.title
    except AttributeError:
        pass
    else:
        try:
            _, admin_comment = event.message.message.split(' ', maxsplit=1)
        except ValueError:
            admin_comment = None

        event.client.repo.add_channel(event.chat_id, forwarded_from_channel_id, channel_title, admin_comment)


@events.register(events.NewMessage(from_users='me', pattern="^//unblock", outgoing=True))
async def unblock_command_handler(event: events.NewMessage.Event):
    try:
        target_message_id: int = event.message.reply_to.reply_to_msg_id
        target_message_obj: Message = await event.client.get_messages(event.chat_id, ids=target_message_id)
        forwarded_from_channel_id: int = target_message_obj.fwd_from.from_id.channel_id
    except AttributeError:
        pass
    else:
        event.client.repo.delete_channel(event.chat_id, forwarded_from_channel_id)


@events.register(events.NewMessage(from_users='me', pattern="^//info", outgoing=True))
async def info_command_handler(event: events.NewMessage.Event):
    current_chat_blocked_data: dict | None = event.client.repo.get_channel_data(event.chat_id)
    if current_chat_blocked_data:
        blocked_data_text_list = []
        for i, (_, channel_blocked_data) in enumerate(current_chat_blocked_data.items()):
            channel_title, comment = channel_blocked_data['channelTitle'], channel_blocked_data['adminComment']
            text = f"{i + 1}. «<b>{channel_title}</b>»"
            if comment:
                text += f" ({comment})"
            blocked_data_text_list.append(text)
        await event.client.send_message(
            entity=event.chat_id,
            message="<u>Список заблокированных каналов в этом чате</u>:\n" + '\n'.join(blocked_data_text_list),
            parse_mode='html'
        )
    else:
        await event.client.send_message(event.chat_id, "В этом чате нет заблокированных каналов.")


@events.register(events.NewMessage(incoming=True, forwards=True))
async def delete_msg_handler(event: events.NewMessage.Event):
    try:
        from_channel_id = event.message.fwd_from.from_id.channel_id
    except AttributeError:
        pass
    else:
        current_chat_blocked_data = event.client.repo.get_channel_data(event.chat_id)

        if current_chat_blocked_data and from_channel_id in current_chat_blocked_data.keys():
            await event.message.delete()

            channel_blocked_data = current_chat_blocked_data[from_channel_id]
            channel_title, comment = channel_blocked_data['channelTitle'], channel_blocked_data['adminComment']

            notify_message = None
            if channel_title:
                notify_message = f"Сообщение от канала «**{channel_title}**» удалено."
            if comment:
                notify_message += f"\nПричина: **{comment}**"

            if notify_message:
                await event.client.send_message(event.chat_id, notify_message)
