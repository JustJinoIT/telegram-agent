"""
Telegram Conversation Manager - Telegram 봇을 더 지능적으로

기존 telegram-agent의 문제:
  - 단순 메시지 전송만
  - python-telegram-bot과 중복
  - 상태 관리 없음

새로운 ConversationManager의 가치:
  - 대화 상태 추적 (사용자별)
  - Context memory (이전 메시지 기억)
  - Button templates (재사용 가능)
  - Error handling (일관된 처리)
  - Session management (타임아웃)
"""

from typing import Optional, Dict, Callable, Any
from datetime import datetime, timedelta
from enum import Enum

class ConversationState(str, Enum):
    """대화 상태"""
    IDLE = "idle"
    WAITING_INPUT = "waiting_input"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class Conversation:
    """사용자 대화 세션"""

    def __init__(self, user_id: int, timeout_seconds: int = 3600):
        self.user_id = user_id
        self.state = ConversationState.IDLE
        self.context: Dict[str, Any] = {}
        self.history: list[Dict] = []
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.timeout_seconds = timeout_seconds

    def add_message(self, role: str, content: str) -> None:
        """대화 히스토리에 메시지 추가"""
        self.history.append({
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.last_activity = datetime.utcnow()

    def get_context(self, key: str) -> Optional[Any]:
        """컨텍스트 조회"""
        return self.context.get(key)

    def set_context(self, key: str, value: Any) -> None:
        """컨텍스트 저장"""
        self.context[key] = value

    def is_expired(self) -> bool:
        """세션 타임아웃 확인"""
        elapsed = (datetime.utcnow() - self.last_activity).total_seconds()
        return elapsed > self.timeout_seconds

    def reset(self) -> None:
        """대화 초기화"""
        self.state = ConversationState.IDLE
        self.context.clear()
        self.history.clear()

class TelegramConversationManager:
    """Telegram 봇의 대화를 관리"""

    def __init__(self):
        self.conversations: Dict[int, Conversation] = {}
        self.handlers: Dict[str, Callable] = {}

    def get_conversation(self, user_id: int) -> Conversation:
        """사용자 대화 세션 조회 (없으면 생성)"""
        if user_id not in self.conversations:
            self.conversations[user_id] = Conversation(user_id)
        return self.conversations[user_id]

    def register_handler(self, action: str, handler: Callable) -> None:
        """액션에 대한 핸들러 등록

        Example:
            manager.register_handler("draft_review", async def handler(conv):
                # draft 검토 로직
        """
        self.handlers[action] = handler

    async def handle_action(self, user_id: int, action: str, data: Dict) -> str:
        """액션 처리"""
        conv = self.get_conversation(user_id)
        handler = self.handlers.get(action)

        if not handler:
            return "❌ 알 수 없는 액션"

        try:
            conv.state = ConversationState.PROCESSING
            result = await handler(conv, data)
            conv.state = ConversationState.COMPLETED
            return result
        except Exception as e:
            conv.state = ConversationState.ERROR
            return f"❌ 오류 발생: {str(e)[:100]}"

    def cleanup_expired(self) -> int:
        """만료된 세션 정리"""
        expired_users = [
            uid for uid, conv in self.conversations.items()
            if conv.is_expired()
        ]
        for uid in expired_users:
            del self.conversations[uid]
        return len(expired_users)

    @staticmethod
    def create_button_template(action: str, label: str) -> Dict:
        """버튼 템플릿 생성

        Example:
            approve_btn = create_button_template("approve_draft", "✅ 승인")
        """
        return {"action": action, "label": label}

    @staticmethod
    def create_menu(buttons: list[Dict]) -> str:
        """메뉴 생성"""
        menu = "선택하세요:\n"
        for i, btn in enumerate(buttons, 1):
            menu += f"{i}. {btn['label']}\n"
        return menu
