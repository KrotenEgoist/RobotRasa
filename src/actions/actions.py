from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, EventType
from rasa_sdk.types import DomainDict
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
        number = int(tracker.latest_message['entities'])
        with open(filename) as f:
            command = f.readlines()[-number][:-1]
        f.close()
        df = pd.DataFrame([command], columns=['command'])
        df.to_csv(filename, mode='a', header=False, index=False)
        response = requests.post(addr, json={'command': command})
        utter = f'{number} команда с конца "{command}" была повторно передана'
        dispatcher.utter_message(text=utter)
        return []


class ActionResetSlot(Action):
    def name(self):
        return 'action_slot_reset'

    def run(self, dispatcher, tracker, domain):
        return_slots = [AllSlotsReset()]
        return return_slots


class ActionMoveCategory(Action):
    def name(self):
        return 'move_category'

    def run(self, dispatcher, tracker, domain):
        object = tracker.get_slot('object')
        direction = tracker.get_slot('direction')

        if object is None and direction is None:
            move_category = [SlotSet('move_category', 'empty')]
        elif object is not None and direction is not None:
            move_category = [SlotSet('move_category', None)]
        elif object is not None:
            move_category = [SlotSet('move_category', 'object')]
        else:
            move_category = [SlotSet('move_category', 'direction')]
        return move_category


class AskForSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_param"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        move_category = tracker.get_slot('move_category')
        move_category2 = tracker.get_slot('move_category_2')
        entities = [x['entity'] for x in tracker.latest_message['entities'] if
                    x['entity'] != 'object' and x['entity'] != 'direction']
        if move_category == 'object' or move_category2 == 'object':
            # TODO: текст прошлого сообщения, проверка всех комбинаций entities, выход если не совпали
            if len(entities) == 0:
                dispatcher.utter_message(text="К какому?")
            else:
                return [SlotSet('param', 'текст прошлого сообщения без объекта'), SlotSet('requested_slot', None)]
        if move_category == 'direction' or move_category2 == 'direction':
            # TODO: текст прошлого сообщения. Слот на выход из loop, если не distance
            if len(entities) == 0:
                dispatcher.utter_message(text="На сколько?")
            elif 'distance' in entities:
                return [SlotSet('param', 'текст прошлого сообщения без объекта'), SlotSet('requested_slot', None)]
            else:
                dispatcher.utter_message(text="Укажите расстояние?")
        return []


class ValidateMoveCategoryForm(FormValidationAction):
    def name(self):
        return "validate_move_category_form"

    def validate_move_category_2(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        object = tracker.get_slot('object')
        direction = tracker.get_slot('direction')
        if (object is None and direction is None) or (object is not None and direction is not None):
            move_category = {'move_category_2': None}
        elif object is not None:
            move_category = {'move_category_2': 'object'}
        else:
            move_category = {'move_category_2': 'direction'}
        return move_category
