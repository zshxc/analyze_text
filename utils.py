def get_error_description(error_code: int) -> str:

    descriptions = {
        1: "Орфографическая ошибка.",
        2: "Повтор слова.",
        3: "Неверное использование заглавных букв.",
        4: "Пунктуационная ошибка.",
    }
    return descriptions.get(error_code, "Неизвестная ошибка.")