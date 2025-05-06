import os
from telegram_bot import TelegramBot
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = [
        "GROQ_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "ZEP_API_KEY",
        "ZEP_API_URL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your environment or .env file")
        return
    
    try:
        # Initialize and run the bot
        bot = TelegramBot()
        print("Bot started successfully!")
        bot.run()
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    main() 