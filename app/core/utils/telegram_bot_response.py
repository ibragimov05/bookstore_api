import os

import httpx

from app.db.models import Order

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = -4618071305


async def send_order_notification_to_telegram(order: Order):
	text = (
		f"🛒 *New Order Placed!* \n\n"
		f"📦 *Order ID:* `{order.id}`\n"
		f"👤 *User ID:* #ID{order.user_id}\n"
		f"💰 *Total Amount:* `${order.total_amount:.2f}`\n"
		f"📦 *Total Items:* `{order.total_quantity}`\n"
		f"🕒 *Ordered At:* `{order.created_at.strftime('%Y-%m-%d %H:%M:%S')}`\n"
		f"📌 *Status:* `{order.status}`\n"
	)

	payload = {
		"chat_id": TELEGRAM_CHAT_ID,
		"text": text,
		"parse_mode": "Markdown"
	}

	async with httpx.AsyncClient() as client:
		response = await client.post(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage', json=payload)
		from json import loads
		return {"status": response.status_code, "message": loads(response.text)}
