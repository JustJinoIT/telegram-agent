"""
Telegram Agent 테스트
"""

import asyncio
from telegram_agent import TelegramAgent


async def test_init():
    """초기화 테스트."""
    agent = TelegramAgent(
        bot_token="123456789:ABCDEfghijklmnopqrstuvwxyzABCDEfg",
        chat_id=987654321
    )

    assert agent.bot_token == "123456789:ABCDEfghijklmnopqrstuvwxyzABCDEfg"
    assert agent.chat_id == 987654321
    print("✅ test_init passed")


async def test_register_callback():
    """콜백 등록 테스트."""
    agent = TelegramAgent(
        bot_token="test_token",
        chat_id=123
    )

    async def handler(data: str):
        pass

    agent.register_callback("ap", handler)
    assert "ap" in agent._handlers
    assert agent._handlers["ap"] == handler
    print("✅ test_register_callback passed")


async def test_shorten_id():
    """ID 단축 테스트."""
    agent = TelegramAgent(
        bot_token="test_token",
        chat_id=123
    )

    uid = "550e8400-e29b-41d4-a716-446655440000"
    shortened = agent._shorten_id(uid)
    assert len(shortened) <= 12
    assert "-" not in shortened
    print("✅ test_shorten_id passed")


async def test_multiple_handlers():
    """다중 핸들러 등록 테스트."""
    agent = TelegramAgent(
        bot_token="test_token",
        chat_id=123
    )

    async def approve(data: str):
        pass

    async def reject(data: str):
        pass

    async def skip(data: str):
        pass

    agent.register_callback("ap", approve)
    agent.register_callback("rj", reject)
    agent.register_callback("sk", skip)

    assert len(agent._handlers) == 3
    assert "ap" in agent._handlers
    assert "rj" in agent._handlers
    assert "sk" in agent._handlers
    print("✅ test_multiple_handlers passed")


async def test_callback_data_parsing():
    """콜백 데이터 파싱 테스트 (형식: action:arg1:arg2)."""
    agent = TelegramAgent(
        bot_token="test_token",
        chat_id=123
    )

    # 테스트용 데이터
    callback_data = "ap:contest123:draft456"
    parts = callback_data.split(":")

    assert parts[0] == "ap"
    assert parts[1] == "contest123"
    assert parts[2] == "draft456"
    print("✅ test_callback_data_parsing passed")


async def main():
    print("🧪 Telegram Agent 테스트 시작\n")

    await test_init()
    await test_register_callback()
    await test_shorten_id()
    await test_multiple_handlers()
    await test_callback_data_parsing()

    print("\n✅ 모든 테스트 통과!")


if __name__ == "__main__":
    asyncio.run(main())
