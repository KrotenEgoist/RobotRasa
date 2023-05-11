import requests
import socket
import numpy as np

from pathlib import Path

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, SlotSet, ActiveLoop, SessionStarted, ActionExecuted

from src.db.psql_control_db import PostgresqlControl


db = PostgresqlControl(user='root', password='root')
cmd_list = []

# from src.db.sqlite_control_db import ControlDB


# project_path = Path(__file__).parents[2]
# db_path = project_path.joinpath("database/rasa.db")
# database = ControlDB(db_path)


def text_to_vector(text: str) -> dict:
    """
    Отправляет POST запрос на сервис преобразования текствой команды в вектор атрибутов
    url записан в конфиге ~/arctic_build/robots_HRI/CONFIG/config.conf:text_to_rdf

    Args:
        text (str): текстовая команда
    Returns:
        vector: Словарь с ключем 'parse_result', содержащий список с количеством распознанных команд
                каждая команда содержит набор атрибутов и вероятности разбора

                Пример: "иди вперед 1 м"
                {
                    'parse_result': [
                        [
                            ['action', 'move_on', 0.9999855756759644],
                            ['direction', 'dir_forward', 0.9999639987945557],
                            ['meters', '1', 0.9999811053276062]
                        ]
                    ]
                }
    """
    # try:
    response = requests.post("http://192.168.1.34:8892/classify_phrases", json={'commands': text})
    # except requests.exceptions.ConnectionError:
        # sys.stderr.write('Парсер команд недоступен')
        # sys.stderr.flush()
        # return {}

    # try:
    vector = response.json()
    # except requests.exceptions.JSONDecodeError:
    #     sys.stderr.write('Ошибка в формировании ответа от парсера (нет текста команды)')
    #     sys.stderr.flush()
    #     vector = {}

    return vector


def vector_to_rdf(vector: dict) -> str:
    """
    Отправляет POST запрос на сервис преобразования вектора атрибутов в RDF формат
    url записан в конфиге ~/arctic_build/robots_HRI/CONFIG/config.conf:cmd_processing

    Args:
        vector (dict): вектор атрибутов в виде возвращаемого значения text_to_vector()
    Returns:
        rdf: RDF формат команды
    """
    # try:
    response = requests.post("http://localhost:6355/nn_to_rdf", json=vector)
    # except requests.exceptions.ConnectionError:
    #     sys.stderr.write('Обработчик команд недоступен')
    #     sys.stderr.flush()
    #     return ''

    rdf = response.text

    return rdf


def send_to_robot(rdf: str) -> None:
    """
    Отправляет POST запрос на сервис обработки RDF команд
    url записан в конфиге ~/arctic_build/robots_HRI/CONFIG/config.conf:rdf
    """
    # try:
    response = requests.post("http://192.168.1.36:8001/", rdf)
    # except requests.exceptions.ConnectionError:
    #     sys.stderr.write('Нет связи с роботом')
    #     sys.stderr.flush()


def receive_data(host: str, port: int) -> bytes:
    """
    Получение данных из основного окна интерфейса через сокет

    Args:
        host (str): хост
        port (int): порт
    Returns:
        байты с данными
    """
    with socket.socket() as s:
        s.connect((host, port))

        return s.recv(512)


def rdf_gaze_data(gaze: bytes) -> str:
    """
    Преобразование направления взгляда из пикселей в 3D вектор относительно центра изображения с камеры робота

    Args:
        gaze (bytes): координаты взгляда в пикселях на экране монитора в байтах
    Returns:
        rdf_gaze: RDF формат, описывающий 3D вектор направления взгляда
    """
    str_gaze = gaze.decode()
    str_x, str_y = str_gaze.split(' ')
    x, y = int(str_x), int(str_y)

    if x <= 1300 and y <= 980:
        theta = np.arctan((2 * x - 1280) / 1280 * np.tan(80 / 2))
        phi = np.arctan((2 * y - 960) / 960 * np.tan(64 / 2))

        length = np.sqrt(1 + np.sin(theta)**2 + np.sin(phi)**2)

        dec_x = 1
        dec_y = 1 / length * np.sin(theta)
        dec_z = -1 / length * np.sin(phi)

        rdf_gaze = f'<ki:eyes> <rdf:type> <ki:gaze_data> .\n' \
                   f'<ki:eyes> <ki:x> "{dec_x}" .\n' \
                   f'<ki:eyes> <ki:y> "{dec_y}" .\n' \
                   f'<ki:eyes> <ki:z> "{dec_z}" .\n\n'

        return rdf_gaze


class ActionSessionStart(Action):
    """
    Действие выполняется при запуске новой сессии,
    либо при отправке сообщения /session_start
    """
    def name(self):
        return "action_session_start"

    async def run(
      self, dispatcher, tracker: Tracker, domain
    ):

        dispatcher.utter_message(text="Назовите команду для отправки роботу")

        return [SessionStarted(), ActionExecuted("action_listen")]


class AskSubjectAction(Action):

    def name(self):
        return "action_ask_subject"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain,
    ):
        entities = tracker.latest_message["entities"]
        for entity in entities:
            if entity["entity"] == "action":
                role = entity["role"]

        match role:
            case "move" | "rotate":
                dispatcher.utter_message(text="Укажите объект или направление")
            case "analyze" | "around" | "find" | "monitor" | "follow":
                dispatcher.utter_message(text="Укажите объект")

        return []


class AskFeatureAction(Action):

    def name(self):
        return "action_ask_feature"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain,
    ):
        if tracker.slots["relation"] or tracker.slots["distance"]:
            return [ActiveLoop(None), SlotSet("feature", tracker.latest_message["text"])]

        entities = tracker.latest_message["entities"]
        for entity in entities:
            if entity["entity"] == "subject":
                role = entity["role"]

        match role:
            case "object":
                dispatcher.utter_message(response="utter_ask_relation")
            case "direction":
                dispatcher.utter_message(response="utter_ask_distance")

        return []


class ActionResetSlots(Action):

    def name(self):
        return "action_reset_slots"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain,
    ):

        return [
            AllSlotsReset()
        ]


class ActionSendCommand(Action):

    def name(self):
        return "action_send_command"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain,
    ):
        parsed_slots = {}
        for key, value in tracker.slots.items():
            if value:
                parsed_slots[key] = value

        for key in ['feature', 'requested_slot']:
            parsed_slots.pop(key, None)

        if "relation" and "addition" in parsed_slots.keys():
            relation_addition = zip(parsed_slots["relation"], parsed_slots["addition"])
            parsed_slots.pop("relation", None)
            parsed_slots.pop("addition", None)

            cmd_list = list(parsed_slots.values()) + [j for i in relation_addition for j in i]

        elif "relation" in parsed_slots.keys():
            relation = parsed_slots["relation"]
            parsed_slots.pop("relation", None)

            cmd_list = list(parsed_slots.values()) + relation

        elif "distance" in parsed_slots.keys():
            parsed_slots.pop("num", None)

            cmd_list = list(parsed_slots.values())
        else:
            cmd_list = list(parsed_slots.values())

        cmd_string = ' '.join(map(lambda x: str(x), cmd_list))
        db.insert_into_table_commands(cmd_string)

        gaze_data = receive_data('localhost', 4579)
        rdf_gaze = rdf_gaze_data(gaze_data)
        send_to_robot(rdf_gaze)

        vector = text_to_vector(cmd_string)
        rdf = vector_to_rdf(vector)
        send_to_robot(rdf)

        dispatcher.utter_message(text=f"Команда отправлена: {cmd_string}")

        return []


class ActionAskNum(Action):

    def name(self):
        return "action_ask_num"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain,
    ):
        global cmd_list

        intent = tracker.latest_message['intent']['name']

        commands = db.select_last_n_commands(3)
        cmd_print = []
        for i, cmd in enumerate(commands, 1):
            cmd_list.append(cmd[0])
            cmd_print.append(f"{i}. {cmd[0]}")

        if intent == "wrong_command":
            text_to_user = "Какую команду исправить?\n" + "\n".join(cmd_print)
        elif intent == "repeat_command":
            text_to_user = "Какую команду повторить?\n" + "\n".join(cmd_print)

        dispatcher.utter_message(text=text_to_user)

        return []


class ActionFixCommand(Action):

    def name(self):
        return "action_fix_command"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain,
    ):
        global cmd_list

        cmd_idx = tracker.slots['num'] - 1
        cmd_string = cmd_list[cmd_idx]
        dispatcher.utter_message(f'Исправляю команду: {cmd_string}')
        # db.insert_into_table_commands(cmd_string)

        cmd_list = []

        return []


class ActionRepeatCommand(Action):

    def name(self):
        return "action_repeat_command"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain,
    ):
        global cmd_list

        cmd_idx = tracker.slots['num'] - 1
        cmd_string = cmd_list[cmd_idx]

        gaze_data = receive_data('localhost', 4579)
        rdf_gaze = rdf_gaze_data(gaze_data)
        send_to_robot(rdf_gaze)

        vector = text_to_vector(cmd_string)
        rdf = vector_to_rdf(vector)
        send_to_robot(rdf)

        dispatcher.utter_message(f'Повторяю команду: {cmd_string}')
        db.insert_into_table_commands(cmd_string)

        cmd_list = []

        return []


class ActionSetLocation(Action):

    def name(self):
        return "action_set_location"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain,
    ):

        dispatcher.utter_message("Вокруг меня ...")

        return []
