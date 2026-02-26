import discord
from discord.ext import commands
import yt_dlp
import asyncio

# ==========================
# CẤU HÌNH BOT 1
# ==========================
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN_NHAC_1")

SERVER_ID = 1413966849053294634   # ID server Hoàng Cung
VOICE_CHANNEL_ID = 1474786871400861828  # Room Nhạc 1
TEXT_CHANNEL_NAME = "🎵nghe-nhạc-room-1"  # Tên channel chat nhạc 1

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================
# CẤU HÌNH NHẠC
# ==========================
YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": "True",
    "quiet": True
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

queue = []
current_song = None
is_repeat = False


# ==========================
# CHỈ CHO PHÉP BOT HOẠT ĐỘNG ĐÚNG PHÒNG
# ==========================
def is_correct_room(ctx):
    return (
        ctx.guild.id == SERVER_ID and
        ctx.channel.name == TEXT_CHANNEL_NAME
    )


# ==========================
# BOT READY → TỰ JOIN VOICE
# ==========================
@bot.event
async def on_ready():
    print(f"🎵 Bot Nhạc 1 đã online!")

    guild = bot.get_guild(SERVER_ID)
    if guild:
        channel = guild.get_channel(VOICE_CHANNEL_ID)
        if channel:
            try:
                await channel.connect()
                print("Đã vào voice channel Room 1")
            except:
                pass


# ==========================
# LỆNH LIST
# ==========================
@bot.command()
@commands.check(is_correct_room)
async def list1(ctx):
    embed = discord.Embed(title="🎵 Danh sách lệnh Bot Nhạc 1", color=discord.Color.gold())
    embed.add_field(name="!play [tên/link]", value="Phát nhạc", inline=False)
    embed.add_field(name="!add [tên/link]", value="Thêm bài vào danh sách phát", inline=False)
    embed.add_field(name="!skip", value="Bỏ qua bài hiện tại", inline=False)
    embed.add_field(name="!stop", value="Dừng nhạc", inline=False)
    embed.add_field(name="!repeat", value="Bật/Tắt lặp lại bài", inline=False)
    embed.add_field(name="!queue", value="Xem danh sách phát", inline=False)
    embed.set_footer(text="📍 Chỉ hoạt động tại Room Nhạc 1")
    await ctx.send(embed=embed)


# ==========================
# HÀM PHÁT NHẠC
# ==========================
async def play_song(ctx, url):
    global current_song

    voice = ctx.voice_client
    if not voice:
        return await ctx.send("Bot chưa vào voice!")

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]
        title = info["title"]
        current_song = {"url": url, "title": title}

    source = await discord.FFmpegOpusAudio.from_probe(audio_url, **FFMPEG_OPTIONS)

    def after_play(err):
        if is_repeat:
            bot.loop.create_task(play_song(ctx, current_song["url"]))
        else:
            if queue:
                next_url = queue.pop(0)
                bot.loop.create_task(play_song(ctx, next_url))

    voice.play(source, after=after_play)
    await ctx.send(f"🎶 Đang phát: **{title}**")


# ==========================
# LỆNH PLAY
# ==========================
@bot.command()
@commands.check(is_correct_room)
async def play(ctx, *, search):
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)["entries"][0]
        url = info["webpage_url"]

    await play_song(ctx, url)


# ==========================
# LỆNH ADD QUEUE
# ==========================
@bot.command()
@commands.check(is_correct_room)
async def add(ctx, *, search):
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)["entries"][0]
        url = info["webpage_url"]
        title = info["title"]

    queue.append(url)
    await ctx.send(f"➕ Đã thêm vào danh sách: **{title}**")


# ==========================
# LỆNH QUEUE
# ==========================
@bot.command()
@commands.check(is_correct_room)
async def queue(ctx):
    if not queue:
        return await ctx.send("📭 Danh sách phát trống!")

    msg = "**📜 Danh sách phát:**\n"
    for i, url in enumerate(queue, start=1):
        msg += f"{i}. {url}\n"

    await ctx.send(msg)


# ==========================
# LỆNH SKIP
# ==========================
@bot.command()
@commands.check(is_correct_room)
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Đã bỏ qua bài.")


# ==========================
# LỆNH STOP
# ==========================
@bot.command()
@commands.check(is_correct_room)
async def stop(ctx):
    queue.clear()
    if ctx.voice_client:
        ctx.voice_client.stop()
    await ctx.send("⏹️ Đã dừng nhạc.")


# ==========================
# LỆNH REPEAT
# ==========================
@bot.command()
@commands.check(is_correct_room)
async def repeat(ctx):
    global is_repeat
    is_repeat = not is_repeat
    await ctx.send(f"🔁 Lặp lại: **{'BẬT' if is_repeat else 'TẮT'}**")


# ==========================
# CHẶN LỆNH SAI CHANNEL
# ==========================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return


bot.run(TOKEN)
