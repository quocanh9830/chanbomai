import os
import discord
from discord.ext import commands
from google import genai
from google.genai import errors

# Khởi tạo Discord Bot với các quyền cơ bản
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Lấy Token và Gemini API Key từ biến môi trường trên Cloud/Render
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Khởi tạo client Gemini mới nhất
client = genai.Client(api_key=GEMINI_API_KEY)

# ID kênh chat được phép hoạt động
ALLOWED_CHANNEL_ID = 1560253665913208938


@bot.event
async def on_ready():
  print(f"✅ Bot {bot.user.name} đã sẵn sàng hoạt động!")


@bot.command(name="hoidap")
async def hoidap(ctx, *, prompt: str = None):
  # Kiểm tra xem bot có đang được gọi đúng kênh chat cho phép hay không
  if ctx.channel.id != ALLOWED_CHANNEL_ID:
    await ctx.send(
        f"⚠️ Bot chỉ được phép hoạt động trong kênh <#{ALLOWED_CHANNEL_ID}> thôi"
        " bạn nhé!"
    )
    return

  if not prompt:
    await ctx.send("Vui lòng nhập nội dung câu hỏi sau lệnh `!hoidap` nhé!")
    return

  # Thông báo đang xử lý
  waiting_msg = await ctx.send("⏳ Đang phân tích và giải bài tập, chờ chút nhé...")

  try:
    # Gọi Gemini API sử dụng model mới nhất gemini-3.8-flash
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    answer = response.text

    # Discord giới hạn mỗi tin nhắn tối đa 2000 ký tự, nếu dài quá sẽ tự động cắt nhỏ
    if len(answer) > 2000:
      for i in range(0, len(answer), 2000):
        await ctx.send(answer[i : i + 2000])
    else:
      await ctx.send(answer)

    # Xóa thông báo chờ
    await waiting_msg.delete()

  except errors.APIError as e:
    await waiting_msg.edit(
        content=f"❌ Đã xảy ra lỗi từ Gemini API: `{e.message}`"
    )
  except Exception as e:
    await waiting_msg.edit(content=f"❌ Đã xảy ra lỗi không mong muốn: `{e}`")


# Chạy bot
if __name__ == "__main__":
  bot.run(DISCORD_TOKEN)
