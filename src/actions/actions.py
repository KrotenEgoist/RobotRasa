from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, SlotSet


class AskSubjectAction(Action):

    def name(self):
        return "action_ask_subject"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain
    ):

        dispatcher.utter_message(text="Назовите объект или направление")

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
        for entity in tracker.latest_message['entities']:
            try:
                role = entity['role']
            except KeyError:
                role = None

        match role:
            case "direction":
                dispatcher.utter_message(text="Укажите количество метров")
            case "object":
                dispatcher.utter_message(text="Уточните местоположение объекта")

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
