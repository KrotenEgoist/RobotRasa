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

        print(parsed_slots.items())

        dispatcher.utter_message(text="Команда отправлена")

        return []
