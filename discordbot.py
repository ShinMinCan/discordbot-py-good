from cmath import log
from distutils.sysconfig import PREFIX
import discord
from dotenv import load_dotenv
import os
import datetime
import json
load_dotenv()

PREFIX = os.environ['PREFIX']
TOKEN = os.environ['TOKEN']

client = discord.Client()
DATABASE_PATH = 'check.json'

roles = [
    {'role_id': '1095420983483039786', 'count': 1},
    {'role_id': '1010603908793638913', 'count': 5},
    {'role_id': '1010604059071361095', 'count': 10},
    {'role_id': '1010613230932074616', 'count': 20},
    {'role_id': '1010614551663890452', 'count': 30},
    {'role_id': '1010614627413020783', 'count': 50},
    {'role_id': '1010615035493634058', 'count': 100},
    {'role_id': '1010617071845003304', 'count': 300}
]

prefixes = [
    {'prefix': '🥺┃', 'count': 1},
    {'prefix': '🙂┃', 'count': 5},
    {'prefix': '🤪┃', 'count': 10},
    {'prefix': '🤑┃', 'count': 20},
    {'prefix': '🟩┃', 'count': 30},
    {'prefix': '🟨┃', 'count': 50},
    {'prefix': '🟥┃', 'count': 100},
    {'prefix': '💠┃', 'count': 300}
]


def read_database():
    try:
        with open(DATABASE_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

def write_database(data):
    with open(DATABASE_PATH, 'w') as f:
        json.dump(data, f)
@client.event
async def on_ready():
    print('Bot is ready')
    
@client.event
async def on_message(message):
    # 채널 ID를 여기에 입력합니다.
    channel_id = 1095436552789823528
    # 채널 ID가 일치하지 않으면 메시지를 처리하지 않습니다.
    if message.channel.id != channel_id:
        return
    
    if message.content.startswith('!출석'):
        author_id = str(message.author.id)
        database = read_database()

        if author_id in database:
            last_attendance = database[author_id]['last_attendance']
            if datetime.date.today() == datetime.datetime.strptime(last_attendance, '%Y-%m-%d').date():
                # 이미 출석체크를 한 경우
                await message.channel.send(f'{message.author.mention} 오늘은 이미 출석체크를 하셨습니다.')
                return
            attendance_count = database[author_id]['attendance_count']
        else:
            database[author_id] = {}
            attendance_count = 0

        attendance_count += 1
        database[author_id]['attendance_count'] = attendance_count
        database[author_id]['last_attendance'] = str(datetime.date.today())
        write_database(database)
        await message.channel.send(f'{message.author.mention} 출석체크 완료! 현재까지 출석체크 횟수: {attendance_count}회')

        # 출석 횟수에 따라 역할 부여
        for role in roles:
            if attendance_count == role['count']:
                guild = message.guild
                role_id = role['role_id']
                target_role = guild.get_role(int(role_id))
                if target_role is not None:
                    await message.author.add_roles(target_role)
                    await message.channel.send(f'{message.author.mention} 출석체크 {attendance_count}회 달성! {target_role.name} 역할이 부여되었습니다.')
                else:
                    await message.channel.send(f'{message.author.mention} 출석체크 {attendance_count}회 달성! {role_id}에 해당하는 역할을 찾을 수 없습니다.')
                    
        # 출석 횟수에 따라 이름에 접두사 부여
        for prefix in prefixes:
            if attendance_count == prefix['count']:
                guild = message.guild
                member = message.author
                new_name = f"{prefix['prefix']} {member.name}"
                try:
                    await member.edit(nick=new_name)
                    await message.channel.send(f'{member.mention} 출석체크 {attendance_count}회 달성! 이름이 변경되었습니다.')
                except discord.errors.Forbidden:
                    await message.channel.send(f'{member.mention} 출석체크 {attendance_count}회 달성! 이름 변경 권한이 없습니다.')
    elif not message.author.bot:
        # 봇이 보내는 메시지가 아닌 경우에만 삭제
        await message.delete()

try:
    client.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Improper token has been passed.")
