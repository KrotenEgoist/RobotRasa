from pathlib import Path

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, SlotSet, ActiveLoop

from src.db.control_db import ControlDB


project_path = Path(__file__).parents[2]
db_path = project_path.joinpath("database/rasa.db")
database = ControlDB(db_path)


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
        database.insert_into_table_commands(cmd_string)

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

        commands = database.select_last_n_commands(3)
        cmd_list = []
        for i, cmd in enumerate(commands, 1):
            cmd_list.append(f"{i}. {cmd[0]}")

        text_to_user = "Какую команду исправить?\n" + "\n".join(cmd_list)
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


        return []