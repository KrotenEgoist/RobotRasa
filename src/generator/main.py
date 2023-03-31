from pathlib import Path

from src.generator.gen import Generator


project_path = Path(__file__).parents[2]
data_path = project_path.joinpath("src/generator/dictionary")
nlu_path = project_path.joinpath("src/data")

g = Generator(data_path)

patrols = g.generate_patrol(amount=5)
stops = g.generate_stop(amount=25)

move_dirs = g.generate_move_dir(amount=5)
rotate_dirs = g.generate_rotate_dir(amount=5)
# g.save({"direction_commands": move_dirs + rotate_dirs}, nlu_path)

objects = g.generate_objects(states=4, amount=5)
# g.save({"object_commands": objects}, nlu_path)

follows = g.generate_follow(amount=25)
wrong = g.generate_wrong(amount=25)
fallback = g.generate_fallback(amount=25, range_eng=(0, 0), range_rus=(2, 20), range_dig=(0, 3), range_spc=(0, 3))

action = g.generate_action(amount=25)

g.save({"commands_with_attributes": move_dirs + rotate_dirs + objects}, nlu_path)

# g.save({"action_only": action}, nlu_path)

# patrol_command = {"patrol_command": patrols}
# g.save(patrol_command, nlu_path)

# action_command = {"action_command": action}
# g.save(action_command, nlu_path)
#
# simple_command = {"simple_command": stops}
# g.save(simple_command, nlu_path)
#
# object_command = {"object_command": objects + follows}
# g.save(object_command, nlu_path)

# attr_command = {"attr_command": objects + follows + move_dirs + rotate_dirs}
# g.save(attr_command, nlu_path)

# wrong_dict = {"wrong_command": wrong}
# g.save(wrong_dict, nlu_path)

# fallback = {"nlu_fallback": fallback}
# g.save(fallback, nlu_path)
