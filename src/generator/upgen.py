import random
import json

from pathlib import Path

from gen import Generator


class SampleGenerator(Generator):

    def __init__(self, dictionary_path: Path):
        super(SampleGenerator, self).__init__(dictionary_path)

    def ner(self, sample: str) -> (str, str):
        """
        Добавление разметки сущностей для шаблонов

        :param sample: шаблон
        :return:
            шаблон для склонений и шаблон для подстановки
        """
        sample_to_inflect = sample
        edited_sample = sample

        keys = self.key_pattern.findall(sample)

        addition = 0
        # print(keys)
        for key in keys:
            random_word = random.choice(self.dictionary[key])

            sample_to_inflect = sample_to_inflect.replace(key, random_word)

            entity, role = key.split(':')

            match entity:
                case "action":
                    random_word = f'[{random_word}]' + str(json.dumps({"entity": entity, "role": role}))
                case "direction":
                    random_word = f'[{random_word}]' + str(json.dumps({"entity": "subject", "role": "direction"}))
                case "object":
                    if addition == 0 and random_word != '_':
                        random_word = f'[{random_word}]' + str(json.dumps({"entity": "subject", "role": "object"}))
                    elif addition > 0 and random_word != '_':
                        random_word = f'[{random_word}]' + str(json.dumps({"entity": "subject", "role": "addition"}))
                    else:
                        random_word = ''
                    addition += 1
                case "relation":
                    random_word = f'[{random_word}]' + str(json.dumps({"entity": entity}))
                case "route":
                    random_word = f'[{random_word}]' + str(json.dumps({"entity": entity, "role": role}))
                case "feature":
                    random_word = f'[{random_word}]' + str(json.dumps({"entity": "relation"}))

            edited_sample = edited_sample.replace(key, random_word)

        return sample_to_inflect, edited_sample

    def generate_action(self, amount: int = 10) -> list:
        """
        Создает намерения для действий над объектами и направлениями

        :param amount: число примеров на один шаблон
        :return:
            список команд
        """
        actions = self.get_keys('action')
        actions.remove("action:patrol")
        actions.remove("action:stop")
        # двигайся, поворачивай и т.д.
        sample = "|prep:robot|{}|"
        samples = [sample.format(act) for act in actions]
        commands = self.run(samples, amount=amount)

        return commands

    def generate_direction(self, amount: int = 10, start: int = 1, end: int = 360) -> list:
        """
        Создает намерения для направлений

        :param amount: количество примеров на один шаблон
        :param start: минимальное значение расстояния
        :param end: максимальное значение расстояния
        :return:
            список команд
        """
        directions = self.get_keys('direction')
        samples = []
        for direct in directions:
            # вперед
            sample = f"|{direct}|"
            samples.append(sample)
            # вперед на 4м
            sample = f"|{direct}|aux:on|$|distance:meter|"
            samples.append(sample)
            # 4м вперед
            sample = f"|$|distance:meter|{direct}|"
            samples.append(sample)
            # направо на 90°
            sample = f"|{direct}|aux:on|$|distance:degree|"
            samples.append(sample)
            # 90° направо
            sample = f"|$|distance:degree|{direct}|"
            samples.append(sample)

        commands = self.run(samples, amount=amount, start=start, end=end)

        return commands

    def generate_action_direction(self, amount: int = 10, start: int = 1, end: int = 360) -> list:
        """
        Создает мульти-намерение для команд с направлением

        :param amount: количество примеров на один шаблон
        :param start: минимальное значение расстояния
        :param end: максимальное значение расстояния
        :return:
            список команд
        """
        directions = self.get_keys('direction')
        samples = []
        for direct in directions:
            # иди вперед
            sample = f"|prep:robot|action:move|{direct}|"
            samples.append(sample)
            # иди вперед 4м
            sample = f"|prep:robot|action:move|{direct}|$|distance:meter|"
            samples.append(sample)
            # иди 10м вперед
            sample = f"|prep:robot|action:move|$|distance:meter|{direct}|"
            samples.append(sample)
            # иди вперед на 10м
            sample = f"|prep:robot|action:move|{direct}|aux:on|$|distance:meter|"
            samples.append(sample)
            # иди на 10м вперед
            sample = f"|prep:robot|action:move|aux:on|$|distance:meter|{direct}|"
            samples.append(sample)

        for direct in directions:
            # поверни направо
            sample = f"|prep:robot|action:rotate|{direct}|"
            samples.append(sample)
            # поверни направо 90°
            sample = f"|prep:robot|action:rotate|{direct}|$|distance:degree|"
            samples.append(sample)
            # поверни 90° направо
            sample = f"|prep:robot|action:rotate|$|distance:degree|{direct}|"
            samples.append(sample)
            # поверни направо на 90°
            sample = f"|prep:robot|action:rotate|{direct}|aux:on|$|distance:degree|"
            samples.append(sample)
            # поверни на 90° направо
            sample = f"|prep:robot|action:rotate|aux:on|$|distance:degree|{direct}|"
            samples.append(sample)

        commands = self.run(samples, amount=amount, start=start, end=end)

        return commands

    def generate_object(self, states: int = 10, amount: int = 10) -> list:
        """
        Создает намерения для объектов

        :param states: перебор объектов
        :param amount: количество примеров на один шаблон
        :return:
            список команд
        """
        objects = self.get_keys('object')
        objects.remove('object:gaze')
        objects.remove('object:void')

        relations = self.get_keys('relation')

        samples = []
        for _ in range(states):
            temp_objects = objects.copy()
            obj1 = random.choice(temp_objects)
            temp_objects.remove(obj1)
            obj2 = random.choice(temp_objects)
            rel1 = random.choice(relations)
            # к дому
            sample = f"|aux:to|{obj1}|"
            samples.append(sample)
            # к дому около дерева
            sample = f"|aux:to|{obj1}|{rel1}|{obj2}|"
            samples.append(sample)
            # около дерева
            sample = f"|object:void|{rel1}|{obj2}|"
            samples.append(sample)
            # дом
            sample = f"|{obj1}|"
            samples.append(sample)
            # дом около дерева
            sample = f"|{obj1}|{rel1}|{obj2}|"
            samples.append(sample)
            # за машиной
            if obj1 == "object:car":
                sample = f"|aux:into|{obj1}|"
                samples.append(sample)
            # к ближайшему дереву
            sample = f"|aux:to|feature:nearest {obj1}|"
            samples.append(sample)
            # к дереву ближайшему
            sample = f"|aux:to|{obj1} feature:nearest|"
            samples.append(sample)
            # # к этому дереву
            sample = f"|aux:to|feature:gaze {obj1}|"
            samples.append(sample)
            # # к дереву этому
            sample = f"|aux:to|{obj1} feature:gaze|"
            samples.append(sample)
            # # туда
            sample = f"|object:gaze|"
            samples.append(sample)

        commands = self.run(samples, amount=amount)

        return commands

    def generate_action_object(self, states: int = 10, amount: int = 10) -> list:
        """
        Создает мульти-намерение для команд с объектами

        :param states: перебор объектов
        :param amount: количество примеров на один шаблон
        :return:
            список команд
        """
        actions = self.get_keys('action')
        actions.remove('action:follow')
        actions.remove('action:patrol')
        actions.remove('action:stop')

        objects = self.get_keys('object')
        objects.remove('object:gaze')
        objects.remove('object:void')

        relations = self.get_keys('relation')

        samples = []
        for action in actions:
            for _ in range(states):
                temp_objects = objects.copy()
                obj1 = random.choice(temp_objects)
                temp_objects.remove(obj1)
                obj2 = random.choice(temp_objects)
                rel1 = random.choice(relations)

                match action:
                    case "action:move" | "action:rotate":
                        # иди к дому
                        sample = f"|prep:robot|{action}|aux:to|{obj1}|"
                        samples.append(sample)
                        # иди к дому около дерева
                        sample = f"|prep:robot|{action}|aux:to|{obj1}|{rel1}|{obj2}|"
                        samples.append(sample)
                    case "action:follow":
                        if obj1 == "object:car":
                            # следуй за машиной
                            sample = f"|prep:robot|{action}|aux:into|{obj1}|"
                            samples.append(sample)
                    case _:
                        # анализируй дом
                        sample = f"|prep:robot|{action}|{obj1}|"
                        samples.append(sample)
                        # анализируй дом около дерева
                        sample = f"|prep:robot|{action}|{obj1}|{rel1}|{obj2}|"
                        samples.append(sample)

        commands = self.run(samples, amount=amount)

        return commands

    def generate_patrol(self, amount: int = 10) -> list:
        samples = [
            # патрулируй
            "|prep:robot|action:patrol|"
        ]

        commands = self.run(samples, amount=amount)

        return commands

    def generate_route(self, amount: int = 10, start: int = 1, end: int = 10) -> list:
        """
        Создает намерения для типа маршрута патрулирования

        :param amount: количество примеров на один шаблон
        :param start: минимальный номер/радиус
        :param end: максимальный номер/радиус
        :return:
            список команд
        """
        samples = [
            # по кругу радиуса 4м
            "|aux:by|route:circle|aux:radius|$|distance:meter|",
            # по кругу 4м
            "|aux:by|route:circle|$|distance:meter|",
            # по маршруту номер 2
            "|aux:by|route:path|aux:number|$|",
            # по 2 маршруту
            "|aux:by|$|route:path|"
        ]

        commands = self.run(samples, amount=amount, start=start, end=end)

        return commands

    def generate_patrol_route(self, amount: int = 10, start: int = 1, end: int = 10) -> list:
        """
        Создает намерения для команд с маршрутом патрулирования

        :param amount: количество примеров на один шаблон
        :param start: минимальный номер/радиус
        :param end: максимальный номер/радиус
        :return:
            список команд
        """
        samples = [
            # патрулируй по кругу радиуса 4м
            "|prep:robot|action:patrol|aux:by|route:circle|aux:radius|$|distance:meter|",
            # патрулируй по кругу 4м
            "|prep:robot|action:patrol|aux:by|route:circle|$|distance:meter|",
            # патрулируй по маршруту номер 2
            "|prep:robot|action:patrol|aux:by|route:path|aux:number|$|",
            # патрулируй по 2 маршруту
            "|prep:robot|action:patrol|aux:by|$|route:path|"
        ]

        commands = self.run(samples, amount=amount, start=start, end=end)

        return commands

    def generate_simple_action(self, amount: int = 10) -> list:
        """
        Создает намерения для команд без атрибутов

        :param amount: количество примеров на один шаблон
        :return:
            список команд
        """
        samples = [
            # стой
            '|prep:robot|action:stop|'
        ]

        commands = self.run(samples, amount=amount)

        return commands
