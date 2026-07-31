import os
import random
import string
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("No token found! Set TELEGRAM_BOT_TOKEN environment variable.")
    exit(1)

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

def get_strength(password):
    score = 0
    if len(password) >= 12: score += 1
    if len(password) >= 16: score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in "!@#$%^&*()" for c in password): score += 1
    
    if score >= 6: return "🟢 Very Strong"
    elif score >= 5: return "🟢 Strong"
    elif score >= 4: return "🟡 Moderate"
    else: return "🟠 Weak"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 *Password Generator Bot*\n\n"
        "Send /generate for a 16-character password\n"
        "Send /generate 24 for custom length\n"
        "Send /custom for preset options",
        parse_mode='Markdown'
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    length = 16
    
    if args:
        try:
            length = int(args[0])
            if length < 4: length = 4
            if length > 128: length = 128
        except:
            pass
    
    password = generate_password(length)
    strength = get_strength(password)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Copy", callback_data=f"copy_{password}")],
        [InlineKeyboardButton("🔄 New", callback_data="new")],
        [InlineKeyboardButton("⚙️ Custom", callback_data="custom")]
    ])
    
    await update.message.reply_text(
        f"🔑 *Password*\n\n`{password}`\n\nStrength: {strength}\nLength: {len(password)}",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("8 chars", callback_data="p8"), InlineKeyboardButton("12 chars", callback_data="p12")],
        [InlineKeyboardButton("16 chars", callback_data="p16"), InlineKeyboardButton("24 chars", callback_data="p24")],
        [InlineKeyboardButton("32 chars", callback_data="p32"), InlineKeyboardButton("64 chars", callback_data="p64")],
        [InlineKeyboardButton("🎲 Random", callback_data="prand")]
    ])
    await update.message.reply_text("Choose length:", reply_markup=keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("copy_"):
        password = data.replace("copy_", "")
        await query.message.reply_text(f"✅ Copied!\n\n`{password}`", parse_mode='Markdown')
        return
    
    if data == "new":
        password = generate_password(16)
        strength = get_strength(password)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Copy", callback_data=f"copy_{password}")],
            [InlineKeyboardButton("🔄 New", callback_data="new")],
            [InlineKeyboardButton("⚙️ Custom", callback_data="custom")]
        ])
        await query.edit_message_text(
            f"🔑 *Password*\n\n`{password}`\n\nStrength: {strength}\nLength: {len(password)}",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return
    
    if data == "custom":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("8 chars", callback_data="p8"), InlineKeyboardButton("12 chars", callback_data="p12")],
            [InlineKeyboardButton("16 chars", callback_data="p16"), InlineKeyboardButton("24 chars", callback_data="p24")],
            [InlineKeyboardButton("32 chars", callback_data="p32"), InlineKeyboardButton("64 chars", callback_data="p64")],
            [InlineKeyboardButton("🎲 Random", callback_data="prand")]
        ])
        await query.edit_message_text("Choose length:", reply_markup=keyboard)
        return
    
    if data.startswith("p"):
        preset = data.replace("p", "")
        if preset == "rand":
            length = random.randint(8, 32)
        else:
            length = int(preset)
        
        password = generate_password(length)
        strength = get_strength(password)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Copy", callback_data=f"copy_{password}")],
            [InlineKeyboardButton("🔄 New", callback_data="new")],
            [InlineKeyboardButton("⚙️ Custom", callback_data="custom")]
        ])
        await query.edit_message_text(
            f"🔑 *Password*\n\n`{password}`\n\nStrength: {strength}\nLength: {len(password)}",
            parse_mode='Markdown',
            reply_markup=keyboard
        )

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        length = int(update.message.text)
        if 4 <= length <= 128:
            password = generate_password(length)
            strength = get_strength(password)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Copy", callback_data=f"copy_{password}")],
                [InlineKeyboardButton("🔄 New", callback_data="new")],
                [InlineKeyboardButton("⚙️ Custom", callback_data="custom")]
            ])
            await update.message.reply_text(
                f"🔑 *Password*\n\n`{password}`\n\nStrength: {strength}\nLength: {len(password)}",
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text("Send a number between 4-128")
    except:
        await update.message.reply_text("Send a number for custom length")

def main():
    logger.info("Starting bot...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("custom", custom))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    
    logger.info("Bot is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
