from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, SlotSet, Form, ActiveLoop


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
                dispatcher.utter_message(template="utter_ask_relation")
            case "direction":
                dispatcher.utter_message(template="utter_ask_distance")

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
