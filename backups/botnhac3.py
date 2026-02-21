import discord
from discord.ext import commands
import yt_dlp
import asyncio

# --- CẤU HÌNH RIÊNG CHO BOT 3 ---
TOKEN = 'TOKEN_BOT_3_CỦA_SẾP' # Thay token chuẩn của Bot 3 vào đây
GUILD_NAME = "Hoang Cung Bo"
ROOM_NAME = "🎵Nghe Nhạc Room 3"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Thông số kỹ thuật âm thanh
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True', 'quiet': True}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

current_song = None
is_repeat = False

# Hàm kiểm tra chỉ hoạt động trong Room 3
def is_correct_room(ctx):
    return ctx.guild.name == GUILD_NAME and ctx.channel.name == ROOM_NAME

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} (Bot 3) đã sẵn sàng tại {ROOM_NAME}')
    # Tự động kết nối vào Voice Channel khi khởi động
    for guild in bot.guilds:
        if guild.name == GUILD_NAME:
            channel = discord.utils.get(guild.voice_channels, name=ROOM_NAME)
            if channel:
                await channel.connect()

@bot.command()
@commands.check(is_correct_room)
async def list3(ctx):
    embed = discord.Embed(
        title="🎵 Danh sách lệnh Bot nhạc 3", 
        description="Hệ thống âm thanh chuyên dụng cho Room 3",
        color=discord.Color.green()
    )
    embed.add_field(name="!play [tên/link]", value="Phát nhạc từ YouTube", inline=False)
    embed.add_field(name="!skip", value="Bỏ qua bài hiện tại", inline=False)
    embed.add_field(name="!stop", value="Dừng nhạc và nghỉ ngơi", inline=False)
    embed.add_field(name="!repeat", value="Bật/Tắt lặp lại bài hát", inline=False)
    embed.set_footer(text=f"📍 Chỉ hoạt động tại: {ROOM_NAME}")
    await ctx.send(embed=embed)

@bot.command()
@commands.check(is_correct_room)
async def play(ctx, *, search: str):
    global current_song
    if not ctx.voice_client:
        return await ctx.send("Bot 3 chưa vào Voice Channel!")

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
                url, title = info['url'], info['title']
                current_song = {'url': search, 'title': title}

            def play_next(error):
                if is_repeat and current_song:
                    bot.loop.create_task(play(ctx, search=current_song['url']))

            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()

            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=play_next)
            await ctx.send(f"🎶 **[Room 3]** Đang phát: `{title}`")
        except Exception as e:
            print(f"Lỗi: {e}")
            await ctx.send("❌ Bot 3 gặp lỗi khi tải nhạc!")

@bot.command()
@commands.check(is_correct_room)
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ **[Bot 3]** Đã bỏ qua bài hiện tại.")

@bot.command()
@commands.check(is_correct_room)
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ **[Bot 3]** Đã dừng nhạc và nghỉ ngơi.")

@bot.command()
@commands.check(is_correct_room)
async def repeat(ctx):
    global is_repeat
    is_repeat = not is_repeat
    await ctx.send(f"🔁 **[Bot 3]** Chế độ lặp lại: **{'BẬT' if is_repeat else 'TẮT'}**")

# Xử lý lỗi để bot im lặng khi nhắn sai channel
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return

bot.run("TOKEN_NHAC_3")