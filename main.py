import logging
import re
import asyncio

from typing import Union, Optional, AsyncGenerator
from pyrogram import Client, filters, enums
from pyrogram import types
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from config import Config

lock = asyncio.Lock()

class Bot(Client):

    def __init__(self):
        super().__init__(
            name="bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=50,
            sleep_threshold=5,
        )

    async def start(self):
        await super().start()
        logging.info("Bot started")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")
    
    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1


bot = Bot()


@bot.on_message(filters.command("start") & filters.user(Config.OWNER_ID))
async def _start(c, m):
    await m.reply("Hey There, I'm Alive!")
    

@bot.on_message(filters.channel)
async def auto_delete(c, m):
    if m.chat.id != Config.AUTH_CHANNEL:
        return
    try:
        await m.forward(Config.LOG_CHANNEL)
        await m.delete()
    except bot_token as e:
        logging.exception(str(e))
        
        
@bot.on_message(filters.forwarded & filters.user(Config.OWNER_ID) & filters.private & filters.incoming)
async def _delete_all(bot, message):
    if message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.id
    else:
        return
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        logging.exception(e)
        return await message.reply(f'Errors - {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('Make Sure That Iam An Admin In The Channel, if channel is private')
        
    msg = await message.reply("starting...")
    await delete_all(int(last_msg_id), chat_id, msg, bot)
    
    
async def delete_all(lst_msg_id, chat, msg, bot):
    total_deleted = 0
    errors = 0
    async with lock:
        try:
            current = 0
            async for message in bot.iter_messages(chat, lst_msg_id, current):
                current += 1
                if current % 20 == 0:
                    await msg.edit_text(
                        text=f"Total messages fetched: <code>{current}</code>\nTotal messages Deleted: <code>{total_deleted}</code>\nErrors Occurred: <code>{errors}</code>"
                    )
                try:
                    await message.delete()
                    total_deleted += 1
                except Exception as er:
                    logging.exception(er)
                    errors += 1
        except Exception as e:
            logging.exception(e)
            await msg.edit(f'Error: {e}')
        else:
            await msg.edit(f'Succesfully Deleted <code>{total_deleted}</code> !\nErrors Occurred: <code>{errors}</code>')
    
    
    
bot.run()        
