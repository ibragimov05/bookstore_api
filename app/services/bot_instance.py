from app.core.utils.get_db import get_db
from app.services.telegram_bot_service import TelegramBotService

bot_service = TelegramBotService(db=get_db())
