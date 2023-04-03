from rasa_sdk import Action, Tracker, FormValidationAction
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
                subject = entity['value']
                slot = SlotSet("subject", subject)
            except KeyError:
                role = None
                slot = SlotSet("subject", None)

        match role:
            case "direction":
                dispatcher.utter_message(text="Укажите количество метров")
            case "object":
                dispatcher.utter_message(text=f"Уточните местоположение объекта {subject}")

        return [slot]


class ValidateFeatureForm(FormValidationAction):

    def name(self):
        return "validate_feature_form"

    def validate_feature(
        self,
        slot_value,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain,
    ):

        return {"feature": slot_value}


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
