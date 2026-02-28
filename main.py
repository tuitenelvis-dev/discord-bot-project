import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import json
import time

# =========================
# LOAD TOKEN
# =========================
load_dotenv()
TOKEN = os.getenv("TOKEN_BOT_DAM")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)

DATA_FILE = "data.json"

# =========================
# LOAD / SAVE JSON
# =========================
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    # Tự tạo key nếu thiếu
    if "money" not in data:
        data["money"] = {}
    if "exp" not in data:
        data["exp"] = {}
    if "level" not in data:
        data["level"] = {}
    if "notis" not in data:
        data["notis"] = []
    if "jail" not in data:
        data["jail"] = []
    if "interact" not in data:
        data["interact"] = {}

    return data


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


data = load_data()

# =========================
# CONSTANTS
# =========================
CHANNEL_DILAM = 1475671866596135115
CHANNEL_TAIXIU = 1475008504468340888
CHANNEL_NOTI = 1413966849053294637
CHANNEL_GOPY = 1413966849053294637
CHANNEL_REPORT = 1413966849053294637

ROLE_ADMIN = 1159865838925529118
ROLE_QTV = 1474264924657025106

# =========================
# PERMISSION HELPERS
# =========================
def is_admin(member):
    return any(role.id == ROLE_ADMIN for role in member.roles)


def is_qtv(member):
    return any(role.id == ROLE_QTV for role in member.roles)


def has_permission(member):
    return is_admin(member) or is_qtv(member)


# =========================
# MONEY SYSTEM
# =========================
def get_money(uid):
    return data["money"].get(str(uid), 0)


def add_money(uid, amount):
    data["money"][str(uid)] = get_money(uid) + amount
    save_data()


def sub_money(uid, amount):
    if get_money(uid) < amount:
        return False
    data["money"][str(uid)] = get_money(uid) - amount
    save_data()
    return True


@bot.command()
async def topbank(ctx):
    money_data = data.get("money", {})

    if not money_data:
        embed = discord.Embed(
            title="🏦 TOP NGÂN HÀNG",
            description="Chưa có dữ liệu người chơi nào.",
            color=0xe74c3c
        )
        return await ctx.send(embed=embed)

    sorted_users = sorted(
        money_data.items(),
        key=lambda x: x[1],
        reverse=True
    )

    embed = discord.Embed(
        title="🏦 TOP ĐẠI GIA SERVER",
        color=0xf1c40f
    )

    for rank, (uid, money) in enumerate(sorted_users[:10], start=1):
        embed.add_field(
            name=f"#{rank} • UID: {uid}",
            value=f"<@{uid}> — **{money:,} VND**",
            inline=False
        )

    await ctx.send(embed=embed)


# =========================
# EXP – LEVEL SYSTEM
# =========================
def get_exp(uid):
    return data["exp"].get(str(uid), 0)


def add_exp(uid, amount):
    uid = str(uid)
    data["exp"][uid] = get_exp(uid) + amount
    save_data()


def get_level(uid):
    return data["level"].get(str(uid), 1)


def add_level(uid):
    uid = str(uid)
    data["level"][uid] = get_level(uid) + 1
    save_data()


def check_level_up(uid):
    exp = get_exp(uid)
    level = get_level(uid)
    needed = level * 100
    if exp >= needed:
        add_level(uid)
        return True
    return False


# =========================
# BOT READY
# =========================
@bot.event
async def on_ready():
    print(f"Bot đã đăng nhập: {bot.user}")


# =========================
# GHI TƯƠNG TÁC
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = str(message.author.id)
    data["interact"][uid] = data["interact"].get(uid, 0) + 1
    save_data()

    await bot.process_commands(message)


# =========================
# STK
# =========================
@bot.command()
async def stk(ctx):
    money = get_money(ctx.author.id)
    embed = discord.Embed(
        title="💰 SỐ DƯ TÀI KHOẢN",
        color=0xf1c40f
    )
    embed.add_field(name="👤 UID", value=str(ctx.author.id), inline=False)
    embed.add_field(name="💳 Số dư", value=f"{money:,} VND", inline=False)
    await ctx.send(embed=embed)


# =========================
# PAY
# =========================
@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        return await ctx.send(embed=discord.Embed(
            title="❌ Lỗi",
            description="Số tiền phải lớn hơn 0.",
            color=0xe74c3c
        ))

    if not sub_money(ctx.author.id, amount):
        return await ctx.send(embed=discord.Embed(
            title="❌ Không đủ tiền",
            description="Bạn không đủ tiền để chuyển.",
            color=0xe74c3c
        ))

    add_money(member.id, amount)

    embed = discord.Embed(
        title="💸 CHUYỂN TIỀN THÀNH CÔNG",
        color=0x2ecc71
    )
    embed.add_field(name="👤 UID người gửi", value=str(ctx.author.id), inline=False)
    embed.add_field(name="👤 UID người nhận", value=str(member.id), inline=False)
    embed.add_field(name="💰 Số tiền", value=f"{amount:,} VND", inline=False)

    await ctx.send(embed=embed)


# =========================
# PROFILE
# =========================
@bot.command()
async def profile(ctx):
    uid = ctx.author.id
    money = get_money(uid)
    exp = get_exp(uid)
    level = get_level(uid)
    next_level = level * 100

    embed = discord.Embed(
        title=f"📘 Hồ sơ của {ctx.author.name}",
        color=0x00aaff
    )
    embed.add_field(name="👤 UID", value=str(uid), inline=False)
    embed.add_field(name="💰 Tiền", value=f"{money:,} VND", inline=False)
    embed.add_field(name="⭐ Level", value=level, inline=False)
    embed.add_field(name="📈 EXP", value=f"{exp}/{next_level}", inline=False)

    await ctx.send(embed=embed)


# =========================
# ĐI LÀM
# =========================
WORK_CHANNEL = CHANNEL_DILAM
work_cooldown = {}


@bot.command()
async def dilam(ctx):
    uid = ctx.author.id

    if ctx.channel.id != WORK_CHANNEL:
        return await ctx.send(embed=discord.Embed(
            title="❌ Sai khu vực",
            description="Bạn chỉ có thể đi làm trong **khu vực đi làm**.",
            color=0xe74c3c
        ))

    now = time.time()
    if uid in work_cooldown and now - work_cooldown[uid] < 300:
        remaining = int(300 - (now - work_cooldown[uid]))
        minutes = remaining // 60
        seconds = remaining % 60

        return await ctx.send(embed=discord.Embed(
            title="⏳ Chưa thể đi làm",
            description=f"Bạn cần chờ **{minutes} phút {seconds} giây** nữa mới có thể đi làm tiếp.",
            color=0xe67e22
        ))

    work_cooldown[uid] = now

    level = get_level(uid)
    base_salary = random.randint(100_000, 150_000)
    bonus = level * random.randint(5_000, 15_000)
    salary = base_salary + bonus

    add_money(uid, salary)

    exp_gain = random.randint(10, 20)
    add_exp(uid, exp_gain)

    embed = discord.Embed(
        title="🧳 BẠN ĐÃ ĐI LÀM!",
        color=0xf1c40f
    )
    embed.add_field(name="👤 UID", value=str(uid), inline=False)
    embed.add_field(name="💵 Lương cơ bản", value=f"{base_salary:,} VND")
    embed.add_field(name="🎖 Thưởng theo level", value=f"{bonus:,} VND")
    embed.add_field(name="💰 Tổng nhận", value=f"{salary:,} VND", inline=False)
    embed.add_field(name="📈 Nhận EXP", value=f"{exp_gain}", inline=False)

    if check_level_up(uid):
        embed.add_field(
            name="🎉 Lên Level!",
            value=f"Level mới: **{get_level(uid)}**",
            inline=False
        )

    await ctx.send(embed=embed)


# =========================
# TÀI XỈU
# =========================
import discord
from discord.ext import commands
import random
import json
import os

bot = commands.Bot(command_prefix="?", intents=discord.Intents.all())

TAIXIU_CHANNEL_ID = 1475008504468340888
DATA_FILE = "money.json"

def load_money():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_money(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def is_taixiu_channel(ctx):
    return ctx.channel.id == TAIXIU_CHANNEL_ID

@commands.cooldown(1, 5, commands.BucketType.user)
@commands.check(is_taixiu_channel)
@bot.command()
async def taixiu(ctx, bet: int, choice: str):
    ...
    (phần code của bạn giữ nguyên)
    ...

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Bạn phải vào **kênh Tài Xỉu** mới được chơi!")
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Chậm lại nào! Thử lại sau **{error.retry_after:.1f}s**.")
        return

    raise error

# =========================
# ADMIN / QTV COMMANDS
# =========================
@bot.command()
async def kick(ctx, member: discord.Member, *, reason="Không có lý do"):
    if not has_permission(ctx.author):
        return await ctx.send(embed=discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền dùng lệnh này.",
            color=0xe74c3c
        ))
    await member.kick(reason=reason)
    embed = discord.Embed(
        title="👢 Kick thành công",
        description=f"{member.mention} đã bị kick.",
        color=0xf1c40f
    )
    embed.add_field(name="👤 UID người bị kick", value=str(member.id), inline=False)
    embed.add_field(name="👤 UID người thực hiện", value=str(ctx.author.id), inline=False)
    embed.add_field(name="📌 Lý do", value=reason, inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def ban(ctx, member: discord.Member, *, reason="Không có lý do"):
    if not has_permission(ctx.author):
        return await ctx.send(embed=discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền dùng lệnh này.",
            color=0xe74c3c
        ))
    await member.ban(reason=reason)
    embed = discord.Embed(
        title="🔨 Ban thành công",
        description=f"{member.mention} đã bị ban.",
        color=0xf1c40f
    )
    embed.add_field(name="👤 UID người bị ban", value=str(member.id), inline=False)
    embed.add_field(name="👤 UID người thực hiện", value=str(ctx.author.id), inline=False)
    embed.add_field(name="📌 Lý do", value=reason, inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def setmoney(ctx, member: discord.Member, amount: int):
    if not has_permission(ctx.author):
        return await ctx.send(embed=discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền dùng lệnh này.",
            color=0xe74c3c
        ))
    data["money"][str(member.id)] = amount
    save_data()
    embed = discord.Embed(
        title="💰 Set tiền thành công",
        color=0xf1c40f
    )
    embed.add_field(name="👤 UID", value=str(member.id), inline=False)
    embed.add_field(name="💰 Số dư mới", value=f"{amount:,} VND", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def setup_report(ctx):
    if not has_permission(ctx.author):
        return await ctx.send(embed=discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền dùng lệnh này.",
            color=0xe74c3c
        ))
    await ctx.send(embed=discord.Embed(
        title="📨 Hệ thống report",
        description="Hệ thống report đã sẵn sàng.",
        color=0xf1c40f
    ))
@bot.command()
async def pingall(ctx, *, content: str):
    # Kiểm tra quyền
    if not has_permission(ctx.author):
        return await ctx.send(embed=discord.Embed(
            title="❌ Không có quyền",
            description="Chỉ Admin hoặc QTV mới được dùng lệnh này.",
            color=0xe74c3c
        ))

    # Gửi ping all
    await ctx.send(f"@everyone {content}")


# =========================
# TOP TƯƠNG TÁC
# =========================
@bot.command()
async def top(ctx):
    interact_data = data.get("interact", {})

    if not interact_data:
        embed = discord.Embed(
            title="💬 TOP TƯƠNG TÁC",
            description="Chưa có dữ liệu tương tác.",
            color=0xe74c3c
        )
        return await ctx.send(embed=embed)

    sorted_users = sorted(
        interact_data.items(),
        key=lambda x: x[1],
        reverse=True
    )

    embed = discord.Embed(
        title="💬 TOP TƯƠNG TÁC SERVER",
        description="Ai là người nói nhiều nhất server đây?",
        color=0x3498db
    )

    medals = ["🥇", "🥈", "🥉"]

    for rank, (uid, count) in enumerate(sorted_users[:10], start=1):
        medal = medals[rank - 1] if rank <= 3 else f"#{rank}"

        embed.add_field(
            name=f"{medal} • UID: {uid}",
            value=f"<@{uid}> — **{count} tin nhắn**",
            inline=False
        )

    embed.set_footer(text="Bot Hoàng Cung • PNV Server")

    await ctx.send(embed=embed)


@bot.command()
async def reset_top(ctx):
    if not has_permission(ctx.author):
        return await ctx.send(embed=discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền dùng lệnh này.",
            color=0xe74c3c
        ))
    data["notis"] = []
    save_data()
    await ctx.send(embed=discord.Embed(
        title="♻️ Reset thành công",
        description="Đã reset bảng thông báo.",
        color=0xf1c40f
    ))


@bot.command()
async def noti(ctx, *, content: str):
    if not has_permission(ctx.author):
        return await ctx.send(embed=discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền dùng lệnh này.",
            color=0xe74c3c
        ))

    msg = f"📢 Thông báo: {content}"
    data["notis"].append(msg)
    save_data()

    channel = bot.get_channel(CHANNEL_NOTI)
    if channel:
        embed = discord.Embed(
            title="📢 THÔNG BÁO",
            description=content,
            color=0xf1c40f
        )
        embed.add_field(name="👤 UID người gửi", value=str(ctx.author.id), inline=False)
        await channel.send(embed=embed)

    await ctx.send(embed=discord.Embed(
        title="✅ Đã gửi thông báo",
        description="Thông báo đã được gửi vào kênh thông báo.",
        color=0x2ecc71
    ))


# =========================
# JAIL SYSTEM
# =========================
def is_in_jail(uid):
    return str(uid) in data["jail"]


def jail_user(uid):
    if str(uid) not in data["jail"]:
        data["jail"].append(str(uid))
        save_data()


def unjail_user(uid):
    if str(uid) in data["jail"]:
        data["jail"].remove(str(uid))
        save_data()


@bot.command()
async def jail(ctx, member: discord.Member):
    if not has_permission(ctx.author):
        return await ctx.send(embed=discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền dùng lệnh này.",
            color=0xe74c3c
        ))

    if is_in_jail(member.id):
        return await ctx.send(embed=discord.Embed(
            title="⚠ Người này đã bị giam",
            description=f"{member.mention} (UID: {member.id}) đang ở trong tù rồi.",
            color=0xf1c40f
        ))

    jail_user(member.id)

    embed = discord.Embed(
        title="🚔 ĐÃ TỐNG VÀO NGỤC",
        color=0xe74c3c
    )
    embed.add_field(name="👤 Người bị giam", value=f"{member.mention}\nUID: {member.id}", inline=False)
    embed.add_field(name="🔧 Người thực hiện", value=f"{ctx.author.mention}\nUID: {ctx.author.id}", inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def unjail(ctx, member: discord.Member):
    if not has_permission(ctx.author):
        return await ctx.send(embed=discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền dùng lệnh này.",
            color=0xe74c3c
        ))

    if not is_in_jail(member.id):
        return await ctx.send(embed=discord.Embed(
            title="⚠ Người này không bị giam",
            description=f"{member.mention} (UID: {member.id}) không ở trong tù.",
            color=0xf1c40f
        ))

    unjail_user(member.id)

    embed = discord.Embed(
        title="🔓 ĐÃ THẢ TÙ",
        color=0x2ecc71
    )
    embed.add_field(name="👤 Người được thả", value=f"{member.mention}\nUID: {member.id}", inline=False)
    embed.add_field(name="🔧 Người thực hiện", value=f"{ctx.author.mention}\nUID: {ctx.author.id}", inline=False)

    await ctx.send(embed=embed)


# =========================
# LIST COMMAND
# =========================
@bot.command()
async def list(ctx):
    embed = discord.Embed(
        title="📜 DANH SÁCH LỆNH BOT HOÀNG CUNG",
        description="Tất cả lệnh đều hỗ trợ embed + UID.",
        color=0xf1c40f
    )

    embed.add_field(
        name="👑 QUẢN TRỊ",
        value="`?kick`, `?ban`, `?setmoney`, `?setup_report`, `?noti`, `?reset_top`, `?pingall`",
        inline=False
    )


    embed.add_field(
        name="💰 KINH TẾ",
        value="`?stk`, `?pay`, `?dilam`, `?taixiu`, `?profile`, `?topbank`",
        inline=False
    )

    embed.add_field(
        name="🛠 HỖ TRỢ NGƯỜI DÙNG",
        value="`?report <nội dung>` — Báo cáo người dùng\n"
              "`?gopy <nội dung>` — Góp ý cho bot",
        inline=False
    )

    embed.add_field(
        name="🕒 Giờ làm việc của bot",
        value=(
            "Thứ 2–Thứ 6: **4:00 sáng → 10:00 trưa**\n"
            "Thứ 7 & Chủ nhật: **8:00 tối → 12:00 trưa**\n"
            "_(Chỉ là giờ hoạt động dự kiến, lệnh vẫn dùng được mọi lúc nếu bot online)_"
        ),
        inline=False
    )

    embed.add_field(
        name="🎵 ROOM NHẠC",
        value="Lệnh bot nhạc: `!list (số phòng)`",
        inline=False
    )

    embed.add_field(
        name="🔒 QUẢN LÝ TÙ NHÂN",
        value="`?jail @user` — Tống vào ngục\n`?unjail @user` — Thả khỏi ngục",
        inline=False
    )

    embed.set_footer(text="Bot Hoàng Cung • PNV Server")

    await ctx.send(embed=embed)


# =========================
# GÓP Ý
# =========================
@bot.command()
async def gopy(ctx, *, content: str):
    channel = bot.get_channel(CHANNEL_GOPY)
    if channel is None:
        return await ctx.send(embed=discord.Embed(
            title="❌ Lỗi hệ thống",
            description="Không tìm thấy kênh góp ý. Hãy kiểm tra lại ID.",
            color=0xe74c3c
        ))

    embed = discord.Embed(
        title="💡 GÓP Ý NGƯỜI DÙNG",
        color=0x3498db
    )
    embed.add_field(name="👤 Người góp ý", value=ctx.author.mention, inline=False)
    embed.add_field(name="🆔 UID", value=str(ctx.author.id), inline=False)
    embed.add_field(name="📝 Nội dung", value=content, inline=False)

    await channel.send(embed=embed)

    await ctx.send(embed=discord.Embed(
        title="✨ Đã gửi góp ý",
        description="Cảm ơn bạn đã đóng góp ý kiến!",
        color=0x2ecc71
    ))


# =========================
# REPORT
# =========================
@bot.command()
async def report(ctx, *, content: str):
    channel = bot.get_channel(CHANNEL_REPORT)
    if channel is None:
        return await ctx.send(embed=discord.Embed(
            title="❌ Lỗi hệ thống",
            description="Không tìm thấy kênh report. Hãy kiểm tra lại ID.",
            color=0xe74c3c
        ))

    embed = discord.Embed(
        title="🚨 BÁO CÁO NGƯỜI DÙNG",
        color=0xe74c3c
    )
    embed.add_field(name="👤 Người báo cáo", value=ctx.author.mention, inline=False)
    embed.add_field(name="🆔 UID", value=str(ctx.author.id), inline=False)
    embed.add_field(name="📄 Nội dung", value=content, inline=False)

    await channel.send(embed=embed)

    await ctx.send(embed=discord.Embed(
        title="✅ Đã gửi báo cáo",
        description="Cảm ơn bạn đã báo cáo. QTV sẽ xem xét sớm nhất.",
        color=0x2ecc71
    ))


# =========================
# RUN BOT
# =========================
bot.run(TOKEN)
