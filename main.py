import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from motor.motor_asyncio import AsyncIOMotorClient

# ==========================================
# 1. KEEP ALIVE (24/7)
# ==========================================
app = Flask('')
@app.route('/')
def home(): return "Bot Dam 24/7 is Live!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
# Sửa đoạn khai báo intents này
intents = discord.Intents.default()
intents.message_content = True  # THIẾU DÒNG NÀY LÀ BOT ĐIẾC
intents.members = True
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
# ==========================================
# 2. CẤU HÌNH DATABASE & BOT
# ==========================================
load_dotenv()
TOKEN = os.getenv("TOKEN_BOT_DAM")
MONGO_URI = os.getenv("MONGO_URI")

cluster = AsyncIOMotorClient(MONGO_URI)
db = cluster["HoangCungDB"]
collection = db["tuong_tac"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"--- ✅ BOT DAM ONLINE 24/7 (DATA CLOUD) ---")

@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id)
    await collection.update_one(
        {"_id": uid},
        {"$inc": {"count": 1}, "$set": {"name": message.author.display_name}},
        upsert=True
    )
    await bot.process_commands(message)

# ==========================================
# 3. HỆ THỐNG SINH SÁT (KICK/BAN/ADMIN)
# ==========================================
def checks_leader():
    async def predicate(ctx):
        is_qtv = discord.utils.get(ctx.author.roles, name="QTV") is not None
        return ctx.author.guild_permissions.administrator or is_qtv
    return commands.check(predicate)

@bot.command()
@checks_leader()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"🚫 Đã đuổi cổ {member.mention}! Lý do: {reason}")

@bot.command()
@checks_leader()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Đã tiễn {member.mention} về trời! Lý do: {reason}")

class AdminView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🧹 Reset Tương Tác", style=discord.ButtonStyle.danger)
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Sếp mới làm được!", ephemeral=True)
        await collection.delete_many({})
        await interaction.response.send_message("🧹 Đã dọn sạch database Cloud!")

@bot.command()
@commands.has_permissions(administrator=True)
async def admin_panel(ctx):
    await ctx.send("👑 **BẢNG ĐIỀU KHIỂN SẾP TỔNG**", view=AdminView())

# ==========================================
# 4. TỐ CÁO & GÓP Ý (MODAL)
# ==========================================
class ReportModal(discord.ui.Modal, title='🚨 Tố Cáo Ẩn Danh'):
    victim = discord.ui.TextInput(label='Kẻ bị tố cáo', placeholder='Nhập tên/tag...')
    reason = discord.ui.TextInput(label='Lý do/Bằng chứng', style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        admin = discord.utils.get(interaction.guild.members, name="vitentoi")
        embed = discord.Embed(title="🚨 TỐ CÁO", color=0xff0000)
        embed.add_field(name="Gửi bởi", value=interaction.user.mention)
        embed.add_field(name="Kẻ bị tố", value=self.victim.value)
        embed.add_field(name="Nội dung", value=self.reason.value, inline=False)
        if admin: await admin.send(embed=embed)
        await interaction.response.send_message("✅ Đã gửi báo cáo kín!", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_report(ctx):
    view = discord.ui.View(timeout=None)
    btn = discord.ui.Button(label="Gửi Tố Cáo", style=discord.ButtonStyle.danger)
    btn.callback = lambda i: i.response.send_modal(ReportModal())
    view.add_item(btn)
    await ctx.send("🛡️ **HÒM THƯ TỐ CÁO**", view=view)

# ==========================================
# 5. BỘ LỆNH CHỌC GHẸO (DAM, TAT, SUT...)
# ==========================================
@bot.command()
async def dam(ctx, member: discord.Member):
    embed = discord.Embed(title=f"👊 {ctx.author.display_name} đấm vỡ alo {member.display_name}!", color=0xff0000)
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueGZ3bmZ3bmZ3bmZ3bmZ3bmZ3JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/alsdBBDv2vWVS/giphy.gif")
    await ctx.send(embed=embed)

@bot.command()
async def tat(ctx, member: discord.Member): await ctx.send(f"✋ {ctx.author.mention} tát {member.mention} vêu mồm!")
@bot.command()
async def sut(ctx, member: discord.Member): await ctx.send(f"👞 {ctx.author.mention} sút {member.mention} bay màu!")
@bot.command()
async def om(ctx, member: discord.Member): await ctx.send(f"❤️ {ctx.author.mention} ôm {member.mention} thắm thiết!")
@bot.command()
async def hon(ctx, member: discord.Member): await ctx.send(f"😘 {ctx.author.mention} hôn {member.mention} nồng cháy!")
@bot.command()
async def ngu(ctx, member: discord.Member): await ctx.send(f"🧠 {member.mention}, bớt cái sự **ngu** lại cho anh em nhờ!")
@bot.command()
async def ngao(ctx, member: discord.Member): await ctx.send(f"🥴 {member.mention} ngáo vừa thôi sếp!")

# ==========================================
# 6. MENU & TOP
# ==========================================
@bot.command()
async def top(ctx):
    cursor = collection.find().sort("count", -1).limit(10)
    data = await cursor.to_list(length=10)
    if not data: return await ctx.send("📊 Data đang trống!")
    desc = ""
    for i, doc in enumerate(data):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
        desc += f"{medal} **{doc['name']}**: `{doc['count']}` tin\n"
    await ctx.send(embed=discord.Embed(title="🏆 CHIẾN THẦN TƯƠNG TÁC", description=desc, color=0x00ff00))

@bot.command()
async def list(ctx):
    embed = discord.Embed(title="🐂 HOANG CUNG BO - BOT DAM", color=0xffd700)
    embed.add_field(name="🎁 QUÀ", value="🏆 **180k VND** cho **Top 1**!", inline=False)
    embed.add_field(name="🎧 NHẠC (Prefix !)", value="`!list1, !list2, !list3`", inline=False)
    embed.add_field(name="🎉 GHẸO (? )", value="`?dam, ?tat, ?sut, ?om, ?hon, ?ngu, ?ngao, ?top, ?check`", inline=False)
    embed.add_field(name="🛡️ ADMIN (? )", value="`?admin_panel, ?kick, ?ban, ?setup_report`", inline=False)
    await ctx.send(embed=embed)

if TOKEN:
    keep_alive()
    bot.run(TOKEN.strip())
