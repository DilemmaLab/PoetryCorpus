# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Считыватель файлов разных расширений.

import os
import xml.etree.ElementTree as etree
import json
from enum import Enum
from typing import Iterator

from poetry.apps.corpus.scripts.main.markup import Markup
from poetry.apps.corpus.scripts.main.phonetics import Phonetics
from poetry.apps.corpus.scripts.accents.dict import AccentDict
from poetry.apps.corpus.scripts.accents.classifier import MLAccentClassifier
from poetry.apps.corpus.scripts.metre.metre_classifier import MetreClassifier


RAW_SEPARATOR = "\n\n\n"


class FileTypeEnum(Enum):
    RAW = ".txt"
    XML = ".xml"
    JSON = ".json"


class Reader(object):
    @staticmethod
    def read_markups(path: str, source_type: FileTypeEnum, is_processed: bool,
                     accents_dict: AccentDict=None, accents_classifier: MLAccentClassifier=None) -> Iterator[Markup]:
        paths = Reader.__get_paths(path, source_type.value)
        for filename in paths:
            with open(filename, "r", encoding="utf-8") as file:
                if is_processed:
                    if source_type == FileTypeEnum.XML:
                        for elem in Reader.__xml_iter(file, 'markup'):
                            markup = Markup()
                            markup.from_xml(etree.tostring(elem, encoding='utf-8', method='xml'))
                            yield markup
                    elif source_type == FileTypeEnum.JSON:
                        j = json.load(file)
                        for item in j['items']:
                            markup = Markup()
                            markup.from_json(item)
                            yield markup
                    elif source_type == FileTypeEnum.RAW:
                        raise NotImplementedError("Пока не реализовано.")
                else:
                    assert accents_dict is not None
                    assert accents_classifier is not None
                    for text in Reader.read_texts(filename, source_type):
                        yield Reader.__markup_text(text, accents_dict, accents_classifier)

    @staticmethod
    def read_texts(path: str, source_type: FileTypeEnum) -> Iterator[str]:
        paths = Reader.__get_paths(path, source_type.value)
        for filename in paths:
            with open(filename, "r", encoding="utf-8") as file:
                if source_type == FileTypeEnum.XML:
                    for elem in Reader.__xml_iter(file, 'item'):
                        yield elem.find(".//text").text
                elif source_type == FileTypeEnum.JSON:
                    # TODO: ленивый парсинг
                    j = json.load(file)
                    for item in j['items']:
                        yield item['text']
                elif source_type == FileTypeEnum.RAW:
                    text = file.read()
                    for t in text.split(RAW_SEPARATOR):
                        yield t

    @staticmethod
    def __get_paths(path: str, ext: str) -> Iterator[str]:
        if os.path.isfile(path):
            if ext == os.path.splitext(path)[1]:
                yield path
        else:
            for root, folders, files in os.walk(path):
                for file in files:
                    if ext == os.path.splitext(file)[1]:
                        yield os.path.join(root, file)
                for folder in folders:
                    return Reader.__get_paths(folder, ext)

    @staticmethod
    def __get_source_type(path):
        ext = ""
        current_path = path
        while ext != "":
            p = os.listdir(current_path)[0]
            ext = os.path.splitext(p)[1]
            current_path = p
        return FileTypeEnum(ext)

    @staticmethod
    def __markup_text(text: str, accents_dict: AccentDict=None,
                      accents_classifier: MLAccentClassifier=None) -> Markup:
        markup = Phonetics.process_text(text, accents_dict)
        markup = MetreClassifier.improve_markup(markup, accents_classifier)[0]
        return markup

    @staticmethod
    def __xml_iter(file, tag):
        return (elem for event, elem in etree.iterparse(file, events=['end']) if event == 'end' and elem.tag == tag)