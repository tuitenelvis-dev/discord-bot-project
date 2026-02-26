import discord
from discord.ext import commands
import yt_dlp
import asyncio

# --- CẤU HÌNH BOT 1 ---
TOKEN = 'TOKEN_BOT_1_CỦA_SẾP'
GUILD_NAME = "Hoang Cung Bo"
ROOM_NAME = "🎵Nghe Nhạc Room 1"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Cấu hình kỹ thuật cho Nhạc
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True', 'quiet': True}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Biến lưu trữ trạng thái
current_song = None
is_repeat = False

# Hàm kiểm tra Channel (Quan trọng để không bị x2 list)
def is_correct_room(ctx):
    return ctx.guild.name == GUILD_NAME and ctx.channel.name == ROOM_NAME

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} đang hoạt động tại {ROOM_NAME}')
    # Tự động vào room khi khởi động
    for guild in bot.guilds:
        if guild.name == GUILD_NAME:
            channel = discord.utils.get(guild.voice_channels, name=ROOM_NAME)
            if channel:
                await channel.connect()

@bot.command()
@commands.check(is_correct_room)
async def list1(ctx):
    embed = discord.Embed(title="🎵 Danh sách lệnh Bot nhạc 1", color=discord.Color.gold())
    embed.add_field(name="!play [tên/link]", value="Phát nhạc từ YouTube", inline=False)
    embed.add_field(name="!skip", value="Bỏ qua bài hiện tại", inline=False)
    embed.add_field(name="!stop", value="Dừng nhạc và thoát", inline=False)
    embed.add_field(name="!repeat", value="Bật/Tắt lặp lại bài hiện tại", inline=False)
    embed.set_footer(text=f"📍 Chỉ hoạt động tại: {ROOM_NAME}")
    await ctx.send(embed=embed)

@bot.command()
@commands.check(is_correct_room)
async def play(ctx, *, search: str):
    global current_song
    voice_client = ctx.voice_client

    if not voice_client:
        return await ctx.send("Bot chưa vào Voice Channel!")

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
                url = info['url']
                title = info['title']
                current_song = {'url': search, 'title': title}

            def play_next(error):
                if is_repeat and current_song:
                    bot.loop.create_task(play(ctx, search=current_song['url']))

            if voice_client.is_playing():
                voice_client.stop()

            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            voice_client.play(source, after=play_next)
            await ctx.send(f"🎶 **[Room 1]** Đang phát: `{title}`")
        except Exception as e:
            await ctx.send(f"❌ Lỗi: Không thể phát bài này. (Thử lại bài khác sếp nhé)")
            print(f"Lỗi Play: {e}")

@bot.command()
@commands.check(is_correct_room)
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ **[Bot 1]** Đã bỏ qua bài.")

@bot.command()
@commands.check(is_correct_room)
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ **[Bot 1]** Đã dừng nhạc.")

@bot.command()
@commands.check(is_correct_room)
async def repeat(ctx):
    global is_repeat
    is_repeat = not is_repeat
    await ctx.send(f"🔁 **[Bot 1]** Lặp lại: **{'BẬT' if is_repeat else 'TẮT'}**")

# Chống báo lỗi khi nhắn sai channel
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return 

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN_NHAC_3")

import os
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("TOKEN_NHAC_1")

bot.run(TOKEN)