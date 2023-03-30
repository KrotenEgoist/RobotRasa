# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionSendCommand(Action):

    def name(self):
        return "action_send_command"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain):

        intent = tracker.latest_message["intent"]["name"]

        for i in tracker.latest_message["entities"]:
            print(i["value"], i["entity"])

        entities = ', '.join(['|'.join([str(i["value"]), str(i["entity"])]) for i in tracker.latest_message["entities"]])

        dispatcher.utter_message(text=f"Команда {intent} {entities}")

        return []
