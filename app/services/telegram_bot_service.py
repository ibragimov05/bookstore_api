import os
from typing import List

import httpx
from sqlalchemy.orm import Session
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler

from app.core.utils.get_db import get_db
from app.db.models import Order, TelegramUser


class TelegramBotService:
	def __init__(self):
		self.token = os.getenv("TELEGRAM_BOT_TOKEN")
		self.application = Application.builder().token(self.token).build()
		self._setup_handlers()

	def _setup_handlers(self):
		"""Setup message and command handlers"""
		self.application.add_handler(CommandHandler("start", self.start))
		self.application.add_handler(CommandHandler("help", self.help_command))
		self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

	async def start_polling(self):
		await self.application.initialize()
		await self.application.start()
		await self.application.updater.start_polling()

	async def run(self):
		await self.start_polling()

	async def stop(self):
		"""Properly stop the bot"""
		if hasattr(self.application, 'updater') and self.application.updater:
			await self.application.updater.stop()
		await self.application.stop()
		await self.application.shutdown()

	def save_user_to_db(self, chat_id: int, username: str = None) -> TelegramUser:
		"""Save or update user in database"""
		db: Session = next(get_db())
		try:
			user = db.query(TelegramUser).filter(TelegramUser.chat_id == chat_id).first()
			if not user:
				user = TelegramUser(chat_id=chat_id, username=username)
				db.add(user)
			else:
				user.username = username  # Update username if changed
			db.commit()
			db.refresh(user)
			return user
		except Exception as e:
			db.rollback()
			raise e
		finally:
			db.close()

	def get_all_users(self) -> List[TelegramUser]:
		"""Get all registered telegram users"""
		db: Session = next(get_db())
		try:
			return db.query(TelegramUser).all()
		finally:
			db.close()

	async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		"""Handle the /start command and save new users to the database"""
		user = update.effective_user
		chat_id = update.message.chat_id

		try:
			saved_user = self.save_user_to_db(chat_id, user.username)
			await update.message.reply_html(
				rf"Hi {user.mention_html()}! Your Telegram ID has been saved.",
				reply_markup=ForceReply(selective=True),
			)
		except Exception as e:
			await update.message.reply_text(
				f"""Sorry, there was an error saving your information. Please try again later.
				```
				{e}
				```
				""",
				parse_mode="Markdown",
			)

	async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		await update.message.reply_text("Use /start to register for order notifications.")

	async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		await update.message.reply_text(update.message.text)

	async def send_order_to_telegram_bot(self, order: Order):
		"""Sends order details to all registered Telegram users"""
		text = (
			f"📦 *New Order Received!*\n\n"
			f"🆔 *Order ID:* `{order.id}`\n"
			f"👤 *User ID:* `{order.user_id}`\n"
			f"💰 *Total Amount:* `${order.total_amount:.2f}`\n"
			f"📦 *Total Quantity:* `{order.total_quantity}`\n"
			f"📌 *Status:* `{order.status}`\n"
			f"📅 *Created At:* `{order.created_at.strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
			f"🛒 *Order Items:*\n"
		)

		for item in order.order_items:
			text += (
				f"  - 📖 *Book ID:* `{item.book_id}`\n"
				f"    🔢 *Quantity:* `{item.quantity}`\n"
				f"    💲 *Price per Item:* `${item.price_per_item:.2f}`\n\n"
			)

		telegram_users = self.get_all_users()

		if not telegram_users:
			return {"status": "error", "message": "No registered Telegram users."}

		failed_users = []
		success_count = 0

		async with httpx.AsyncClient() as client:
			for user in telegram_users:
				try:
					payload = {
						"chat_id": user.chat_id,
						"text": text,
						"parse_mode": "Markdown",
						"disable_web_page_preview": True
					}
					response = await client.post(
						f'https://api.telegram.org/bot{self.token}/sendMessage',
						json=payload,
						timeout=10.0
					)
					if response.status_code == 200:
						success_count += 1
					else:
						failed_users.append(user.chat_id)
				except Exception as e:
					failed_users.append(user.chat_id)

		return {
			"status": "success" if success_count > 0 else "error",
			"message": f"Notification sent to {success_count} users. Failed for {len(failed_users)} users.",
			"failed_users": failed_users
		}
