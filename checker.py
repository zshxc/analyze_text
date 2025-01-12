from pyaspeller import YandexSpeller
import re
import asyncio

class GrammarChecker:

    def __init__(self, text: str) -> None:
        self.text = text
        self.speller = YandexSpeller()
        self.errors = []

    async def check_text(self) -> None:
        self.errors = await asyncio.to_thread(list, self.speller.spell(self.text))

        punctuation_errors = self.check_punctuation()
        self.errors.extend(punctuation_errors)

    def check_punctuation(self) -> list:

        errors = []
        for match in re.finditer(r"[.,!?;:]([^\s])", self.text):
            errors.append({
                "word": match.group(0),
                "pos": match.start(),
                "s": [f"{match.group(0)} {match.group(1)}"],
                "code": 4,  # Код для пунктуационных ошибок
            })
        return errors

    def get_errors(self) -> list:
        return self.errors