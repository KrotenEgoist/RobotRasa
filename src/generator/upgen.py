import random

from pathlib import Path

from gen import Generator


class SampleGenerator(Generator):

    def __init__(self, dictionary_path: Path):
        super(SampleGenerator, self).__init__(dictionary_path)

    def ner(self, sample):
        """
        Добавление разметки сущностей для шаблонов

        :param sample: шаблон
        :return:
            шаблон для склонений и шаблон для подстановки
        """
        sample_to_inflect = sample
        edited_sample = sample

        keys = self.key_pattern.findall(sample)

        # Извлечение ключей для словаря по шаблону
        addition_object = 0
        for key in keys:
            random_word = random.choice(self.dictionary[key])

            sample_to_inflect = sample_to_inflect.replace(key, random_word)

            # Выделение сущностей
            if "action" in key:
                random_word = f'[{random_word}]' + '{"entity": "action"}'
            elif "object" in key and addition_object > 0:
                random_word = f'[{random_word}]' + '{"entity": "subject", "role": "addition"}'
            elif "object" in key and addition_object == 0:
                if random_word == '_':
                    random_word = ''
                else:
                    random_word = f'[{random_word}]' + '{"entity": "subject", "role": "object"}'
                addition_object += 1
            elif "direction" in key:
                random_word = f'[{random_word}]' + '{"entity": "subject", "role": "direction"}'
            elif "relation" in key:
                random_word = f'[{random_word}]' + '{"entity": "relation"}'
            # elif "nearest" in key:
            #     random_word = f"[{random_word}](nearest)"
            # elif "feature:gaze" in key:
            #     random_word = f"[{random_word}](gaze)"

            edited_sample = edited_sample.replace(key, random_word)

        return sample_to_inflect, edited_sample

    def generate_move_dir(self, amount: int = 10, start: int = 1, end: int = 50) -> list:
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
            # вперед
            sample = f"|{direct}|"
            samples.append(sample)
            # вперед на 4м
            sample = f"|{direct}|" + "aux:on|$|distance:meter|"
            samples.append(sample)
            # иди вперед
            sample1 = f"|prep:robot|action:move|{direct}|"
            samples.append(sample1)
            # иди вперед 10 м
            sample2 = f"|prep:robot|action:move|{direct}|" + "$|distance:meter|"
            samples.append(sample2)
            # иди 10 м вперед
            sample3 = "|prep:robot|action:move|$|distance:meter|" + f"{direct}|"
            samples.append(sample3)
            # иди вперед на 10 м
            sample4 = f"|prep:robot|action:move|{direct}|aux:on|" + "$|distance:meter|"
            samples.append(sample4)
            # иди на 10 м вперед
            sample5 = "|prep:robot|action:move|aux:on|$|distance:meter|" + f"{direct}|"
            samples.append(sample5)

        commands = self.run(samples, amount=amount, start=start, end=end)

        return commands

    def generate_rotate_dir(self, amount: int = 10, start: int = 1, end: int = 360) -> list:
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
            # направо
            sample = f"|{direct}|"
            samples.append(sample)
            # направо на 90 °
            sample = f"|{direct}|" + "$|distance:degree|"
            # поворачивай направо
            sample1 = f"|prep:robot|action:rotate|{direct}|"
            samples.append(sample1)
            # поворачивай направо 90 °
            sample2 = f"|prep:robot|action:rotate|{direct}|" + "$|distance:degree|"
            samples.append(sample2)
            # поворачивай 90 ° направо
            sample3 = "|prep:robot|action:rotate|$|distance:degree|" + f"{direct}|"
            samples.append(sample3)
            # поворачивай направо на 90 °
            sample4 = f"|prep:robot|action:rotate|{direct}|aux:on|" + "$|distance:degree|"
            samples.append(sample4)
            # поворачивай на 90 ° направо
            sample5 = "|prep:robot|action:rotate|aux:on|$|distance:degree|" + f"{direct}|"
            samples.append(sample5)

        commands = self.run(samples, amount=amount, start=start, end=end)

        return commands

    def generate_move_to(self, states: int = 10, amount: int = 10):
        """
        Создает команды движения/поворота к объектам

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
        objects.remove('object:void')

        relations_path = list(self.dictionary_path.glob('**/relation/*'))
        relations = list(map(lambda x: ':'.join(x.parts[-2:]), relations_path))

        samples = []
        commands = []
        for _ in range(states):
            temp_objects = objects.copy()
            obj1 = random.choice(temp_objects)
            temp_objects.remove(obj1)
            obj2 = random.choice(temp_objects)
            rel1 = random.choice(relations)
            # иди к дому
            sample = f"|prep:robot|action:move|aux:to|{obj1}|"
            samples.append(sample)
            # поверни к дому
            sample = f"|prep:robot|action:rotate|aux:to|{obj1}|"
            samples.append(sample)
            # к дому
            sample = f"|aux:to|{obj1}|"
            samples.append(sample)
            # иди к дому около дерева
            sample = f"|prep:robot|action:move|aux:to|{obj1}|{rel1}|{obj2}|"
            samples.append(sample)
            # поверни к дому около дерева
            sample = f"|prep:robot|action:move|aux:to|{obj1}|{rel1}|{obj2}|"
            samples.append(sample)
            # около дерева
            sample = f"|object:void|{rel1}|{obj2}|"
            samples.append(sample)

        commands.extend(self.run(samples=samples, amount=amount))

        return commands

    def generate_objects(self, states: int = 10, amount: int = 10) -> list:
        """
        Создает команды поиска/анализа/осмотра/объезда объектов

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
        objects.remove('object:void')

        relations_path = list(self.dictionary_path.glob('**/relation/*'))
        relations = list(map(lambda x: ':'.join(x.parts[-2:]), relations_path))

        commands = []
        for action in ["action:analyze",
                       "action:find",
                       "action:around",
                       "action:monitor"]:

            samples = []
            for _ in range(states):
                temp_objects = objects.copy()
                obj1 = random.choice(temp_objects)
                temp_objects.remove(obj1)
                obj2 = random.choice(temp_objects)
                rel1 = random.choice(relations)
                # анализируй дом
                sample = f"|prep:robot|{action}|aux:to|{obj1}|"
                samples.append(sample)
                # к дому
                sample = f"|aux:to|{obj1}|"
                samples.append(sample)
                # анализируй дом около дерева
                sample = f"|prep:robot|{action}|aux:to|{obj1}|{rel1}|{obj2}|"
                samples.append(sample)
                # около дерева
                sample = f"|object:void|{rel1}|{obj2}|"
                samples.append(sample)

            commands.extend(self.run(samples=samples, amount=amount))

        return commands


    # @staticmethod
    # def generate_fallback(amount: int = 100,
    #                       range_eng: list | tuple = (0, 10),
    #                       range_rus: list | tuple = (0, 10),
    #                       range_dig: list | tuple = (0, 10),
    #                       range_spc: list | tuple = (0, 10)) -> list:
    #     """
    #     Создает некорректный ввод
    #
    #     :param amount: количество примеров
    #     :param range_eng: количество английских букв
    #     :param range_rus: количество русских букв
    #     :param range_dig: количество цифр
    #     :param range_spc: количество пробелов
    #     :return:
    #
    #     """
    #     en_letters = string.ascii_letters
    #     ru_letters = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    #     digits = string.digits
    #
    #     commands = []
    #     for _ in range(amount):
    #         eng = [random.choice(en_letters) for _ in range(random.randint(*range_eng))]
    #         rus = [random.choice(ru_letters) for _ in range(random.randint(*range_rus))]
    #         dig = [random.choice(digits) for _ in range(random.randint(*range_dig))]
    #         spaces = [random.choice(["", " "]) for _ in range(random.randint(*range_spc))]
    #
    #         inp = eng + rus + dig + spaces
    #         random.shuffle(inp)
    #
    #         inp_string = ''.join(inp)
    #         commands.append(inp_string)
    #
    #     return commands
    #
    # def generate_action(self, action_type: str = "action:move", amount: int = 10) -> list:
    #     """
    #     Создает команды без атрибутов для уточнения
    #
    #     :param action_type: тип действия
    #     :param amount: количество примеров на шаблон
    #     :return:
    #     """
    #     actions_blacklist = ["action:stop", "action:patrol", "action:follow"]
    #     actions_path = list(self.dictionary_path.glob('**/action/*'))
    #     actions = list(map(lambda x: ':'.join(x.parts[-2:]), actions_path))
    #     for ignore in actions_blacklist:
    #         actions.remove(ignore)
    #
    #     samples = []
    #     sample = f"|prep:robot|{action_type}|"
    #     samples.append(sample)
    #
    #     commands = self.run(samples, amount=amount)
    #
    #     return commands
    #
    # def generate_wrong(self, amount: int = 10) -> list:
    #     """
    #     Создает запросы на исправление команды
    #
    #     :param amount: количество примеров на один шаблон
    #     :return:
    #         Список запросов
    #     """
    #     samples = [
    #         # исправь команду
    #         "|prep:robot|wrong:fix|wrong:mistake|"
    #     ]
    #
    #     commands = self.run(samples, amount=amount)
    #
    #     return commands
    #
    # def generate_patrol(self, amount: int = 10, start: int = 1, end: int = 10) -> list:
    #     """
    #     Создает команды патрулирования
    #
    #     :param amount: количество примеров на один шаблон
    #     :param start: начальное случайное число
    #     :param end: конечное случайное число
    #     :return:
    #         Список команд патрулирования
    #     """
    #     samples = [
    #         # патрулируй
    #         "|prep:robot|action:patrol|",
    #         # патрулируй по кругу 10 м
    #         "|prep:robot|action:patrol|aux:by|object:circle|{}|distance:meter|",
    #         # патрулируй по кругу радиуса 10 м
    #         "|prep:robot|action:patrol|aux:by|object:circle|aux:radius|{}|distance:meter|",
    #         # патрулируй по маршруту 1
    #         "|prep:robot|action:patrol|aux:by|object:route|{}|",
    #         # патрулируй по маршруту номер 1
    #         "|prep:robot|action:patrol|aux:by|object:route|aux:number|{}|",
    #         # патрулируй по 1 маршруту
    #         "|prep:robot|action:patrol|aux:by|{}|object:route|",
    #     ]
    #
    #     commands = self.run(samples, amount=amount, start=start, end=end)
    #
    #     return commands
    #
    # def generate_stop(self, amount: int = 10) -> list:
    #     """
    #     Создает команды остановки
    #
    #     :param amount: количество примеров на один шаблон
    #     :return:
    #         Список команд остановки
    #     """
    #     samples = [
    #         # остановись
    #         "|prep:robot|action:stop|"
    #     ]
    #
    #     commands = self.run(samples, amount=amount)
    #
    #     return commands
    #
    # def generate_follow(self, amount=10) -> list:
    #     """
    #     Создает команды следования за машиной
    #
    #     :param amount: количество примеров на один шаблон
    #     :return:
    #         Список команд следования
    #     """
    #     samples = [
    #         # следуй за машиной
    #         "|prep:robot|action:follow|aux:into|object:car|"
    #     ]
    #
    #     commands = self.run(samples, amount=amount)
    #
    #     return commands