from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset


class ActionSendCommand(Action):

    def name(self):
        return "action_send_command"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain,
    ):

        intent = tracker.latest_message["intent"]["name"]

        entities = ', '.join(['|'.join([str(i["value"]), str(i["entity"])]) for i in tracker.latest_message["entities"]])

        dispatcher.utter_message(text=f"Команда {intent} {entities}")

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

        return [AllSlotsReset()]
