from transitions import Machine


class Command(object):
    states = ['S', 'Adir', 'Aobj', 'A_dir', 'A_num', 'A_dir_num', 'A_obj', 'A_gaze_obj', 'A_near', 'A_near_obj',
              'A_obj_rel', 'A_rel',
              'A_obj_rel_obj', 'A_gaze']

    def __init__(self):
        utter = 'utter'
        self.utter_text = 'Какое действие?'
        self.machine = Machine(self, states=Command.states, initial='S', auto_transitions=False)
        # {иди, поворот}
        self.machine.add_transition('obj_dir', 'S', 'Adir', after=utter)

        # {обыскивай, анализируй}
        self.machine.add_transition('obj', 'S', 'Aobj', after=utter)

        # иди {на север}
        self.machine.add_transition('direction', 'Adir', 'A_dir', after=utter)

        # иди на север {5 метров}
        self.machine.add_transition('num', 'A_dir', 'A_dir_num')

        # иди {5 метров}
        self.machine.add_transition('num', 'Adir', 'A_num', after=utter)

        # иди 5 метров {на север}
        self.machine.add_transition('direction', 'A_num', 'A_dir_num')

        # иди {к дереву}, анализируй {дерево}
        self.machine.add_transition('object', ['Adir', 'Aobj'], 'A_obj', after=utter)

        # иди {справа}, анализируй {справа}
        self.machine.add_transition('relation', ['Adir', 'Aobj'], 'A_rel', after=utter)

        # иди {близкому}, анализируй {близкий}
        self.machine.add_transition('nearest', ['Adir', 'Aobj'], 'A_near', after=utter)

        # иди {к тому}, анализируй {тот}
        self.machine.add_transition('gaze', ['Adir', 'Aobj'], 'A_gaze', after=utter)

        # иди к дереву {тому}, анализируй дерево {то}
        self.machine.add_transition('gaze', 'A_obj', 'A_gaze_obj')

        # иди к тому {дереву}, анализируй то {дерево}
        self.machine.add_transition('object', 'A_gaze', 'A_gaze_obj')

        # иди к близкому {дереву}, анализируй близкое {дерево}
        self.machine.add_transition('object', 'A_near', 'A_near_obj')

        # иди к дереву {близкому}, анализируй дерево {близкое}
        self.machine.add_transition('nearest', 'A_obj', 'A_near_obj')

        # иди к дереву {справа}, анализируй дерево {справа}
        self.machine.add_transition('relation', 'A_obj', 'A_obj_rel')

        # иди справа {к дереву}, анализуруй справа {дерево}
        self.machine.add_transition('object', 'A_rel', 'A_obj_rel')

        # иди к дереву спарава {дома}, анализуруй дерево спарава {дома}
        self.machine.add_transition('object', 'A_obj_rel', 'A_obj_rel_obj')

        # иди к дереву спарава дома {севернее}, анализуруй дерево спарава дома {севернее}
        self.machine.add_transition('relation', 'A_obj_rel_obj', 'A_obj_rel')

    def utter(self, **arg):
        state = self.state
        if state == 'Adir':
            self.utter_text = 'Куда?'
        elif state == 'Aobj':
            self.utter_text = 'Какой объект?'
        elif state == 'A_dir':
            self.utter_text = 'На сколько?'
        elif state == 'A_obj':
            self.utter_text = 'Какому?'
        elif state == 'A_near':
            self.utter_text = 'Какой объект?'
        elif state == 'A_gaze':
            self.utter_text = 'Какой объект?'
        elif state == 'A_rel':
            self.utter_text = 'Какого объекта?'
        elif state == 'A_num':
            self.utter_text = 'Куда?'
        else:
            self.utter_text = None
