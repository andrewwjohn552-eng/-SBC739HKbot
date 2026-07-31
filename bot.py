import os
import random
import string
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sys

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
    sys.exit(1)

# Password generation function
def generate_password(length=16):
    """Generate a strong password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def get_strength(password):
    """Evaluate password strength"""
    score = 0
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    
    if score >= 6:
        return "🟢 Very Strong"
    elif score >= 5:
        return "🟢 Strong"
    elif score >= 4:
        return "🟡 Moderate"
    else:
        return "🟠 Weak"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🔐 *Welcome to Secure Password Generator!*\n\n"
        "I can generate strong passwords for you instantly.\n\n"
        "📌 *Commands:*\n"
        "/generate - Generate a 16-character password\n"
        "/generate 24 - Generate a 24-character password\n"
        "/custom - Choose from preset lengths\n"
        "/help - Show help\n\n"
        "🔒 Passwords are generated locally and never stored."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ *How to use:*\n\n"
        "1️⃣ /generate - Quick password (16 chars)\n"
        "2️⃣ /generate 24 - Custom length (4-128)\n"
        "3️⃣ /custom - Choose from presets\n\n"
        "*Features:*\n"
        "✅ Strong passwords\n"
        "✅ Strength indicator\n"
        "✅ Customizable length"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Generate command
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Check if user specified length
        args = context.args
        length = 16  # default
        
        if args:
            try:
                length = int(args[0])
                if length < 4:
                    length = 4
                elif length > 128:
                    length = 128
            except ValueError:
                await update.message.reply_text("⚠️ Please send a valid number (4-128). Using default 16.")
        
        # Generate password
        password = generate_password(length)
        strength = get_strength(password)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Copy", callback_data=f"copy_{password}")],
            [InlineKeyboardButton("🔄 New Password", callback_data="new")],
            [InlineKeyboardButton("⚙️ Custom Length", callback_data="custom")]
        ])
        
        response = (
            f"🔑 *Your Password*\n\n"
            f"`{password}`\n\n"
            f"📊 Strength: {strength}\n"
            f"📏 Length: {len(password)}\n\n"
            f"Click 'Copy' to copy the password!"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)
    
    except Exception as e:
        logger.error(f"Error in generate: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again.")

# Custom command
async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔢 8 chars", callback_data="preset_8"),
         InlineKeyboardButton("🔢 12 chars", callback_data="preset_12")],
        [InlineKeyboardButton("🔢 16 chars", callback_data="preset_16"),
         InlineKeyboardButton("🔢 24 chars", callback_data="preset_24")],
        [InlineKeyboardButton("🔢 32 chars", callback_data="preset_32"),
         InlineKeyboardButton("🔢 64 chars", callback_data="preset_64")],
        [InlineKeyboardButton("🎲 Random", callback_data="preset_random")]
    ])
    
    await update.message.reply_text(
        "⚙️ *Choose password length:*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

# Handle button clicks
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Copy password
    if data.startswith("copy_"):
        password = data.replace("copy_", "")
        await query.message.reply_text(f"✅ Password copied!\n\n`{password}`", parse_mode='Markdown')
        return
    
    # Generate new password
    if data == "new":
        password = generate_password(16)
        strength = get_strength(password)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Copy", callback_data=f"copy_{password}")],
            [InlineKeyboardButton("🔄 New Password", callback_data="new")],
            [InlineKeyboardButton("⚙️ Custom Length", callback_data="custom")]
        ])
        
        response = (
            f"🔑 *Your Password*\n\n"
            f"`{password}`\n\n"
            f"📊 Strength: {strength}\n"
            f"📏 Length: {len(password)}"
        )
        
        await query.edit_message_text(response, parse_mode='Markdown', reply_markup=keyboard)
        return
    
    # Custom options
    if data == "custom":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔢 8 chars", callback_data="preset_8"),
             InlineKeyboardButton("🔢 12 chars", callback_data="preset_12")],
            [InlineKeyboardButton("🔢 16 chars", callback_data="preset_16"),
             InlineKeyboardButton("🔢 24 chars", callback_data="preset_24")],
            [InlineKeyboardButton("🔢 32 chars", callback_data="preset_32"),
             InlineKeyboardButton("🔢 64 chars", callback_data="preset_64")],
            [InlineKeyboardButton("🎲 Random", callback_data="preset_random")]
        ])
        
        await query.edit_message_text(
            "⚙️ *Choose password length:*",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return
    
    # Preset lengths
    if data.startswith("preset_"):
        preset = data.replace("preset_", "")
        
        if preset == "random":
            length = random.randint(8, 32)
        else:
            length = int(preset)
        
        password = generate_password(length)
        strength = get_strength(password)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Copy", callback_data=f"copy_{password}")],
            [InlineKeyboardButton("🔄 New Password", callback_data="new")],
            [InlineKeyboardButton("⚙️ Custom Length", callback_data="custom")]
        ])
        
        response = (
            f"🔑 *Your Password*\n\n"
            f"`{password}`\n\n"
            f"📊 Strength: {strength}\n"
            f"📏 Length: {len(password)}"
        )
        
        await query.edit_message_text(response, parse_mode='Markdown', reply_markup=keyboard)

# Handle text messages (for custom length)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        length = int(update.message.text.strip())
        if 4 <= length <= 128:
            password = generate_password(length)
            strength = get_strength(password)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Copy", callback_data=f"copy_{password}")],
                [InlineKeyboardButton("🔄 New Password", callback_data="new")],
                [InlineKeyboardButton("⚙️ Custom Length", callback_data="custom")]
            ])
            
            response = (
                f"🔑 *Your Password*\n\n"
                f"`{password}`\n\n"
                f"📊 Strength: {strength}\n"
                f"📏 Length: {len(password)}"
            )
            
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)
        else:
            await update.message.reply_text("⚠️ Please send a number between 4 and 128.")
    except ValueError:
        await update.message.reply_text(
            "🤔 Send a number (4-128) for a custom length, or use /generate"
        )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ An error occurred. Please try again.")

# Main function
def main():
    logger.info("🚀 Bot is starting...")
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generate", generate))
    application.add_handler(CommandHandler("custom", custom))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("✅ Bot is ready!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
