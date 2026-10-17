import os
import discord
from discord.ext import commands
from google import genai
from google.genai import types

# Code sẽ tự động lấy token từ bảo mật của Render, không sợ bị lộ lên GitHub
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
ALLOWED_CHANNEL_ID = 1560253665913208938

SYSTEM_INSTRUCTION = """
Bạn là một trợ lý AI thông minh, thân thiện, chuyên hỗ trợ giải bài tập về nhà.
Hãy giải thích từng bước rõ ràng, dễ hiểu và khích lệ người học tư duy.
"""

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user.name} đã sẵn sàng hoạt động!')

@bot.command(name="hoidap")
async def hoidap(ctx, *, question: str = ""):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.message.delete()
        warning = await ctx.send(f"⚠️ Bot này chỉ được phép hoạt động trong kênh <#{ALLOWED_CHANNEL_ID}> thôi nhé!")
        await warning.delete(delay=5)
        return

    async with ctx.typing():
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3,
                ),
            )
            
            answer = response.text
            if len(answer) > 2000:
                for chunk in [answer[i:i+1990] for i in range(0, len(answer), 1990)]:
                    await ctx.send(chunk)
            else:
                await ctx.send(answer)
                
        except Exception as e:
            await ctx.send(f"❌ Đã xảy ra lỗi: {e}")

bot.run(DISCORD_TOKEN)