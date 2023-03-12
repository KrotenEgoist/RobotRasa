from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import pandas as pd
import requests
import re

addr = 'http://127.0.0.1:5000'
filename = 'commands.log'

class ActionCommand(Action):

    def name(self) -> Text:
        return "send_command"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        command = tracker.latest_message['text'].lower()
        command = re.sub(r'[.,"\'-?:!;]', '', command)
        df = pd.DataFrame([command], columns=['command'])
        df.to_csv(filename, mode='a', header=False, index=False)
        response = requests.post(addr, json={'command': command})
        utter = f'Команда "{command}" была передана'
        dispatcher.utter_message(text=utter)
        return []


class ActionWrongCommand(Action):

    def name(self) -> Text:
        return "send_wrong_command"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open(filename) as f:
            command = f.readlines()[-1][:-1]
        f.close()
        utter = f'Сообщение об ошибке в команде "{command}" была передана'
        dispatcher.utter_message(text=utter)
        return []


class ActionStoryCommand(Action):

    def name(self) -> Text:
        return "send_story_command"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        number = int(tracker.latest_message['entities'][0]['value'])
        with open(filename) as f:
            command = f.readlines()[-number][:-1]
        f.close()
        df = pd.DataFrame([command], columns=['command'])
        df.to_csv(filename, mode='a', header=False, index=False)
        response = requests.post(addr, json={'command': command})
        utter = f'{number} команда с конца "{command}" была повторно передана'
        dispatcher.utter_message(text=utter)
        return []
