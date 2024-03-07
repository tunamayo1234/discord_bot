import discord
from discord.ext import tasks
import datetime
import os 
from discord.utils import get
import random
import sys
import requests
from bs4 import BeautifulSoup
import traceback
from valorant import*
import asyncio

DISCORD_BOT_TOKEN = os.environ["DISCORD_TOKEN"]
bot_message_channel_id = int(os.environ["bot_message_channel_id"])
bot_id = int(os.environ["bot_id"])
callHour = int(os.environ["callHour"])
callMinutes = int(os.environ["callMinutes"])
howmany_10pm = int(os.environ["howmany_10pm"])
api_key = os.environ["art3"]
serverID = int(os.environ["SERVER_ID"])
client = discord.Client()
onetimeRefresh = False
onetimeRemoveO = True
onetimeRemoveX = True
reactlist = []
denylist = []
stop304 = False
onetm = True
ok_emoji = "⭕"
no_emoji = "❌"
onetimeEveryone = True
error_message = ""
join_list = []
class FILEIO:
    def __init__(self,filename):
        self.filename = filename
    def list_writer(self,save_list):
        with open(self.filename, 'w') as file:
            for column in save_list:
                file.write(str(column) + '\n')
    def list_reader(self):
        int_list = []
        with open(self.filename, 'r') as file:
            for column in file:
                int_list.append(int(column.strip()))
            print(f"{self.filename}を読み込みました: {int_list}")
            return int_list
    def deleter(self):
        with open(self.filename, 'w') as file:
          pass
        
@client.event
async def on_ready():
  try:
    global bot_message_id
    global reactlist 
    global denylist
    print('ログインしました')
    message_edit_resume = FILEIO("sample.txt")
    oklist_resume = FILEIO("ok_react.txt")
    nolist_resume = FILEIO("no_react.txt")
    bot_message_id_list = message_edit_resume.list_reader()
    bot_message_id = bot_message_id_list[0]
    reactlist = oklist_resume.list_reader()
    denylist = nolist_resume.list_reader()
    send_message.start()
    read_default_react()
  except Exception as e:
            print("Error occurred at on_ready:", e)
            traceback.print_exc()

async def default_react(person):
    global sheredefault
    sheredefault.append(person)
    file_io = FILEIO('default_reaction.txt')
    file_io.list_writer(sheredefault)
    read_default_react()
    await edit_message()

def default_react_remove(remsg):
    global denylist
    file_io = FILEIO('default_reaction.txt')
    string_default = file_io.list_reader()
    if remsg in string_default:
        string_default.remove(remsg)
        file_io.list_writer(string_default)
    if remsg in denylist:
        denylist.remove(remsg)
        file_io = FILEIO('no_react.txt')
        file_io.list_writer(denylist)
    read_default_react()

def read_default_react():
    global denylist
    global sheredefault
    file_io = FILEIO('default_reaction.txt')
    string_default = file_io.list_reader()
    sheredefault = string_default
    print(f"読み込んだデフォルト拒否リスト: {string_default}")
    string_default = list(map(int, string_default))
    new_items = [item for item in string_default if item not in denylist]
    denylist.extend(new_items)
    file_io = FILEIO('no_react.txt')
    file_io.list_writer(denylist)

@client.event
async  def on_message(message):
    global stop304
    global bot_message_id
    global message_weather
    global messageID
    message_weather =""
    global message_catgpt
    if message.content == ("cat.default"):
        await default_react(message.author.id)
        print(f"set{message.author.id}as default react list")
        await message.channel.send("ついかしたにゃ")
    #
    if message.content == ("cat.default.remove"):
        default_react_remove(message.author.id)
        print(f"remove{message.author.id}in default react list")
        await message.channel.send("とりけしたにゃ")
    #   
    if message.content.startswith("catenki."):
        
        message_weather = message.content
        messageID = message
        print(message.author,message.content)
        await send_weather()
    #
    if message.content.startswith("@every-one !"): 
        p = open('sample.txt', 'r')
        global bot_message_id  
        guild_id = serverID
        guild = client.get_guild(guild_id)
        channel = guild.get_channel(bot_message_channel_id)
        Dmessage = await channel.fetch_message(bot_message_id)
        print(Dmessage)
        await Dmessage.delete()
        bot_message_id = message.id
        with open("sample.txt", "w+") as p:
            p.seek(0)
            p.write(str(message.id))
            p.seek(0)
            print(f"新規メッセージを取得して{p.read()}にbot_message_idが更新されました")
    channel = message.channel
    if message.content.startswith("@every-one !"): 
        await message.add_reaction('⭕')
        await message.add_reaction('❌')

@tasks.loop(seconds = 20) 
async def send_message():
    global bot_message_channel_id
    global onetimeEveryone ,onetimeRemoveO,onetimeRemoveX
    global onetimeRefresh
    global callHour,callMinutes
    now = datetime.datetime.now()
    channel = client.get_channel(bot_message_channel_id)
    try:
        if now.hour == callHour and now.minute == callMinutes and onetimeEveryone:
            await channel.send("@every-one ! \n ")
            onetimeEveryone = False   
        if now.hour == callHour and now.minute == (callMinutes - 6):
            onetimeRefresh = True
        if now.hour == 0 and now.minute == 25:
            print("refreshed")
            refresh_oklist = FILEIO("ok_react.txt")
            refresh_nolist = FILEIO("no_react.txt")
            refresh_oklist.deleter()
            refresh_nolist.deleter()
            await sys.exit()
        await edit_message()
    except Exception as e:
            print("Error occurred at send_message:", e)
            traceback.print_exc()
          
@client.event
async def on_raw_reaction_add(payload):
    try:
      global reactlist
      global name
      global onetimeRemoveO
      global onetimeRemoveX
      global bot_id
      global denylist
      now = datetime.datetime.now()
      if payload.member.name != "cat.basic":
        if payload.message_id == bot_message_id:
            if str(payload.emoji) != no_emoji:
                print(f"{now}時に{payload.member.name}がOリアクションしました")
                reactlist.append(payload.user_id)
                save_oklist = FILEIO("ok_react.txt")
                save_oklist.list_writer(reactlist)
            elif str(payload.emoji) == no_emoji:
                denylist.append(payload.user_id)
                save_nolist = FILEIO("no_react.txt")
                save_nolist.list_writer(denylist)
                print(f"{now}時に{payload.member.name}がXリアクションしました")
        await edit_message()
    except discord.errors.HTTPException as e:
        if e.status == 429:
            print("on_raw_reaction_add:レートリミットに達しました。後ほど再試行します。")
        else:
            raise
@client.event
async def on_raw_reaction_remove(payload):
  try:
    guild = client.get_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)
    now = datetime.datetime.now()
    if payload.message_id == bot_message_id:
        if str(payload.emoji) != no_emoji:
            
            print(f"{now}時に{member.name}がbotのコメントのOリアクションを削除しました")
            reactlist.remove(payload.user_id)
            save_oklist = FILEIO("ok_react.txt")
            save_oklist.list_writer(reactlist)
    if payload.message_id == bot_message_id:
        if str(payload.emoji) == no_emoji:   
            denylist.remove(payload.user_id)
            save_nolist = FILEIO("no_react.txt")
            save_nolist.list_writer(denylist)
            print(f"{now}時に{member.name}がbotのコメントのXリアクションを削除しました")
    await edit_message()
  except discord.errors.HTTPException as e:
        if e.status == 429:
            print("on_raw_reaction_remove:レートリミットに達しました。後ほど再試行します。")
        else:
            raise
async def edit_message():
  try:
    global join_list
    global reactlist
    global notjoin_list
    global error_message
    channel = client.get_channel(bot_message_channel_id)
    message = await channel.fetch_message(bot_message_id)
    await get_reaction_count()
    num_to_str = {907617707996876813:"cappisub",1080489193236594721:"かぴ",802525935105736754:"1rappy",1178287752840753162:"cat.basic",790130065261592577:"aiueo",939562255291412520:"aimisbokko",746254144276398083:"Diablo",475530091699634186:"soso",433253570662367252:"UMARU",873847008375500800:"Tsuki",481672483758669844:"とかちさん",963432252241485854:"べちょ",672095682953216051:"クリアアサヒ",1181504046436196414:"cat.test"}
    now = datetime.datetime.now()
    join_list = [num_to_str[num] for num in reactlist]
    notjoin_list = [num_to_str[nim] for nim in denylist] 
    if (message.content.startswith("@everyone !") or message.content.startswith("@every-one !"))  and now.hour <13:
        if len(reactlist) == 0 and len(denylist) != 0:
            await message.edit(content=f"@everyone ! 10時~\n9時以降で5人以上集まったら呼びますにゃ!  \n ----------\n🚫__不参加の{len(denylist)}人⇒{notjoin_list}__\n ---------- \n({now.hour+9}時{now.minute}分)\n{error_message}")
        elif len(reactlist) == 0 and len(denylist) == 0: 
            await message.edit(content=f"@everyone ! 10時~\n9時以降で5人以上集まったら呼びますにゃ!\n({now.hour+9}時{now.minute}分)\n{error_message}")
        elif len(reactlist) != 0 and len(denylist) ==0:
            await message.edit(content=f"@everyone ! 10時~\n9時以降で5人以上集まったら呼びますにゃ!  \n ----------\n🌟**__参加する{len(reactlist)}人⇒{join_list}__**\n ---------- \n({now.hour+9}時{now.minute}分)\n{error_message}")
        else  :
            await message.edit(content=f"@everyone ! 10時~\n9時以降で5人以上集まったら呼びますにゃ! \n ----------\n🌟**__参加する{len(reactlist)}人⇒{join_list}__**\n🚫__不参加の{len(denylist)}人⇒{notjoin_list}__\n ---------- \n({now.hour+9}時{now.minute}分)\n{error_message}") 
    if 20 >= now.hour >= 13:
        valorant_news = "```" + valorant() + "```"
        get_weather = GetYahooWeather("13","4410")
        if now.hour <=15:
            messages = (f"もう{now.hour-3}時{now.minute}分なので寝ます。")   
        if now.hour > 15 :
            messages = (f"もう{now.hour-15}時{now.minute}分なので寝ます。") 
        messages += "\n"+"```　<東京の天気です>"+"\n"+get_weather + error_message+valorant_news
        await message.edit(content=messages)
        return
    if 24 >now.hour >=21:
        adfsd = GetYahooWeather("13","4410")
        await message.edit(content=f"おはようございます！\n📍東京の天気です \n {adfsd}")
  except Exception as e:
            error_message = str(e)
            error_message = "```" + error_message   + "```"
            print("Error occurred at edit_message:", e) 
            await asyncio.sleep(300)
            error_message = ""
            print("error message deleted")

async def get_reaction_count():
    global stop304
    global howmany_10pm
    global join_list
    num_to_str = {456:"まだ参加できる人は「@everyone 10時~」のメッセージのほうにリアクションしてください(めんどくさいのでリストは更新されません)",907617707996876813:"cappisub",1080489193236594721:"かぴ",802525935105736754:"1rappy",1178287752840753162:"cat.basic",790130065261592577:"aiueo",939562255291412520:"aimisbokko",746254144276398083:"Diablo",475530091699634186:"soso",433253570662367252:"UMARU",873847008375500800:"Tsuki",481672483758669844:"とかちさん",963432252241485854:"あぺくすぼしゅう",672095682953216051:"クリアアサヒ",1181504046436196414:"cat.test"}
    now = datetime.datetime.now()
    await asyncio.sleep(5)
    join_list = [num_to_str[num] for num in reactlist]
    notjoin_list = [num_to_str[nim] for nim in denylist] 
    channel = client.get_channel(bot_message_channel_id)
    now = datetime.datetime.now()
    message = await channel.fetch_message(bot_message_id)
    if len(reactlist) >=howmany_10pm and stop304 != True and (13>=now.hour>=12 ):
        if len(reactlist) == 5:
            await message.channel.send(f"@everyone may🐝10時~ \n 🌟**__参加する人⇒{join_list}__**(まだ参加できます!)")
        elif len(reactlist) ==6:
            number = random.randrange(5)
            await message.channel.send(f"@everyone may🐝10時~ \n 🌟**__参加する人⇒{join_list}__**(まだ参加できます!)\n```6人なので勝手に抽選します\n本日参加できないのはリスト{number+1}番目の{join_list[number]}さんです!```")
        elif len(reactlist) >=7:    
            number = random.randrange(6)
            number2 = random.randrange(6)
            if number == number2:
                number = random.randrange(6)
                number2 = random.randrange(6)
            await message.channel.send(f"@everyone may🐝10時~ \n 🌟**__参加する人⇒{join_list}__**(まだ参加できます!)\n**7人なので勝手に抽選します**\n本日参加できないのは{join_list[number]}さんと{join_list[number2]}さんです!")
        stop304 = True

def GetYahooWeather(PreCode,AreaCode):
    if PreCode == 1:
      a = str(PreCode) + "b"
    else :
      a = str(PreCode)
    url = "https://weather.yahoo.co.jp/weather/jp/"+a+"/" + str(AreaCode) + ".html"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    rs = soup.find(class_='forecastCity')
    rs = [i.strip() for i in rs.text.splitlines()]
    rs = [i for i in rs if i != ""]
    ls = soup.find(class_= "yjw_main_md target_modules")
    ls = [p.strip() for p in ls.text.splitlines()]
    ls = [p for p in ls if  p!= "" and p!= ","]
    unb = soup.find(class_= "tabView_content")
    unb = [z.strip() for z in unb.text.splitlines()]
    unb = [z for z in unb if  z!= "" and z!= ","]
    cl = soup.find(class_= "indexList_item indexList_item-clothing")
    cl = [q.strip() for q in cl.text.splitlines()]
    cl = [q for q in cl if  q!= "" and q!= ","]  
    dt = soup.find(class_= "yjSt yjw_note_h2")
    dt = [qs.strip() for qs in dt.text.splitlines()]
    dt = [qs for qs in dt if  qs!= "" and qs!= ","]
    a, b, c, d, e, f, g = get_random_pokemon_info()  
    nrs = [None] * len(rs)
    nrs[2] = rs[2].split("℃")[0]
    nrs[3] = rs[3].split("℃")[0]
    nrs[20] = rs[20].split("℃")[0]
    nrs[21] = rs[21].split("℃")[0]
    nrs[23] = rs[23].split("℃")[0]
    nrs[22] = rs[22].split("℃")[0]
    weather_data = [
    ("今日", rs[1], nrs[2], nrs[3]),
    ("明日", rs[19], nrs[20], nrs[21]),
    ("明後日",ls[15],ls[23],ls[22])  ,
    ]
    text = create_discord_weather_message(weather_data)
    text2 = f"``````🌟{join_list}\n🚫{notjoin_list}```"
    text3 = text + text2
    return text3
def create_discord_weather_message(data):
    header = "|　　　| 天気　　　|最高気温|最低気温 |"
    line = "|" + "-" * (len(header)+9 ) + "　|"
    message = line + "\n" + header + "\n" + line + "\n"
    for day, weather, high, low in data:
        day_field = f"|{day}" + "　" * (3 - len(day))
        weather_field = f"| {weather}" + "　" * (5 - len(weather))
        high_field = f"|　{high}℃" + " " * (4 - len(high) )
        low_field = f"|　{low}℃" + " " * (4 - len(low) )
        message += f"{day_field}{weather_field}{high_field}{low_field}|\n"
    message += line 
    return message

japan_cities0 = {
    "北海道": 1, "青森": 2, "岩手": 3, "宮城": 4, "秋田": 5,
    "山形": 6, "福島": 7, "茨城": 8, "栃木": 9, "群馬": 10,
    "埼玉": 11, "千葉": 12, "東京": 13, "神奈川": 14, "新潟": 15,
    "富山": 16, "石川": 17, "福井": 18, "山梨": 19, "長野": 20,
    "岐阜": 21, "静岡": 22, "愛知": 23, "三重": 24, "滋賀": 25,
    "京都": 26, "大阪": 27, "兵庫": 28, "奈良": 29, "和歌山": 30,
    "鳥取": 31, "島根": 32, "岡山": 33, "広島": 34, "山口": 35,
    "徳島": 36, "香川": 37, "愛媛": 38, "高知": 39, "福岡": 40,
    "佐賀": 41, "長崎": 42, "熊本": 43, "大分": 44, "宮崎": 45,
    "鹿児島": 46, "沖縄": 47
}
japan_cities = {
    "北海道": 1400, "青森": 3110, "岩手": 3310, "宮城": 3410, "秋田": 3210, "山形": 3510, "福島": 3610, "茨城": 4010,
    "栃木": 4110, "群馬": 4210, "埼玉": 4310, "千葉": 4510, "東京": 4410, "神奈川": 4610, "新潟": 5410, "富山": 5510,
    "石川": 5610, "福井": 5710, "山梨": 4910, "長野": 4810, "岐阜": 5210, "静岡": 5010, "愛知": 5110, "三重": 5310,
    "滋賀": 6010, "京都": 6110, "大阪": 6200, "兵庫": 6310, "奈良": 6410, "和歌山": 6510, "鳥取": 6910, "島根": 6810,
    "岡山": 6610, "広島": 6710, "山口": 8110, "徳島": 7110, "香川": 7200, "愛媛": 7310, "高知": 7410, "福岡": 8210,
    "佐賀": 8510, "長崎": 8410, "熊本": 8610, "大分": 8310, "宮崎": 8710, "鹿児島": 8810, "沖縄": 9110
}
async def send_weather():
    global message_weather
    global messageID
    parts = message_weather.split('.')
    city_name = parts[1] if len(parts) > 1 else None
    city_code = japan_cities.get(city_name)
    city_code0 = japan_cities0.get(city_name)
    if city_code:
        weather_info = GetYahooWeather(city_code0,city_code)
        await messageID.channel.send(f"📍{parts[1]}の天気です。 \n {weather_info}")
    else:
        await messageID.channel.send("都道府県名に誤りがあります。 \n 例): catenki.青森")
"""POKEMON"""
def get_japanese_name(url):
    response = requests.get(url)
    if response.status_code == 200:
        for name in response.json()['names']:
            if name['language']['name'] == 'ja':
                return name['name']
    return None
def get_random_pokemon_info():
    url = "https://pokeapi.co/api/v2/pokemon/"
    response = requests.get(url + str(random.randint(1, 898)))
    if response.status_code != 200:
        return "Error: Failed to retrieve data"
    data = response.json()
    pokemon = get_japanese_name(data["species"]["url"])
    pokemon_abilities = [get_japanese_name(ability["ability"]["url"]) for ability in data["abilities"]]
    pokemon_moves = [get_japanese_name(move["move"]["url"]) for move in data["moves"]]
    pokemon_height = data["height"]
    pokemon_weight = data["weight"]
    pokemon_types = [get_japanese_name(ptype["type"]["url"]) for ptype in data["types"]]
    pokemon_image = data["sprites"]["front_default"]
    return pokemon, pokemon_abilities, pokemon_moves, pokemon_height, pokemon_weight, pokemon_types, pokemon_image
client.run(DISCORD_BOT_TOKEN)
