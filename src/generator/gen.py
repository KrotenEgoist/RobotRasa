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

    def create_dictionary(self) -> dict:
        """
        Создает словарь из директории dictionary
        Ключ - путь до файла со словами, пример action/move, object/house
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

    def inflect(self, words: list, grammes: set):
        """
        Преобразует слово в соответствии с граммемами (http://opencorpora.org/dict.php?act=gram)

        :param word: слово в нормальной форме, пример: "идти"
        :param grammes: множество граммем, пример: {'excl'}
        :return:
            Измененное слово: "идти", {'excl'} -> "иди"
        """
        morphed = []
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
                "prep:robot": ["|excl", "|plur"],
                "action:patrol" ["патрулировать", "разведывать", "охранять"],
                ...
            }

            P.S.: для работы преобразования слов, необходимо указывать в файлах словаря требуемые граммемы,
            пример для файла prep/robot: "|excl" означает, что преобразование применится к следующему слову в шаблоне
        :return:
            измененная строка в соответствии с выбранными значениями словаря

        """
        # keys = self.key_pattern.findall(sample)

        keys = list(map(lambda x: x.split('-'), sample.split(" ")))

        case = None
        cmd = []
        for subkey in keys:
            words = None
            inflected = []
            for key in subkey:
                words = random.choice(self.dictionary[key]).split('|')

                if case:
                    word = self.inflect([words[0]], case)
                else:
                    word = words[0]

                inflected.append(word)

            if len(inflected) > 1:
                idx = list(map(lambda x: self.morph.parse(x)[0].tag.POS, inflected)).index('NOUN')
                gender = self.morph.parse(inflected[idx])[0].tag.gender
                animacy = self.morph.parse(inflected[idx])[0].tag.animacy

                inflected = self.inflect(inflected, {gender})
            else:
                inflected = inflected[0]

            if len(words) > 1:
                case = set(words[1:])
            else:
                case = None

            if inflected:
                cmd.append(inflected)

        return ' '.join(cmd)

    def run(self, samples, amount=10, start=None, end=None):

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

    exmp = [
        # "prep:robot action:patrol",
        # "prep:robot action:stop",
        # "prep:robot action:move direction:forward",
        # "prep:robot action:rotate direction:right",
        # "prep:robot action:move aux:to object:tree",
        # "prep:robot action:move aux:to feature:nearest-object:tree",
        # "prep:robot action:rotate aux:to object:house",
        # "prep:robot action:find object:tree",
        # "prep:robot action:around object:rock",
        # "prep:robot action:monitor object:car",
        # "prep:robot action:analyze object:tree",
        "prep:robot action:follow aux:into object:car"
    ]

    actions = generator.run(samples=exmp)
    for act in actions:
        print(act)

