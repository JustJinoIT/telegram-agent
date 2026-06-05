"""
Telegram Agent — FastAPI + Telegram.ext 통합 프레임워크

특징:
  - 메시지/버튼/콜백 처리
  - 비동기 메시지 전송
  - 콜백 라우팅
  - 액션 로깅
"""

from typing import Optional, Callable, Dict, Any
import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters

logger = logging.getLogger(__name__)


class TelegramAgent:
    def __init__(self, bot_token: str, chat_id: int):
        """
        Args:
            bot_token: Telegram Bot Token
            chat_id: 메시지를 받을 Chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self._bot: Optional[Bot] = None
        self._app: Optional[Application] = None
        self._handlers: Dict[str, Callable] = {}

    def _get_bot(self) -> Bot:
        if self._bot is None:
            self._bot = Bot(token=self.bot_token)
        return self._bot

    def _get_app(self) -> Application:
        if self._app is None:
            self._app = Application.builder().token(self.bot_token).build()
        return self._app

    async def send_message(
        self, text: str, reply_markup=None, parse_mode: str = None
    ) -> None:
        """메시지 전송."""
        bot = self._get_bot()
        await bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )

    async def send_buttons(
        self,
        text: str,
        buttons: list[list[tuple[str, str]]],
        parse_mode: str = "Markdown",
    ) -> None:
        """
        버튼과 함께 메시지 전송.

        Args:
            text: 메시지 텍스트
            buttons: 버튼 목록 (2중 리스트) — [(라벨, callback_data), ...]
            parse_mode: "Markdown" 또는 "HTML"

        Example:
            buttons = [
                [("✅ 승인", "ap:123"), ("❌ 거부", "rj:123")],
                [("수정", "edit:123")],
            ]
        """
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(label, callback_data=data)
                    for label, data in row
                ]
                for row in buttons
            ]
        )
        await self.send_message(text, reply_markup=keyboard, parse_mode=parse_mode)

    def register_callback(self, action: str, handler: Callable) -> None:
        """
        콜백 핸들러 등록.

        Args:
            action: 콜백 액션명 (예: "ap" for approve)
            handler: async def handler(callback_data: str) -> None

        Example:
            agent.register_callback("ap", handle_approve)
        """
        self._handlers[action] = handler

    async def handle_update(self, data: dict) -> None:
        """
        Telegram 웹훅 업데이트 처리.

        Args:
            data: Telegram 웹훅 JSON
        """
        app = self._get_app()
        update = Update.de_json(data, app.bot)

        # 콜백 쿼리 (버튼 클릭)
        if update.callback_query:
            cq = update.callback_query
            await cq.answer()
            callback_data = cq.data

            # 액션 추출 (format: "action:arg1:arg2")
            parts = callback_data.split(":")
            action = parts[0] if parts else ""

            if action in self._handlers:
                await self._handlers[action](callback_data)
                logger.info(f"✅ Callback processed: {action}")
            else:
                logger.warning(f"⚠️ Unknown callback: {action}")

        # 텍스트 메시지
        elif update.message and update.message.text:
            text = update.message.text.strip()
            logger.info(f"📨 Message: {text[:50]}")

            # 명령어 처리
            if text.startswith("/"):
                await self._handle_command(text)

    async def _handle_command(self, cmd: str) -> None:
        """명령어 처리."""
        parts = cmd.split()
        command = parts[0].lower()
        logger.info(f"🔧 Command: {command}")

    def _shorten_id(self, uid: str) -> str:
        """UUID를 12자로 단축 (Telegram callback_data 64byte 제한)."""
        return uid.replace("-", "")[:12]
