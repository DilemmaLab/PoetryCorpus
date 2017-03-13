# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Класс для удобной работы со словарём ударений.

import datrie
import os
from typing import List, Tuple
from enum import Enum

from poetry.apps.corpus.scripts.util.preprocess import CYRRILIC_LOWER_VOWELS, CYRRILIC_LOWER_CONSONANTS


class AccentType(Enum):
    ANY = -1
    PRIMARY = 0
    SECONDARY = 1


class AccentDict:
    """
    Класс данных, для сериализации словаря как dict'а и быстрой загрузки в память.
    """
    def __init__(self, accents_filename: str) -> None:
        """
        :param accents_filename: имя файла со словарём, без расширения.
        """
        self.data = datrie.Trie(CYRRILIC_LOWER_VOWELS+CYRRILIC_LOWER_CONSONANTS+"-")
        src_filename = accents_filename + '.txt'
        dst_filename = accents_filename + '.trie'
        if not os.path.isfile(src_filename):
            raise FileNotFoundError("Не найден файл словаря.")
        if os.path.isfile(dst_filename):
            self.data = datrie.Trie.load(dst_filename)
        else:
            self.create(src_filename, dst_filename)

    def create(self, src_filename: str, dst_filename: str) -> None:
        """
        Загрузка словаря из файла. Если уже есть его сериализация в .trie файле, берём из него.

        :param src_filename: имя файла с оригинальным словарём.
        :param dst_filename: имя файла, в который будет сохранён дамп.
        """
        with open(src_filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                for word in line.split("#")[1].split(","):
                    word = word.strip()
                    pos = -1
                    accents = []
                    clean_word = ""
                    for i in range(len(word)):
                        if word[i] == "'" or word[i] == "`":
                            if word[i] == "`":
                                accents.append((pos, AccentType.SECONDARY))
                            else:
                                accents.append((pos, AccentType.PRIMARY))
                            continue
                        clean_word += word[i]
                        pos += 1
                        if word[i] == "ё":
                            accents.append((pos, AccentType.PRIMARY))
                    self.__update(clean_word, accents)
        self.data.save(dst_filename)

    def save(self, dst_filename: str) -> None:
        """
        Сохранение дампа.

        :param dst_filename: имя файла, в который сохраняем дамп словаря.
        """
        self.data.save(dst_filename)

    def get_accents(self, word: str, accent_type: AccentType=AccentType.ANY) -> List[int]:
        """
        Обёртка над data.get().

        :param word: слово, которое мы хотим посмотреть в словаре.
        :param accent_type: тип ударения.
        :return forms: массив всех ударений.
        """
        if word in self.data:
            if accent_type == AccentType.ANY:
                return [i[0] for i in self.data[word]]
            else:
                return [i[0] for i in self.data[word] if i[1] == accent_type]
        return []

    def get_all(self) -> List[Tuple[str, List[Tuple[int, AccentType]]]]:
        """
        Получение всех элементов словаря.

        :return items: все ключи и ударения словаря.
        """
        return self.data.items()

    def __update(self, word: str, accent_pairs: List[Tuple[int, AccentType]]) -> None:
        """
        Обновление словаря.

        :param word: слово.
        :param accent_pairs: набор ударений.
        """
        if word not in self.data:
            self.data[word] = set(accent_pairs)
        else:
            self.data[word].update(accent_pairs)