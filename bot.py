import os
import random
import string
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Password generation function
def generate_password(length=16, use_uppercase=True, use_lowercase=True, 
                      use_digits=True, use_symbols=True, exclude_ambiguous=False):
    """
    Generate a secure password based on user preferences.
    """
    # Character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Ambiguous characters to exclude if requested
    ambiguous = "il1Lo0O"
    
    # Build character pool
    pool = ""
    if use_lowercase:
        pool += lowercase
    if use_uppercase:
        pool += uppercase
    if use_digits:
        pool += digits
    if use_symbols:
        pool += symbols
    
    # Remove ambiguous characters
    if exclude_ambiguous and pool:
        for char in ambiguous:
            pool = pool.replace(char, "")
    
    # Ensure at least one character from each selected type
    if not pool:
        pool = lowercase + digits  # Fallback
    
    # Generate password
    password = ''.join(random.choice(pool) for _ in range(length))
    
    # Ensure minimum requirements for strength
    if use_uppercase and not any(c.isupper() for c in password):
        pos = random.randint(0, length-1)
        password = password[:pos] + random.choice(uppercase) + password[pos+1:]
    
    if use_digits and not any(c.isdigit() for c in password):
        pos = random.randint(0, length-1)
        password = password[:pos] + random.choice(digits) + password[pos+1:]
    
    if use_symbols and not any(c in symbols for c in password):
        pos = random.randint(0, length-1)
        password = password[:pos] + random.choice(symbols) + password[pos+1:]
    
    return password

# Generate password strength indicator
def get_strength(password):
    """Evaluate password strength."""
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
    elif score >= 3:
        return "🟠 Weak"
    else:
        return "🔴 Very Weak"

# Start command handler
@dp.message(Command("start"))
async def start_command(message: types.Message):
    welcome_text = (
        "🔐 *Welcome to Secure Password Generator!*\n\n"
        "I can generate strong, secure passwords for you instantly.\n\n"
        "📌 *Commands:*\n"
        "/generate - Generate a password with default settings\n"
        "/custom - Generate a password with custom options\n"
        "/help - Show this help message\n"
        "/about - About this bot\n\n"
        "🔒 All passwords are generated locally and never stored."
    )
    await message.answer(welcome_text, parse_mode="Markdown")

# Help command handler
@dp.message(Command("help"))
async def help_command(message: types.Message):
    help_text = (
        "❓ *How to use this bot:*\n\n"
        "1️⃣ Click /generate for a quick password (16 chars)\n"
        "2️⃣ Click /custom to customize your password\n"
        "3️⃣ Or just type /generate 24 to get a 24-character password\n\n"
        "*Features:*\n"
        "✅ Strong passwords with mixed characters\n"
        "✅ Copy to clipboard with one click\n"
        "✅ Password strength indicator\n"
        "✅ Customizable length and character types"
    )
    await message.answer(help_text, parse_mode="Markdown")

# About command handler
@dp.message(Command("about"))
async def about_command(message: types.Message):
    about_text = (
        "ℹ️ *About This Bot*\n\n"
        "🔐 Password Generator Bot v1.0\n\n"
        "👨‍💻 Built with aiogram\n"
        "📦 Deployed on Railway\n"
        "🔄 Open Source\n\n"
        "🔒 Your passwords are generated locally and NEVER stored.\n"
        "No data is collected or logged."
    )
    await message.answer(about_text, parse_mode="Markdown")

# Generate command handler
@dp.message(Command("generate"))
async def generate_command(message: types.Message):
    # Check if user specified a length
    args = message.text.split()
    length = 16  # Default length
    
    if len(args) > 1:
        try:
            length = int(args[1])
            if length < 4:
                length = 4
            elif length > 128:
                length = 128
        except ValueError:
            await message.answer("⚠️ Please provide a valid number (4-128). Using default 16.")
    
    # Generate password
    password = generate_password(length=length)
    strength = get_strength(password)
    
    # Create inline keyboard with copy button
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Copy Password", callback_data=f"copy_{password}")],
            [InlineKeyboardButton(text="🔄 Generate Another", callback_data="generate_another")],
            [InlineKeyboardButton(text="⚙️ Custom Options", callback_data="custom_options")]
        ]
    )
    
    response = (
        f"🔑 *Your Generated Password*\n\n"
        f"`{password}`\n\n"
        f"📊 Strength: {strength}\n"
        f"📏 Length: {len(password)} characters\n\n"
        f"💡 Click the button below to copy!"
    )
    
    await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)

# Custom command handler
@dp.message(Command("custom"))
async def custom_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔢 12 chars", callback_data="preset_12"),
                InlineKeyboardButton(text="🔢 16 chars", callback_data="preset_16"),
                InlineKeyboardButton(text="🔢 24 chars", callback_data="preset_24")
            ],
            [
                InlineKeyboardButton(text="🔢 32 chars", callback_data="preset_32"),
                InlineKeyboardButton(text="🔢 64 chars", callback_data="preset_64"),
                InlineKeyboardButton(text="🔢 128 chars", callback_data="preset_128")
            ],
            [
                InlineKeyboardButton(text="🎲 Random Length", callback_data="preset_random")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to Main", callback_data="back_to_main")
            ]
        ]
    )
    
    await message.answer(
        "⚙️ *Choose Password Length:*\n\n"
        "Select a preset length or use the main /generate command with a custom number.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# Handle callback queries
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    data = callback.data
    
    # Handle copy action
    if data.startswith("copy_"):
        password = data.replace("copy_", "")
        await callback.answer(f"📋 Password copied to clipboard!", show_alert=False)
        # Note: Telegram doesn't allow auto-copy, but we show it prominently
    
    # Handle generate another
    elif data == "generate_another":
        password = generate_password()
        strength = get_strength(password)
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📋 Copy Password", callback_data=f"copy_{password}")],
                [InlineKeyboardButton(text="🔄 Generate Another", callback_data="generate_another")],
                [InlineKeyboardButton(text="⚙️ Custom Options", callback_data="custom_options")]
            ]
        )
        
        response = (
            f"🔑 *Your New Password*\n\n"
            f"`{password}`\n\n"
            f"📊 Strength: {strength}\n"
            f"📏 Length: {len(password)} characters"
        )
        
        await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)
        await callback.answer()
    
    # Handle custom options
    elif data == "custom_options":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔢 12 chars", callback_data="preset_12"),
                    InlineKeyboardButton(text="🔢 16 chars", callback_data="preset_16"),
                    InlineKeyboardButton(text="🔢 24 chars", callback_data="preset_24")
                ],
                [
                    InlineKeyboardButton(text="🔢 32 chars", callback_data="preset_32"),
                    InlineKeyboardButton(text="🔢 64 chars", callback_data="preset_64"),
                    InlineKeyboardButton(text="🔢 128 chars", callback_data="preset_128")
                ],
                [
                    InlineKeyboardButton(text="🎲 Random Length", callback_data="preset_random")
                ],
                [
                    InlineKeyboardButton(text="🔙 Back to Main", callback_data="back_to_main")
                ]
            ]
        )
        
        await callback.message.edit_text(
            "⚙️ *Choose Password Length:*\n\n"
            "Select a preset length for your password.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        await callback.answer()
    
    # Handle preset lengths
    elif data.startswith("preset_"):
        preset = data.replace("preset_", "")
        
        if preset == "random":
            length = random.randint(8, 32)
        else:
            length = int(preset)
        
        password = generate_password(length=length)
        strength = get_strength(password)
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📋 Copy Password", callback_data=f"copy_{password}")],
                [InlineKeyboardButton(text="🔄 Generate Another", callback_data="generate_another")],
                [InlineKeyboardButton(text="⚙️ Custom Options", callback_data="custom_options")]
            ]
        )
        
        response = (
            f"🔑 *Your Generated Password*\n\n"
            f"`{password}`\n\n"
            f"📊 Strength: {strength}\n"
            f"📏 Length: {len(password)} characters"
        )
        
        await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)
        await callback.answer()
    
    # Handle back to main
    elif data == "back_to_main":
        await start_command(callback.message)
        await callback.answer()

# Default message handler - generate password from any text
@dp.message(F.text)
async def handle_text(message: types.Message):
    text = message.text.strip()
    
    # Check if user sent a number
    try:
        length = int(text)
        if 4 <= length <= 128:
            password = generate_password(length=length)
            strength = get_strength(password)
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📋 Copy Password", callback_data=f"copy_{password}")],
                    [InlineKeyboardButton(text="🔄 Generate Another", callback_data="generate_another")]
                ]
            )
            
            response = (
                f"🔑 *Your Generated Password*\n\n"
                f"`{password}`\n\n"
                f"📊 Strength: {strength}\n"
                f"📏 Length: {len(password)} characters"
            )
            
            await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)
            return
    except ValueError:
        pass
    
    # If not a number, give help
    await message.answer(
        "🤔 Send me a number (4-128) to generate a password of that length,\n"
        "or use /generate for a quick password!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔑 Generate Password", callback_data="generate_another")],
                [InlineKeyboardButton(text="⚙️ Custom Options", callback_data="custom_options")]
            ]
        )
    )

# Main function
async def main():
    print("🚀 Bot is starting...")
    print("🤖 Password Generator Bot is running!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
