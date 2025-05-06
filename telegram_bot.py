import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq_agent import GroqAgent
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class TelegramBot:
    def __init__(self):
        self.agent = GroqAgent()
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user_id = str(update.effective_user.id)
        welcome_message = (
            "👋 Olá! Eu sou um assistente AI baseado no Groq.\n\n"
            "Posso ajudar você com várias tarefas e manter memória das nossas conversas.\n"
            "Use /help para ver os comandos disponíveis."
        )
        await update.message.reply_text(welcome_message)
        
        # Store initial user preference
        self.agent.update_user_memory(user_id, "language", "pt-BR")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        help_text = (
            "🤖 Comandos disponíveis:\n\n"
            "/start - Iniciar o bot\n"
            "/help - Mostrar esta mensagem de ajuda\n"
            "/tools - Listar todas as ferramentas disponíveis\n"
            "/memory - Mostrar suas memórias armazenadas\n"
            "/clear - Limpar suas memórias\n\n"
            "Você também pode simplesmente me enviar mensagens e eu responderei!"
        )
        await update.message.reply_text(help_text)

    async def list_tools(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all available tools."""
        tools = self.agent.tool_registry.get_tools()
        if not tools:
            await update.message.reply_text("Nenhuma ferramenta disponível no momento.")
            return

        tools_text = "🛠️ Ferramentas disponíveis:\n\n"
        for tool in tools:
            tools_text += f"• {tool['name']}: {tool['description']}\n"
            tools_text += f"  Parâmetros: {tool['parameters']}\n"
            tools_text += f"  Criado em: {tool['created_at']}\n"
            tools_text += f"  Última modificação: {tool['last_modified']}\n\n"

        await update.message.reply_text(tools_text)

    async def show_memory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's stored memories."""
        user_id = str(update.effective_user.id)
        memories = self.agent.memory_manager.get_memories(user_id)
        
        if not memories:
            await update.message.reply_text("Você ainda não tem memórias armazenadas.")
            return

        memory_text = "🧠 Suas memórias:\n\n"
        for key, value in memories.items():
            memory_text += f"• {key}: {value}\n"

        await update.message.reply_text(memory_text)

    async def clear_memory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear user's stored memories."""
        user_id = str(update.effective_user.id)
        self.agent.memory_manager.clear_memories(user_id)
        await update.message.reply_text("✅ Suas memórias foram limpas com sucesso!")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        user_id = str(update.effective_user.id)
        message_text = update.message.text

        # Send "typing" action
        await update.message.chat.send_action(action="typing")

        try:
            # Process message with Groq agent
            response = self.agent.process_message(user_id, message_text)
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
            )

    def run(self):
        """Start the bot."""
        # Create the Application
        application = Application.builder().token(self.token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(CommandHandler("tools", self.list_tools))
        application.add_handler(CommandHandler("memory", self.show_memory))
        application.add_handler(CommandHandler("clear", self.clear_memory))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Start the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        logger.error(f"Error starting bot: {e}") 