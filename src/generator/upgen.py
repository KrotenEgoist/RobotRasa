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
                    else:
                        random_word = ''
                    if addition > 0:
                        random_word = f'[{random_word}]' + str(json.dumps({"entity": "subject", "role": "addition"}))
                    addition += 1
                case "relation":
                    random_word = f'[{random_word}]' + str(json.dumps({"entity": entity}))

            edited_sample = edited_sample.replace(key, random_word)

        return sample_to_inflect, edited_sample

    def generate_action(self, amount: int = 10) -> list:
        """


        :param amount:
        :return:
        """
        actions = self.get_keys('action')
        # двигайся, поворачивай и т.д.
        sample = "|prep:robot|{}|"
        samples = [sample.format(act) for act in actions]
        commands = self.run(samples, amount=amount)

        return commands

    def generate_direction(self, amount: int = 10, start: int = 1, end: int = 50) -> list:
        """


        :param amount:
        :param start:
        :param end:
        :return:
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

        commands = self.run(samples, amount=amount, start=start, end=end)

        return commands

    def generate_action_direction(self, amount: int = 10, start: int = 1, end: int = 50) -> list:
        """


        :param amount:
        :param start:
        :param end:
        :return:
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

        commands = self.run(samples, amount=amount, start=start, end=end)

        return commands

    def generate_object(self, states: int = 10, amount: int = 10) -> list:
        """


        :param states:
        :param amount:
        :return:
        """
        objects = self.get_keys('object')
        objects.remove('object:circle')
        objects.remove('object:route')
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

        commands = self.run(samples, amount=amount)

        return commands

    def generate_action_object(self, states: int = 10, amount: int = 10) -> list:
        objects = self.get_keys('object')
        objects.remove('object:circle')
        objects.remove('object:route')
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
            # иди к дому
            sample = f"|prep:robot|action:move|aux:to|{obj1}|"
            samples.append(sample)
            # иди к дому около дерева
            sample = f"|prep:robot|action:move|aux:to|{obj1}|{rel1}|{obj2}|"
            samples.append(sample)

        commands = self.run(samples, amount=amount)

        return commands
