import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from motor.motor_asyncio import AsyncIOMotorClient

# 1. SERVER 24/7 (Cho Render)
app = Flask('')
@app.route('/')
def home(): return "Bot Dam is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. CONFIG & INTENTS
load_dotenv()
TOKEN = os.getenv("TOKEN_BOT_DAM")
MONGO_URI = os.getenv("MONGO_URI")

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True

bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)

# 3. KẾT NỐI DATABASE
cluster = AsyncIOMotorClient(MONGO_URI)
db = cluster["HoangCungDB"]
collection = db["tuong_tac"]

@bot.event
async def on_ready():
    print(f"--- ✅ {bot.user.name} ĐÃ LÊN SÀN ---")

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # Cộng điểm tương tác
    uid = str(message.author.id)
    await collection.update_one(
        {"_id": uid},
        {"$inc": {"count": 1}, "$set": {"name": message.author.display_name}},
        upsert=True
    )
    await bot.process_commands(message)

# 4. HỆ THỐNG SINH SÁT (ADMIN)
def is_admin():
    return commands.has_permissions(administrator=True)

@bot.command()
@is_admin()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"🚫 Đã sút {member.mention} khỏi server! Lý do: {reason}")

@bot.command()
@is_admin()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Đã tiễn {member.mention} về trời! Lý do: {reason}")

@bot.command()
@is_admin()
async def reset_data(ctx):
    await collection.delete_many({})
    await ctx.send("🧹 Đã dọn sạch bảng xếp hạng tương tác!")

# 5. CHỨC NĂNG BÁO CÁO (REPORT)
@bot.command()
async def report(ctx, *, ndung):
    # Thay 'ID_CUA_SEP' bằng ID Discord thật của sếp để nhận tin nhắn
    admin_id = 1159865838925529118  # Lấy ID từ file json của sếp
    admin = await bot.fetch_user(admin_id)
    if admin:
        embed = discord.Embed(title="🚨 BÁO CÁO MỚI", color=0xff0000)
        embed.add_field(name="Người gửi", value=ctx.author.mention)
        embed.add_field(name="Nội dung", value=ndung)
        await admin.send(embed=embed)
        await ctx.send("✅ Đã gửi báo cáo đến sếp tổng!")

# 6. BỘ LỆNH CHỌC GHẸO
@bot.command()
async def dam(ctx, member: discord.Member):
    embed = discord.Embed(title=f"👊 {ctx.author.display_name} đấm vỡ alo {member.display_name}!", color=0xff0000)
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueGZ3bmZ3bmZ3bmZ3bmZ3bmZ3JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/alsdBBDv2vWVS/giphy.gif")
    await ctx.send(embed=embed)

@bot.command()
async def tat(ctx, member: discord.Member): await ctx.send(f"✋ {ctx.author.mention} tát {member.mention} sưng mặt!")
@bot.command()
async def sut(ctx, member: discord.Member): await ctx.send(f"👞 {ctx.author.mention} sút {member.mention} bay màu!")

# 7. TOP TƯƠNG TÁC
@bot.command()
async def top(ctx):
    cursor = collection.find().sort("count", -1).limit(10)
    data = await cursor.to_list(length=10)
    if not data: return await ctx.send("📊 Chưa có ai tương tác sếp ơi!")
    
    desc = ""
    for i, doc in enumerate(data):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
        desc += f"{medal} **{doc['name']}**: `{doc['count']}` tin nhắn\n"
    
    embed = discord.Embed(title="🏆 CHIẾN THẦN TƯƠNG TÁC", description=desc, color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def list(ctx):
    embed = discord.Embed(title="📜 DANH SÁCH LỆNH", color=0xffd700)
    embed.add_field(name="👊 Ghẹo", value="`?dam`, `?tat`, `?sut`", inline=False)
    embed.add_field(name="📊 Thống kê", value="`?top`", inline=False)
    embed.add_field(name="🚨 Góp ý", value="`?report [nội dung]`", inline=False)
    embed.add_field(name="🛠️ Admin", value="`?kick`, `?ban`, `?reset_data`", inline=False)
    await ctx.send(embed=embed)

if TOKEN:
    keep_alive()
    bot.run(TOKEN.strip())
