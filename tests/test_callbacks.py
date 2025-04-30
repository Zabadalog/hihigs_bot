import pytest
from types import SimpleNamespace
from src import callbacks


class MockCallbackQuery:
    def __init__(self, data="button_pressed"):
        self.data = data
        self.from_user = SimpleNamespace(id=123, username="testuser")
        self.message = SimpleNamespace()
        self._answer_text = None
        self._message_answer = None

        self.message.answer = self._mock_message_answer
        self.answer_called = False

    async def answer(self, text=None):
        self._answer_text = text
        self.answer_called = True
        print(f"[Callback.answer()]: {text}")

    async def _mock_message_answer(self, text):
        self._message_answer = text
        print(f"[Callback.message.answer()]: {text}")
        return text


@pytest.mark.asyncio
async def test_on_button_pressed():
    cb = MockCallbackQuery(data="button_pressed")
    await callbacks.on_button(cb)

    assert cb.answer_called
    assert cb._answer_text == "Кнопка нажата"
    assert cb._message_answer == "Обработка выполнена"
    
    
