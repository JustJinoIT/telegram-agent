# Telegram Agent 🤖

FastAPI + Telegram.ext 통합 봇 프레임워크.

## 특징

- 📨 **메시지**: 텍스트, 버튼, 콜백
- ⚡ **비동기**: 모든 작업이 async
- 🔌 **콜백 라우팅**: 버튼 클릭 자동 처리
- 📝 **명령어 처리**: /start, /help 등

## 설치

```bash
pip install telegram-agent
```

## 사용법

```python
import asyncio
from fastapi import FastAPI, Request
from telegram_agent import TelegramAgent

app = FastAPI()
agent = TelegramAgent(
    bot_token="6123456789:ABCDEfghijklmnopqrstuvwxyzABCDEfg",
    chat_id=123456789
)

# 콜백 핸들러 등록
async def handle_approve(callback_data: str):
    """사용자가 ✅ 승인 버튼 클릭"""
    parts = callback_data.split(":")
    contest_id = parts[1] if len(parts) > 1 else "unknown"
    await agent.send_message(f"✅ {contest_id} 승인됨")

agent.register_callback("ap", handle_approve)

# Telegram 웹훅
@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    await agent.handle_update(data)
    return {"ok": True}

# 메시지 전송
@app.post("/notify")
async def notify():
    await agent.send_message("🎯 새로운 공모전이 등록되었습니다!")
    return {"sent": True}

# 버튼 메시지
@app.post("/review")
async def review():
    buttons = [
        [("✅ 승인", "ap:123"), ("❌ 거부", "rj:123")],
        [("✏️ 수정", "edit:123")],
    ]
    await agent.send_buttons("검토하실까요?", buttons)
    return {"sent": True}
```

## API

### `TelegramAgent(bot_token, chat_id)`

초기화.

### `await agent.send_message(text, reply_markup=None, parse_mode=None)`

메시지 전송.

- `parse_mode`: "Markdown" 또는 "HTML"

### `await agent.send_buttons(text, buttons, parse_mode="Markdown")`

버튼과 함께 메시지 전송.

```python
buttons = [
    [("라벨1", "action1"), ("라벨2", "action2")],
    [("라벨3", "action3")],
]
await agent.send_buttons("선택하세요:", buttons)
```

### `agent.register_callback(action, handler)`

콜백 핸들러 등록.

```python
async def on_approve(callback_data: str):
    # callback_data = "ap:id1:id2" 형식
    pass

agent.register_callback("ap", on_approve)
```

### `await agent.handle_update(data)`

Telegram 웹훅 처리.

## 환경 변수

```bash
export TELEGRAM_BOT_TOKEN=6123456789:ABCDEfghijklmnopqrstuvwxyzABCDEfg
export TELEGRAM_CHAT_ID=123456789
```

## 라이선스

MIT
