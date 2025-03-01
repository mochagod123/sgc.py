import discord
from discord import Webhook
import json
import aiohttp
import urllib

class SGC:
    def __init__(self, bot: discord.Client, demo_ch: discord.TextChannel = None):
        self.sgc_channel_id = 707158257818664991
        if not demo_ch:
            self.demo_sgc_channel_id = 707158343952629780
        else:
            self.demo_sgc_channel_id = demo_ch.id
        self.bot = bot
    
    async def make_json(self, message: discord.Message):
        dic = {}
        if message.reference:
            reference_msg = await message.channel.fetch_message(message.reference.message_id)
            reference_mid = 0
            if reference_msg.application_id == self.bot.user.id:
                arr = reference_msg.embeds[0].footer.text

                if "mID:" in arr:
                    reference_mid = arr.replace("mID:","",1)
            elif reference_msg.application_id != self.bot.user.id:
                reference_mid = reference_msg.id
            dic.update({"reference": str(reference_mid)})

        dic.update({"type": "message"})
        dic.update({"userId": str(message.author.id)})
        dic.update({"userName": message.author.name})
        dic.update({"x-userGlobal_name": message.author.global_name})
        dic.update({"userDiscriminator": message.author.discriminator})
        if hasattr(message.author.avatar, 'key'):
            dic.update({"userAvatar": message.author.avatar.key})
        else:
            dic.update({"userAvatar": None})
        dic.update({"isBot": message.author.bot})
        dic.update({"guildId": str(message.guild.id)})
        dic.update({"guildName": message.guild.name})
        if hasattr(message.guild.icon, 'key'):
            dic.update({"guildIcon": message.guild.icon.key})
        else:
            dic.update({"guildIcon": None})
        dic.update({"channelId": str(message.channel.id)})
        dic.update({"channelName": message.channel.name})
        dic.update({"messageId": str(message.id)})
        dic.update({"content": message.content.replace('@', '＠')})

        if message.attachments != []:
            arr = []
            for attachment in message.attachments:
                arr.append(attachment.url)
            dic.update({"attachmentsUrl": arr})

        jsondata = json.dumps(dic, ensure_ascii=False)
        return jsondata
        
    async def send_sgc(self, json: str):
        await self.bot.get_channel(self.sgc_channel_id).send(json)

    async def send_demo_sgc(self, json: str):
        await self.bot.get_channel(self.demo_sgc_channel_id).send(json)

    async def send_channel(self, session: aiohttp.ClientSession, channel: discord.TextChannel, message: discord.Message):
        if channel is None:
            return
        ch_webhooks = await channel.webhooks()
        whname = "Shark-Global-main"
        webhooks = discord.utils.get(ch_webhooks, name=whname)
        if webhooks is None:
            webhooks = await channel.create_webhook(name=whname)
        webhook = Webhook.from_url(webhooks.url, session=session)
        try:
            msg = discord.Embed(color=discord.Color.green()).set_footer(text=f"mID:{message.id}")
            if message.reference:
                try:
                    rmsg = await message.channel.fetch_message(message.reference.message_id)
                    msg.description = rmsg.content
                    msg.set_author(name=f"{rmsg.author.name} - {rmsg.author.id}")
                except:
                    pass
                if message.attachments:
                    msg.set_image(url=message.attachments[0].url)
            elif message.attachments:
                msg.set_image(url=message.attachments[0].url)
        except:
            return
        try:
            username = f"({message.author.name}/{message.author.id})({message.guild.name.lower().replace('discord', '*')})"
            content = message.content.replace("@", "＠")
            avatar_url = message.author.avatar.url if message.author.avatar else None
            await webhook.send(content, username=username, avatar_url=avatar_url, embed=msg)
        except:
            return
        
    async def send_channel_byjson(self, session: aiohttp.ClientSession, channel: discord.TextChannel, message: discord.Message, dic):
        if dic is None:
            return
        if channel is None:
            return
        ch_webhooks = await channel.webhooks()
        whname = "Shark-Global-main"
        webhooks = discord.utils.get(ch_webhooks, name=whname)
        if webhooks is None:
            webhooks = await channel.create_webhook(name=whname)
        webhook = Webhook.from_url(webhooks.url, session=session)
        msg = None
        try:
            reference_mid = dic.get("reference")
            reference_message_content = ""
            reference_message_author = ""
            past_dic = None
            async for past_message in message.channel.history(limit=1000):
                try:
                    past_dic = json.loads(past_message.content)
                except json.decoder.JSONDecodeError:
                    continue
                if "type" in past_dic and past_dic["type"] != "message":
                    continue
                if "messageId" not in past_dic:
                    continue
                if str(past_dic["messageId"]) == str(reference_mid):
                    reference_message_author = f"{past_dic['userName']}#{past_dic['userDiscriminator']}"
                    reference_message_content = past_dic["content"]
                    msg = discord.Embed(description=reference_message_content, color=discord.Color.green()).set_author(name=reference_message_author).set_footer(text=f"mID:{dic['messageId']}")
                    if "attachmentsUrl" in dic:
                        msg.set_image(url=urllib.parse.unquote(dic["attachmentsUrl"][0]))
                    break
        except:
            pass
        if msg is None:
            msg = discord.Embed(color=discord.Color.green()).set_footer(text=f"mID:{dic['messageId']}")
            if "attachmentsUrl" in dic:
                msg.set_image(url=urllib.parse.unquote(dic["attachmentsUrl"][0]))
        await webhook.send(
            dic["content"].replace("@", "＠"),
            avatar_url=f"https://media.discordapp.net/avatars/{dic['userId']}/{dic['userAvatar']}.png?size=1024",
            username=f"({dic['userName']}/{dic['userId']})({dic['guildName'].lower().replace('discord', '*')})",
            embed=msg
        )

    async def read_demo_sgc(self, message: discord.Message):
        if type(message.channel) == discord.DMChannel:
            return
        if message.channel.id == self.demo_sgc_channel_id:
            if message.author.id == self.bot.user.id:
                return
            try:
                dic = json.loads(message.content)
            except json.decoder.JSONDecodeError as e:
                return
            
            if "type" in dic and dic["type"] != "message":
                return
            
            return dic
        
    async def read_sgc(self, message: discord.Message):
        if type(message.channel) == discord.DMChannel:
            return
        if message.channel.id == self.sgc_channel_id:
            if message.author.id == self.bot.user.id:
                return
            try:
                dic = json.loads(message.content)
            except json.decoder.JSONDecodeError as e:
                return
            
            if "type" in dic and dic["type"] != "message":
                return
            
            return dic