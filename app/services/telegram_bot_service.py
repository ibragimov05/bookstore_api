# import logging
#
# from telegram import Update
# from telegram.ext import (
# 	Application, CommandHandler, ContextTypes, filters, MessageHandler
# )
#
# from app.core.utils.get_db import DB_DEPENDENCY
# from app.db.models import TelegramUser, User
#
# logging.basicConfig(
# 	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# logger = logging.getLogger(__name__)
#
#
# class TelegramBotService:
# 	def __init__(self, db: DB_DEPENDENCY):
# 		self.db = db
# 		self.user_states = {}
#
# 		self.application = Application.builder().token("YOUR_BOT_TOKEN").build()
#
# 		self.application.add_handler(CommandHandler("start", self.start))
# 		self.application.add_handler(CommandHandler("help", self.help_command))
# 		self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
#
# 	def run(self):
# 		"""Run bot"""
# 		self.application.run_polling()
#
# 	async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# 		"""Start command - asks for login"""
# 		user_id = update.effective_user.id
# 		self.user_states[user_id] = {"step": "awaiting_login"}
#
# 		tg_user = self.db.query(TelegramUser).filter(TelegramUser.chat_id == user_id).first()
#
# 		if tg_user is None:
# 			await update.message.reply_text("Please enter your login:")
# 		else:
# 			await update.message.reply_text("✅ You are already logged in.")
#
# 	async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# 		"""Handles user input for login and password"""
# 		user_id = update.effective_user.id
# 		text = update.message.text
#
# 		if user_id not in self.user_states:
# 			await update.message.reply_text("Please use /start to begin login.")
# 			return
#
# 		user_state = self.user_states[user_id]
#
# 		if user_state["step"] == "awaiting_login":
# 			user_state["login"] = text
# 			user_state["step"] = "awaiting_password"
# 			await update.message.reply_text("Now enter your password:")
#
# 		elif user_state["step"] == "awaiting_password":
# 			user_state["password"] = text
#
# 			# Fetch user from the database
# 			user_in_db = self.db.query(User).filter(User.username == user_state["login"]).first()
#
# 			if user_in_db is None:
# 				await update.message.reply_text("❌ User not found. Try again with /start.")
# 				del self.user_states[user_id]
# 				return
#
# 			if not user_in_db.verify_password():  # Assuming you have a password verification method
# 				await update.message.reply_text("❌ Invalid password. Try again with /start.")
# 				del self.user_states[user_id]
# 				return
#
# 			if not user_in_db.is_admin:
# 				await update.message.reply_text("❌ You are not an admin. Try again with /start.")
# 				del self.user_states[user_id]
# 				return
#
# 			# Check if TelegramUser already exists
# 			telegram_user = self.db.query(TelegramUser).filter(TelegramUser.chat_id == user_id).first()
#
# 			if telegram_user is None:
# 				telegram_user = TelegramUser(
# 					chat_id=user_id,
# 					username=user_in_db.username,
# 					user_id=user_in_db.id,
# 				)
# 				self.db.add(telegram_user)
# 				self.db.commit()
#
# 			await update.message.reply_text(f"✅ Login successful! Welcome, {user_in_db.username}.")
#
# 			# Clear user state after successful login
# 			del self.user_states[user_id]
#
# 	async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# 		"""Help command"""
# 		await update.message.reply_text("Use /start to login.")
