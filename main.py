import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")

# 1. Mulai Bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kirim file HTML untuk diupload ke Vercel.")

# 2. Proses File HTML
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name

    if not file_name.endswith('.html'):
        return await update.message.reply_text("Kirim file HTML saja.")

    file_path = f"/tmp/{file_name}"
    await file.download_to_drive(file_path)

    # 3. Deploy ke Vercel
    url = deploy_to_vercel(file_path, file_name)
    if url:
        await update.message.reply_text(f"✅ Berhasil diupload ke Vercel:\n{url}")
    else:
        await update.message.reply_text("❌ Gagal upload ke Vercel.")

# 4. Fungsi Upload HTML ke Vercel
def deploy_to_vercel(file_path, file_name):
    with open(file_path, 'r') as f:
        content = f.read()

    files = {
        'index.html': {
            'file': file_name,
            'data': content,
            'encoding': 'utf-8',
        }
    }

    payload = {
        "name": "telegram-html-bot",
        "files": [
            {
                "file": "index.html",
                "data": content
            }
        ],
        "projectSettings": {
            "framework": "other"
        }
    }

    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }

    res = requests.post("https://api.vercel.com/v13/deployments", json=payload, headers=headers)

    if res.status_code == 200:
        return res.json().get("url", "")
    else:
        print("Error:", res.text)
        return None

# 5. Jalankan Bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
app.run_polling()

