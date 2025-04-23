import pytest
from types import SimpleNamespace
from src import handlers


class MockMessage:
    def __init__(self, text="/start"):
        self.text = text
        self.from_user = SimpleNamespace(id=123, username="testuser", first_name="Test")
        self.chat = SimpleNamespace(id=456)
        self._answered_text = None
        self._reply_markup = None

    async def answer(self, text, reply_markup=None):
        self._answered_text = text
        self._reply_markup = reply_markup
        print(f"[Ответ бота]: {text}")
        return text


@pytest.mark.asyncio
async def test_start_handler():
    msg = MockMessage(text="/start")
    await handlers.process_start_command(msg)
    assert msg._answered_text is not None
    assert "привет" in msg._answered_text.lower()


@pytest.mark.asyncio
async def test_help_handler():
    msg = MockMessage(text="/help")
    await handlers.process_help_command(msg)
    assert msg._answered_text is not None
    assert "/help" in msg._answered_text
