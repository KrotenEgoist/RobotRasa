import random
import re
import pymorphy2

from pathlib import Path


class Generator:
    def __init__(self, dictionary_path: Path):
        self.dictionary_files = dictionary_path.glob("**/*/*")
        self.dictionary = self.create_dictionary()
        self.morph = pymorphy2.MorphAnalyzer()
        self.key_pattern = re.compile(r'\w+:\w+')
        self.word_pattern = re.compile(r'\|([\w\s,]+)')

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
            gender = self.morph.parse(words[idx])[0].tag.gender
            words = list(map(lambda x: self.morph.parse(x)[0].inflect({gender}).word, words))

        for word in words:
            try:
                morph = self.morph.parse(word)[0]
                inflected = morph.inflect(grammes)
                new_word = inflected.word
            except AttributeError:
                new_word = word

            morphed.append(new_word)

        return ' '.join(morphed)

    def create(self, sample: str):
        """
        Подставляет случайные слова из словаря в шаблон, применяет преобразование слов

        Ключи для словаря извлекаются регулярным выражением

        :param sample: Шаблон, пример "prep:robot action:patrol"
            Словарь: {
                "prep:robot": [",excl", ",excl,plur"],
                "action:patrol" ["патрулировать", "разведывать", "охранять"],
                ...
            }

            P.S.: для работы преобразования слов, необходимо указывать в файлах словаря требуемые граммемы,
            пример для файла prep:robot: ",excl" означает, что преобразование применится к следующему слову в шаблоне
        :return:
            измененная строка в соответствии с выбранными значениями словаря

        """
        edited_sample = sample
        keys = self.key_pattern.findall(sample)

        # Извлечение ключей для словаря по шаблону
        for key in keys:
            random_word = random.choice(self.dictionary[key])
            edited_sample = edited_sample.replace(key, random_word)

        # Извлечение слов для склонения по шаблону
        words = self.word_pattern.findall(edited_sample)

        case = None
        for stuff in words:
            word_and_case = stuff.split(',')

            word = word_and_case[0]

            if case:
                new_word = self.inflect(word, set(case))
            else:
                new_word = word

            case = word_and_case[1:]
            edited_sample = edited_sample.replace(','.join(case), '')

            if new_word:
                edited_sample = edited_sample.replace(word, new_word)

        edited_sample = edited_sample.replace(',', '')
        edited_sample = edited_sample.replace('|', ' ')
        edited_sample = edited_sample.strip()

        return edited_sample

    def run(self, samples, amount=1, start=None, end=None):

        cmd_list = []
        for sample in samples:
            for i in range(amount):
                example = self.create(sample)
                if start and end:
                    n = random.randint(start, end)
                    example = example.format(n)

                cmd_list.append(example)

        return cmd_list


if __name__ == '__main__':
    project_path = Path(__file__).parents[2]
    dict_path = project_path.joinpath("src/generator/dictionary")
    generator = Generator(dict_path)

