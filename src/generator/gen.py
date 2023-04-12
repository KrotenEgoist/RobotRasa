import random
import re

import pymorphy2

from pathlib import Path


class Generator:
    def __init__(self, dictionary_path: Path):
        self.dictionary_path = dictionary_path
        self.dictionary_files = self.dictionary_path.glob("**/*/*")
        self.dictionary = self.create_dictionary()
        self.morph = pymorphy2.MorphAnalyzer()
        self.key_pattern = re.compile(r'\w+:\w+')
        self.word_pattern = re.compile(r'([\w\s-]+)')

    def create_dictionary(self) -> dict:
        """
        Создает словарь из директории dictionary

        Ключ - путь до файла со словами, пример action:move, object:house
        Значение - содержимое файла со словами в виде списка

        :return
            Словарь: {
                "action:move": ["идти", "двигаться", "направляться"],
                "object:house": ["дом", "изба", "строение"],
                ...
            }
        """
        dictionary = {}
        for path_to_file in self.dictionary_files:
            key = ':'.join(path_to_file.parts[-2:])
            with open(path_to_file, 'r') as values_file:
                value = values_file.read()
                value = value.strip()
                value = value.split('\n')

            dictionary[key] = value

        return dictionary

    def get_keys(self, dictionary_name: str) -> list:
        """
        Создает список всех ключей для конкретного словаря

        :param dictionary_name: Имя директории с файлами словаря внутри src/generator/dictionary
        :return:
            Список ключей, пример ['action:move', 'action:rotate', ... ]
        """
        pattern = f'**/{dictionary_name}/*'
        key_path = list(self.dictionary_path.glob(pattern))
        keys = list(map(lambda x: ':'.join(x.parts[-2:]), key_path))

        return keys

    def inflect(self, words: str, grammes: set) -> str:
        """
        Преобразует слово в соответствии с граммемами (http://opencorpora.org/dict.php?act=gram)

        :param words: слово/слова в нормальной форме, пример: "идти"
        :param grammes: множество граммем, пример: {'excl'}
        :return:
            Измененное слово: "идти", {'excl'} -> "иди"
        """
        morphed = []
        words = words.split(" ")

        # Если слов несколько, то все слова склоняются в род существительного
        if len(words) > 1:
            idx = list(map(lambda x: self.morph.parse(x)[0].tag.POS, words)).index('NOUN')
            noun = words[idx]
            noun_parsed = self.morph.parse(words[idx])[0]
            gender = noun_parsed.tag.gender
            animacy = noun_parsed.tag.animacy

            words.remove(noun)

            # Иногда согласование зависит от одушевленности
            try:
                words = list(map(lambda x: self.morph.parse(x)[0].inflect({gender, animacy}).word, words))
            except AttributeError:
                words = list(map(lambda x: self.morph.parse(x)[0].inflect({gender}).word, words))

            words.append(noun)

        for word in words:
            try:
                morph = self.morph.parse(word)[0]
                inflected = morph.inflect(grammes)
                new_word = inflected.word
            except AttributeError:
                new_word = word

            morphed.append(new_word)

        return ' '.join(morphed)

    def ner(self, sample: str) -> (str, str):
        """
        Добавление разметки сущностей для шаблонов

        :param sample: шаблон
        :return:
            шаблон для склонений и шаблон для подстановки
        """
        sample_to_inflect, edited_sample = sample, sample

        keys = self.key_pattern.findall(sample)
        for key in keys:
            random_word = random.choice(self.dictionary[key])

            # выделение сущностей
            # ...

            sample_to_inflect = sample_to_inflect.replace(key, random_word)
            edited_sample = edited_sample.replace(key, random_word)

        return sample_to_inflect, edited_sample

    def create(self, sample: str) -> str:
        """
        Подставляет случайные слова из словаря в шаблон, применяет преобразование слов

        :param sample: Шаблон, пример "prep:robot action:patrol"
            Словарь: {
                "prep:robot": ["-excl", "-excl-plur"],
                "action:patrol" ["патрулировать", "разведывать", "охранять"],
                ...
            }

            P.S.: для работы преобразования слов, необходимо указывать в файлах словаря требуемые граммемы,
            пример для файла prep:robot: "-excl" означает, что преобразование применится к следующему слову в шаблоне
        :return:
            измененная строка в соответствии с выбранными значениями словаря

        """
        sample_to_inflect, edited_sample = self.ner(sample)

        # Извлечение слов для склонения по шаблону
        words = self.word_pattern.findall(sample_to_inflect)

        case = None
        for stuff in words:
            word_and_case = stuff.split('-')

            word = word_and_case[0]

            if case:
                new_word = self.inflect(word, set(case))
            else:
                new_word = word

            case = word_and_case[1:]
            edited_sample = edited_sample.replace('-'.join(case), '')

            if new_word:
                # Корректная замена слов в шаблоне с учетом сущностей
                for new, old in zip(new_word.split(" "), word.split(" ")):
                    edited_sample = edited_sample.replace(old, new)

        edited_sample = edited_sample.replace('-', '')
        edited_sample = edited_sample.replace('|', ' ')
        edited_sample = edited_sample.strip()

        return edited_sample

    def run(self, samples: list, amount: int, start=None, end=None) -> list:
        """
        Используя шаблоны samples, генерирует команды в количестве amount на каждый шаблон

        Если указан диапазон чисел start, end - подставляет случайное число из диапазона в команду

        :param samples: список шаблонов
        :param amount: количество примеров на один шаблон
        :param start: начальное случайное число
        :param end: конечное случайное число
        :return:
            Список сгенерированных команд по шаблонам
        """
        cmd_list = []
        for sample in samples:
            for i in range(amount):
                example = self.create(sample)
                if start and end:
                    n = random.randint(start, end)
                    example = example.replace("$", str(n))

                cmd_list.append(example)

        return cmd_list

    @staticmethod
    def save(data: dict, path: Path) -> None:
        """
        Сохраняет сгенерированные данные в формат для rasa nlu

        Шапка данных rasa nlu:
        --------------
        version: "3.1"

        nlu:
        - intent: название_намерения
          examples: |
        --------------

        :param data: словарь сгенерированных данных ключ - тип действия, значение - список команд
        :param path: путь до данных rasa nlu
        """
        for key, values in data.items():
            # составление списка уникальных команд и случайное перемешивание
            uniq = list(set(values))
            random.shuffle(uniq)

            filename = f"intent_{key}.yml"
            save_path = path.joinpath(filename)
            head = f'version: "3.1"\n\nnlu:\n- intent: {key}\n  examples: |\n'
            with open(save_path, 'w') as file:
                file.write(head)

                for val in uniq:
                    text = f'    - {val}\n'
                    file.write(text)
