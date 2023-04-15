from typing import Any, Text, Dict, List

import pandas as pd
import requests
from . import fsm
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, AllSlotsReset, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

addr = 'http://127.0.0.1:5000'
filename = 'commands.log'
command = fsm.Command()


class ActionCommand(Action):

    def name(self) -> Text:
        return "send_command"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        command = ValidateCommandForm.command_text
        command_interpretation = ValidateCommandForm.command_interpretation
        # command = tracker.latest_message['text'].lower()
        # command = re.sub(r'[.,"\'-?:!;]', '', command)
        # df = pd.DataFrame([command], columns=['command'])
        # df.to_csv(filename, mode='a', header=False, index=False)
        # response = requests.post(addr, json={'command': command})
        utter = f'Команда "{command}" была передана\nИтерпретация команды: {command_interpretation}'
        dispatcher.utter_message(text=utter)
        return []


class ActionResetSlot(Action):
    def name(self):
        return 'action_slot_reset'

    def run(self, dispatcher, tracker, domain):
        return_slots = [AllSlotsReset()]
        ValidateCommandForm.command_interpretation = []
        ValidateCommandForm.command_text = []
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


class ValidateCommandForm(FormValidationAction):
    command_text = []
    command_interpretation = []
    cur_interpretation = []
    cur_text = []

    def name(self):
        return "validate_command_form"

    def validate_param(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        self.cur_interpretation = [x['role'] if x['entity'] == 'action' else 'num'
        if x['extractor'] == 'DucklingEntityExtractor' else x['entity'] for x in
                                   tracker.latest_message['entities']]
        self.cur_text = [x['value'] for x in tracker.latest_message['entities']]
        try:
            for word, text in zip(self.cur_interpretation, self.cur_text):
                try:
                    command.trigger(word)
                    self.command_interpretation.append(word)
                    self.command_text.append(text)
                    utter_help = None
                except Exception:
                    raise
        except Exception:
            utter_help = f'Укажите {command.machine.get_triggers(command.state)}'

        if command.state not in ['A_dir_num', 'A_near_obj', 'A_obj_rel', 'A_obj_rel_obj', 'A_gaze_obj']:
            utter_text = command.utter_text
            if utter_help is not None:
                utter_text = utter_text + '\n' + utter_help
            dispatcher.utter_message(text=utter_text)
            return {'param': None}
        else:
            dispatcher.utter_message(text='Принял')
            command.machine.set_state('S')
            return {'requested_slot': None}
