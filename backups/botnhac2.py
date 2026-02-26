import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN_NHAC_1")

# Cấu hình Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Đổi prefix thành !2 để tránh trùng lặp hoàn toàn với Bot 1 nếu muốn xịn hơn, 
# hoặc giữ nguyên ! nhưng dùng check_channel để lọc.
bot = commands.Bot(command_prefix='!', intents=intents)

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# --- CẤU HÌNH RIÊNG CHO BOT 2 ---
TARGET_GUILD_NAME = "Hoang Cung Bo"
TARGET_CHANNEL_NAME = "🎵Nghe Nhạc Room 2"
# -------------------------------

current_song = None
is_repeat = False

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} (Bot 2) đã sẵn sàng!')
    
    # Tự động nhảy vào Room 2
    for guild in bot.guilds:
        if guild.name == TARGET_GUILD_NAME:
            channel = discord.utils.get(guild.voice_channels, name=TARGET_CHANNEL_NAME)
            if channel:
                await channel.connect()
                print(f"📍 Bot 2 đã vào {TARGET_CHANNEL_NAME}")

def is_room_2(ctx):
    """
    HÀM QUAN TRỌNG: Chỉ cho phép Bot 2 hoạt động 
    nếu Server là 'Hoang Cung Bo' VÀ Channel là '🎵Nghe Nhạc Room 2'
    """
    return ctx.guild.name == TARGET_GUILD_NAME and ctx.channel.name == TARGET_CHANNEL_NAME

@bot.command()
@commands.check(is_room_2) # Chỉ work trong Room 2
async def list2(ctx):
    embed = discord.Embed(
        title="🎵 Danh sách lệnh Bot nhạc 2",
        description="Hệ thống âm thanh Room 2 - Hoàng Cung",
        color=discord.Color.blue() # Đổi màu xanh cho khác Bot 1
    )
    embed.add_field(name="!play [tên/link]", value="Phát nhạc tại Room 2", inline=False)
    embed.add_field(name="!skip", value="Bỏ qua bài hiện tại", inline=False)
    embed.add_field(name="!stop", value="Dừng và xóa hàng đợi", inline=False)
    embed.add_field(name="!repeat", value="Bật/Tắt lặp lại", inline=False)
    embed.set_footer(text=f"📍 Chỉ hoạt động tại: {TARGET_CHANNEL_NAME}")
    
    await ctx.send(embed=embed)

@bot.command()
@commands.check(is_room_2)
async def play(ctx, *, search: str):
    global current_song
    voice_client = ctx.message.guild.voice_client

    if not voice_client:
        return # Im lặng nếu không ở trong voice

    async with ctx.typing():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
            current_song = {'url': search, 'title': title}

        def play_next(error):
            if is_repeat and current_song:
                bot.loop.create_task(play(ctx, search=current_song['url']))

        voice_client.stop()
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        voice_client.play(source, after=play_next)
        
    await ctx.send(f"🎶 [Room 2] Đang phát: **{title}**")

@bot.command()
@commands.check(is_room_2)
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ Bot 2 đã dừng nhạc.")

@bot.command()
@commands.check(is_room_2)
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Đã bỏ qua bài hiện tại (Bot 2).")

# Xử lý lỗi: Nếu nhắn sai channel, Bot 2 sẽ im lặng hoàn toàn
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return # Không làm gì cả, không nhắn bậy sang channel khác

bot.run(TOKEN)
