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
        dic.update({"x-userGlobal_name": message.author.display_name})
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
        ch_webhooks = await channel.webhooks()
        whname = f"Shark-Global-main"
        webhooks = discord.utils.get(ch_webhooks, name=whname)
        if webhooks is None:
            webhooks = await channel.create_webhook(name=f"{whname}")
        webhook = Webhook.from_url(webhooks.url, session=session)
        try:
            if message.reference:
                if message.attachments == []:
                    try:
                        rmsg = await message.channel.fetch_message(message.reference.message_id)
                        msg = discord.Embed(description=rmsg.content, color=discord.Color.green()).set_author(name=f"{rmsg.author.name} - {rmsg.author.id}").set_footer(text=f"mID:{message.id}")
                    except:
                        msg = discord.Embed(color=discord.Color.green()).set_footer(text=f"mID:{message.id}")
                else:
                    try:
                        rmsg = await message.channel.fetch_message(message.reference.message_id)
                        msg = discord.Embed(description=rmsg.content, color=discord.Color.green()).set_author(name=f"{rmsg.author.name} - {rmsg.author.id}").set_footer(text=f"mID:{message.id}").set_image(url=message.attachments[0].url)
                    except:
                        msg = discord.Embed(color=discord.Color.green()).set_footer(text=f"mID:{message.id}").set_image(url=message.attachments[0].url)
            else:
                if message.attachments == []:
                    msg = discord.Embed(color=discord.Color.green()).set_footer(text=f"mID:{message.id}")
                else:
                    msg = discord.Embed(color=discord.Color.green()).set_footer(text=f"mID:{message.id}").set_image(url=message.attachments[0].url)
        except:
            return
        try:
            if message.author.avatar == None:
                await webhook.send(f"{message.content.replace('@', '＠')}", username=f"({message.author.name}/{message.author.id})({message.guild.name.lower().replace("discord", "*")})", embed=msg)
            else:
                await webhook.send(f"{message.content.replace('@', '＠')}", avatar_url=message.author.avatar.url, username=f"({message.author.name}/{message.author.id})({message.guild.name.lower().replace("discord", "*")})", embed=msg)
        except:
            return
        
    async def send_channel_byjson(self, session: aiohttp.ClientSession, channel: discord.TextChannel, message: discord.Message, dic):
        if dic is None:
            return
        ch_webhooks = await channel.webhooks()
        whname = f"Shark-Global-main"
        webhooks = discord.utils.get(ch_webhooks, name=whname)
        if webhooks is None:
            webhooks = await channel.create_webhook(name=f"{whname}")
        webhook = Webhook.from_url(webhooks.url, session=session)
        if message.reference:
            try:
                rmsg = await message.channel.fetch_message(message.reference.message_id)
                msg = discord.Embed(description=rmsg.content, color=discord.Color.green()).set_author(name=f"{rmsg.author.name} - {rmsg.author.id}")
            except:
                msg = None
        else:
                
            try:
                reference_mid = dic["reference"] #返信元メッセージID

                reference_message_content = "" #返信元メッセージ用変数を初期化
                reference_message_author = "" #返信元ユーザータグ用変数を初期化
                past_dic = None #返信元メッセージの辞書型リスト用変数を初期化
                async for past_message in message.channel.history(limit=1000): #JSONチャンネルの過去ログ1000件をループ
                    try: #JSONのエラーを監視
                        past_dic = json.loads(past_message.content) #過去ログのJSONを辞書型リストに変換
                    except json.decoder.JSONDecodeError as e: #JSON読み込みエラー→そもそもJSONでは無い可能性があるのでスルー
                        continue
                    if "type" in past_dic and past_dic["type"] != "message": #メッセージでは無い時はスルー
                        continue

                    if not "messageId" in past_dic: #キーにメッセージIDが存在しない時はスルー
                        continue
                                    
                    if str(past_dic["messageId"]) == str(reference_mid): #過去ログのメッセージIDが返信元メッセージIDと一致したとき
                        reference_message_author = "{}#{}".format(past_dic["userName"],past_dic["userDiscriminator"]) #ユーザータグを取得
                        reference_message_content = past_dic["content"] #メッセージ内容を取得
                        try:
                            if not "attachmentsUrl" in dic:
                                msg = discord.Embed(description=reference_message_content, color=discord.Color.green()).set_author(name=reference_message_author).set_footer(text=f"mID:{dic["messageId"]}")
                            else:
                                msg = discord.Embed(description=reference_message_content, color=discord.Color.green()).set_author(name=reference_message_author).set_footer(text=f"mID:{dic["messageId"]}").set_image(url=urllib.parse.unquote(dic["attachmentsUrl"][0]))
                                break
                        except:
                            msg = discord.Embed(description=reference_message_content, color=discord.Color.green()).set_author(name=reference_message_author).set_footer(text=f"mID:{dic["messageId"]}")
            except:
                try:
                    if not "attachmentsUrl" in dic:
                        msg = discord.Embed(color=discord.Color.green()).set_footer(text=f"mID:{dic["messageId"]}")
                    else:
                        msg = discord.Embed(color=discord.Color.green()).set_footer(text=f"mID:{dic["messageId"]}").set_image(url=urllib.parse.unquote(dic["attachmentsUrl"][0]))
                except:
                    msg = discord.Embed(color=discord.Color.green()).set_footer(text=f"mID:{dic["messageId"]}")
        await webhook.send(f"{dic["content"].replace('@', '＠')}", avatar_url="https://media.discordapp.net/avatars/{}/{}.png?size=1024".format(dic["userId"], dic["userAvatar"]), username=f"({dic["userName"]}/{dic["userId"]})({dic["guildName"].lower().replace("discord", "*")})", embed=msg)

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