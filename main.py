import discord
from discord.ext import commands
from openai import OpenAI
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
import random
import os
from dotenv import load_dotenv

# Đọc file .env
load_dotenv()

TOKEN = os.getenv("TOKEN_BOT_DAM")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Khởi tạo OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# KHỞI TẠO BIẾN LOCK (Quan trọng để không lỗi AttributeError)
bot._ai_lock = False

# -----------------------------
# ====== Kiểm tra quyền =======
# -----------------------------
def is_admin_or_qtv(ctx):
    qtv_role = discord.utils.get(ctx.guild.roles, name="QTV")
    return ctx.author.guild_permissions.administrator or (qtv_role in ctx.author.roles)

# -----------------------------
# ============ AI =============
# -----------------------------
@bot.command()
async def ai(ctx, *, prompt: str):
    if bot._ai_lock:
        await ctx.send("🤖 Bot đang xử lý yêu cầu trước, vui lòng chờ...")
        return
    
    bot._ai_lock = True
    try:
        # Nếu hỏi giờ (Dùng ZoneInfo để chuẩn giờ VN)
        if any(word in prompt.lower() for word in ["giờ", "mấy giờ", "time"]):
            vn_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%H:%M:%S | %d/%m/%Y")
            await ctx.send(f"🕒 Giờ hiện tại ở Hà Nội: **{vn_time}**")
            bot._ai_lock = False
            return

        msg = await ctx.send("🤖 AI đang suy nghĩ...")
        
        # Chạy trong thread để không làm treo bot
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
        )
        answer = response.choices[0].message.content
        await msg.edit(content=f"💬 {answer}")

    except Exception as e:
        await ctx.send(f"❌ Lỗi AI: {e}")
    finally:
        bot._ai_lock = False

# -----------------------------
# ==== Quản trị (Admin/QTV) ====
# -----------------------------
@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    if is_admin_or_qtv(ctx):
        await member.kick(reason=reason)
        await ctx.send(f"🚫 Đã sút bay màu {member.mention}!")
    else:
        await ctx.send("❌ Sếp không có quyền dùng lệnh này!")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    if is_admin_or_qtv(ctx):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 Đã ban vĩnh viễn {member.mention}!")
    else:
        await ctx.send("❌ Quyền lực chưa đủ để ban sếp ơi!")

@bot.command()
async def pingrole(ctx, *, role_name: str = "QTV"):
    if not is_admin_or_qtv(ctx):
        return await ctx.send("❌ Lệnh này dành cho QTV!")
    
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role and role.members:
        messages = [
            f"📢 {role.mention} vào việc nè!",
            f"🔥 Hội {role.mention} tập hợp!",
            f"🚨 Báo động {role.mention}!"
        ]
        # Dùng random ở đây để VS Code hết báo mờ nè sếp
        await ctx.send(random.choice(messages))
    else:
        await ctx.send(f"⚠️ Không tìm thấy role {role_name} hoặc role không có ai.")

# -----------------------------
# ========== Tương tác =========
# -----------------------------
@bot.command()
async def tat(ctx, member: discord.Member):
    slap_gifs = [
        "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif",
        "https://media.giphy.com/media/RXGNsyRb1hDJm/giphy.gif"
    ]
    embed = discord.Embed(title=f"{ctx.author.display_name} vả lật mặt {member.display_name}!", color=discord.Color.red())
    embed.set_image(url=random.choice(slap_gifs))
    await ctx.send(embed=embed)

@bot.command()
async def om(ctx, member: discord.Member):
    hug_gifs = ["https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif"]
    embed = discord.Embed(title=f"{ctx.author.display_name} ôm {member.display_name} cực chặt!", color=discord.Color.purple())
    embed.set_image(url=random.choice(hug_gifs))
    await ctx.send(embed=embed)

@bot.command()
async def helpme(ctx):
    commands_list = """
**Hệ thống Siêu Bot AI:**
`!ai <câu hỏi>` - Hỏi đáp thông minh
`!kick/!ban <@user>` - Kỷ luật (QTV/Admin)
`!pingrole QTV` - Triệu hồi QTV
`!mostactive` - Xem ai nhắn nhiều nhất
`!om/!tat/!sut <@user>` - Chọc ghẹo có GIF
`!helpme` - Xem lại bảng này
"""
    await ctx.send(commands_list)

# -----------------------------
# ==== Chạy bot =====
# -----------------------------
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Lỗi: Chưa tìm thấy TOKEN trong file .env!")