from pyaspeller import YandexSpeller
import re
import asyncio

class GrammarChecker:
    """
    Класс для проверки грамматических, орфографических и пунктуационных ошибок.
    """

    def __init__(self, text: str) -> None:
        """
        Инициализирует экземпляр класса GrammarChecker.

        Аргументы:
            text (str): Текст для проверки.
        """
        self.text = text
        self.speller = YandexSpeller()
        self.errors = []

    async def check_text(self) -> None:
        """
        Асинхронно проверяет текст на наличие ошибок.
        """
        # Проверка орфографии и грамматики
        self.errors = await asyncio.to_thread(list, self.speller.spell(self.text))

        # Проверка пунктуации
        punctuation_errors = self.check_punctuation()
        self.errors.extend(punctuation_errors)

    def check_punctuation(self) -> list:
        """
        Проверяет текст на пунктуационные ошибки.

        Возвращает:
            list: Список пунктуационных ошибок.
        """
        errors = []
        # Пример: проверка отсутствия пробела после знаков препинания
        for match in re.finditer(r"[.,!?;:]([^\s])", self.text):
            errors.append({
                "word": match.group(0),
                "pos": match.start(),
                "s": [f"{match.group(0)} {match.group(1)}"],
                "code": 4,  # Код для пунктуационных ошибок
            })
        return errors

    def get_errors(self) -> list:
        """
        Возвращает список ошибок.

        Возвращает:
            list: Список ошибок.
        """
        return self.errors