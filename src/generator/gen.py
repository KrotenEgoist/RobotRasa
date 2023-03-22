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

    @staticmethod
    def _gen(func):
        def wrapper(*args, **kwargs):
            cmd_list = []
            for sample in kwargs['samples']:
                for i in range(kwargs['amount']):
                    example = func(*args, sample, **kwargs)
                    cmd_list.append(example)

            return cmd_list

        return wrapper

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

    def inflect(self, word: str, grammes: set):
        """
        Преобразует слово в соответствии с граммемами (http://opencorpora.org/dict.php?act=gram)

        :param word: слово в нормальной форме, пример: "идти"
        :param grammes: множество граммем, пример: {'excl'}
        :return:
            Измененное слово: "идти", {'excl'} -> "иди"
        """
        morphed = self.morph.parse(word)[0]
        inflected = morphed.inflect(grammes)
        new_word = inflected.word

        return new_word

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
        keys = self.key_pattern.findall(sample)

        case = None
        words_dict = {}
        for key in keys:
            words = random.choice(self.dictionary[key]).split('|')

            if case:
                try:
                    word = self.inflect(words[0], case)
                except AttributeError:
                    word = words[0]
            else:
                word = words[0]

            if len(words) > 1:
                case = set(words[1:])
            else:
                case = None

            words_dict[key] = word

        for key, value in words_dict.items():
            sample = sample.replace(key, value)

        return sample.strip()

    @_gen
    def commands_with_numbers(self, sample, **kwargs):
        example = self.create(sample)
        n = random.randint(kwargs['start'], kwargs['end'])
        example = example.format(n)

        return example

    @_gen
    def commands_without_numbers(self, sample, **kwargs):
        example = self.create(sample)

        return example


if __name__ == '__main__':
    project_path = Path(__file__).parents[2]
    dict_path = project_path.joinpath("src/generator/dictionary")
    generator = Generator(dict_path)

    # patrols = [
    #     "prep:robot action:patrol",
    #     "prep:robot action:patrol aux:by object:circle {} distance:meter",
    #     "prep:robot action:patrol aux:by object:circle aux:radius {} distance:meter",
    #     "prep:robot action:patrol aux:by object:route {}",
    #     "prep:robot action:patrol aux:by {} object:route",
    #     "prep:robot action:patrol aux:by object:route aux:number {}",
    # ]
    # action_patrol = generator.commands_with_numbers(samples=patrols, amount=10, start=1, end=10)
    # for act in action_patrol:
    #     print(act)
    #
    # stops = [
    #     "prep:robot action:stop",
    # ]
    # action_stop = generator.commands_without(samples=stops, amount=10)
    # for act in action_stop:
    #     print(act)
    #
    # directions = [
    #     "prep:robot action:move direction:forward {} distance:meter",
    #     "prep:robot action:move {} distance:meter direction:forward"
    # ]
    # action_move_direction = generator.commands_with_numbers(samples=directions, amount=10, start=1, end=50)
    # for act in action_move_direction:
    #     print(act)

    samples = [
        "prep:robot action:move aux:to object:tree relation:behind object:human",
        "prep:robot action:around object:human",
        "prep:robot action:move aux:to feature:nearest object:human"
    ]

    actions = generator.commands_without_numbers(samples=samples, amount=100)

    for act in actions:
        print(act)
