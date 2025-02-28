import sgc
import discord
from discord.ext import commands
import asyncio
import aiohttp

bot = commands.Bot(command_prefix="sgc!", intents=discord.Intents.all())

sgc_ = sgc.SGC(bot)

channel = [1344926367447388200]

@bot.event
async def on_message(message: discord.Message):
    if message.channel.id == sgc_.demo_sgc_channel_id:
        if message.author.id == bot.user.id:
            return
        dic = await sgc_.read_demo_sgc(message)
        for ch in channel:
            async with aiohttp.ClientSession() as session:
                await sgc_.send_channel_byjson(session, bot.get_channel(ch), message, dic)
                await asyncio.sleep(2)
        return
    if not message.channel.id in channel:
        return
    if message.author.bot:
        return
    js = await sgc_.make_json(message)
    for ch in channel:
        if ch == message.channel.id:
            continue
        async with aiohttp.ClientSession() as session:
            await sgc_.send_channel(session, bot.get_channel(ch), message)
            await asyncio.sleep(2)
    await sgc_.send_demo_sgc(js)
    return

bot.run("")