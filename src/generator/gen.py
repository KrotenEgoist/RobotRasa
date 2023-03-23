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
        self.word_pattern = re.compile(r'([\w\s,]+)')

    def generate_patrol(self, amount: int = 10, start: int = 1, end: int = 10) -> dict:
        """
        Создает команды патрулирования

        :param amount: количество примеров на один шаблон
        :param start: начальное случайное число
        :param end: конечное случайное число
        :return:
            Список команд патрулирования
        """
        samples = [
            # патрулируй
            "|prep:robot|action:patrol|",
            # патрулируй по кругу 10 м
            "|prep:robot|action:patrol|aux:by|object:circle|{}|distance:meter|",
            # патрулируй по кругу радиуса 10 м
            "|prep:robot|action:patrol|aux:by|object:circle|aux:radius|{}|distance:meter|",
            # патрулируй по маршруту 1
            "|prep:robot|action:patrol|aux:by|object:route|{}|",
            # патрулируй по маршруту номер 1
            "|prep:robot|action:patrol|aux:by|object:route|aux:number|{}|",
            # патрулируй по 1 маршруту
            "|prep:robot|action:patrol|aux:by|{}|object:route|",
        ]

        commands = self.run(samples, amount=amount, start=start, end=end)

        return {"patrol": commands}

    def generate_stop(self, amount: int = 10) -> dict:
        """
        Создает команды остановки

        :param amount: количество примеров на один шаблон
        :return:
            Список команд остановки
        """
        samples = [
            # остановись
            "|prep:robot|action:stop|"
        ]

        commands = self.run(samples, amount=amount)

        return {"stop": commands}

    def generate_move_dir(self, amount: int = 10, start: int = 1, end: int = 50) -> dict:
        """
        Создает команды движения в направлении

        Используется автоматическая подстановка направлений

        :param amount: количество примеров на один шаблон
        :param start: начальное случайное число
        :param end: конечное случайное число
        :return:
            Список команд движения в направлении
        """
        directions_path = list(self.dictionary_path.glob('**/direction/*'))
        directions = list(map(lambda x: ':'.join(x.parts[-2:]), directions_path))

        samples = []
        for direct in directions:
            # иди вперед
            sample1 = f"|prep:robot|action:move|{direct}|"
            samples.append(sample1)

            # иди вперед 10 м
            sample2 = f"|prep:robot|action:move|{direct}|" + "{}|distance:meter|"
            samples.append(sample2)

            # иди 10 м вперед
            sample3 = "|prep:robot|action:move|{}|distance:meter|" + f"{direct}|"
            samples.append(sample3)

        commands = self.run(samples, amount=amount, start=start, end=end)

        return {"move_dir": commands}

    def generate_rotate_dir(self, amount: int = 10, start: int = 1, end: int = 360) -> dict:
        """
        Создает команды поворота в направлении

        Используется автоматическая подстановка направлений

        :param amount: количество примеров на один шаблон
        :param start: начальное случайное число
        :param end: конечное случайное число
        :return:
            Список команд поворота в направлении
        """
        directions_path = list(self.dictionary_path.glob('**/direction/*'))
        directions = list(map(lambda x: ':'.join(x.parts[-2:]), directions_path))

        samples = []
        for direct in directions:
            # поворачивай направо
            sample1 = f"|prep:robot|action:rotate|{direct}|"
            samples.append(sample1)

            # поворачивай направо 90 °
            sample2 = f"|prep:robot|action:rotate|{direct}|" + "{}|distance:degree|"
            samples.append(sample2)

            # поворачивай 90 ° направо
            sample3 = "|prep:robot|action:rotate|{}|distance:degree|" + f"{direct}|"
            samples.append(sample3)

        commands = self.run(samples, amount=amount, start=start, end=end)

        return {"rotate_dir": commands}

    def generate_follow(self, amount=10):
        """
        Создает команды следования

        :param amount: количество примеров на один шаблон
        :return:
            Список команд следования
        """
        samples = [
            "|prep:robot|action:follow|aux:into|object:car|"
        ]

        commands = self.run(samples, amount=amount)

        return {"follow": commands}

    def generate_objects(self, states: int = 10, amount: int = 10):
        """
        Создает команды движения/поиска/анализа/осмотра/объезда/поворота к объектам

        Используются случайный выбор объектов и отношений между ними

        :param states: количество переборов объектов и отношений
        :param amount: количество примеров на один шаблон
        :return:
            Список команд движения к объектам
        """
        objects_path = list(self.dictionary_path.glob('**/object/*'))
        objects = list(map(lambda x: ':'.join(x.parts[-2:]), objects_path))
        objects.remove('object:circle')
        objects.remove('object:route')
        objects.remove('object:gaze')

        relations_path = list(self.dictionary_path.glob('**/relation/*'))
        relations = list(map(lambda x: ':'.join(x.parts[-2:]), relations_path))

        commands = {}
        for action in ["action:move",
                       "action:analyze",
                       "action:find",
                       "action:around",
                       "action:monitor",
                       "action:rotate"]:

            samples = []
            for _ in range(states):
                obj1 = random.choice(objects)

                if action in ["action:move", "action:rotate"]:
                    # иди/повернись к дому
                    sample = f"|prep:robot|{action}|aux:to|{obj1}|"
                else:
                    # найди/обойди/осмотри/анализируй дом
                    sample = f"|prep:robot|{action}|{obj1}|"

                samples.append(sample)

            for _ in range(states):
                temp_objects = objects.copy()
                obj1 = random.choice(temp_objects)
                temp_objects.remove(obj1)
                obj2 = random.choice(temp_objects)
                rel1 = random.choice(relations)

                if action in ["action:move", "action:rotate"]:
                    # иди к дому около дерева
                    sample = f"|prep:robot|{action}|aux:to|{obj1}|{rel1}|{obj2}|"
                else:
                    # найди/обойди/осмотри/анализируй дом около дерева
                    sample = f"|prep:robot|{action}|{obj1}|{rel1}|{obj2}|"

                samples.append(sample)

            for _ in range(states):
                obj1 = random.choice(objects)

                if action in ["action:move", "action:rotate"]:
                    # иди к ближайшему дому
                    sample = f"|prep:robot|{action}|aux:to|feature:nearest {obj1}|"
                else:
                    # найди/обойди/осмотри/анализируй ближайший дому
                    sample = f"|prep:robot|{action}|feature:nearest {obj1}|"
                samples.append(sample)

            for _ in range(states):
                temp_objects = objects.copy()
                obj1 = random.choice(temp_objects)
                temp_objects.remove(obj1)
                obj2 = random.choice(temp_objects)
                temp_objects.remove(obj2)
                obj3 = random.choice(temp_objects)
                rel1 = random.choice(relations)
                rel2 = random.choice(relations)

                if action in ["action:move", "action:rotate"]:
                    # иди к дому около дерева рядом с камнем
                    sample = f"|prep:robot|{action}|aux:to|{obj1}|{rel1}|{obj2}|{rel2}|{obj3}|"
                else:
                    # найди/обойди/осмотри/анализируй дом около дерева рядом с камнем
                    sample = f"|prep:robot|{action}|{obj1}|{rel1}|{obj2}|{rel2}|{obj3}|"
                samples.append(sample)

            for _ in range(states):
                obj1 = random.choice(objects)

                if action in ["action:move", "action:rotate"]:
                    # иди к этому дому
                    sample = f"|prep:robot|{action}|aux:to|feature:gaze {obj1}|"
                else:
                    # найди/обойди/осмотри/анализируй этот дом
                    sample = f"|prep:robot|{action}|feature:gaze {obj1}|"

                samples.append(sample)

            temp_relations = relations.copy()
            temp_relations.remove('relation:near')
            for _ in range(states):
                obj1 = random.choice(objects)
                rel1 = random.choice(temp_relations)

                if action in ["action:move", "action:rotate"]:
                    # иди к дому левее себя
                    sample = f"|prep:robot|{action}|aux:to|{obj1}|{rel1}|aux:self|"
                else:
                    # найди/обойди/осмотри/анализируй дом левее себя
                    sample = f"|prep:robot|{action}|{obj1}|{rel1}|aux:self|"

                samples.append(sample)

            if action in ["action:move", "action:rotate"]:
                # иди туда
                sample = f"|prep:robot|{action}|object:gaze|"
                samples.append(sample)

            commands[action.split(':')[-1]] = self.run(samples=samples, amount=amount)

        return commands

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

    def create(self, sample: str) -> str:
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
        # Шаблон для склонений
        sample_to_inflect = sample
        # Общий шаблон с выделением сущностей
        edited_sample = sample
        keys = self.key_pattern.findall(sample)

        # Извлечение ключей для словаря по шаблону
        for key in keys:
            random_word = random.choice(self.dictionary[key])

            sample_to_inflect = sample_to_inflect.replace(key, random_word)

            # Выделение сущностей
            if "object" in key:
                random_word = f"[{random_word}](object)"
            elif "direction" in key:
                random_word = f"[{random_word}](direction)"
            elif "relation" in key:
                random_word = f"[{random_word}](relation)"
            elif "nearest" in key:
                random_word = f"[{random_word}](nearest)"
            elif "feature:gaze" in key:
                random_word = f"[{random_word}](nearest)"

            edited_sample = edited_sample.replace(key, random_word)

        # Извлечение слов для склонения по шаблону
        words = self.word_pattern.findall(sample_to_inflect)

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
                # Корректная замена слов в шаблоне с учетом сущностей
                for new, old in zip(new_word.split(" "), word.split(" ")):
                    edited_sample = edited_sample.replace(old, new)

        edited_sample = edited_sample.replace(',', '')
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
                    example = example.format(n)

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
