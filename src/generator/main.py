from pathlib import Path

from src.generator.gen import Generator


project_path = Path(__file__).parents[2]
data_path = project_path.joinpath("src/generator/dictionary")
nlu_path = project_path.joinpath("src/data")

g = Generator(data_path)

patrols = g.generate_patrol(amount=10)
stops = g.generate_stop(amount=50)
move_dirs = g.generate_move_dir(amount=3)
rotate_dirs = g.generate_rotate_dir(amount=3)
objects = g.generate_objects(states=4, amount=3)
follows = g.generate_follow(amount=50)
wrong = g.generate_wrong(amount=50)
fallback = g.generate_fallback(amount=50, range_eng=(0, 0), range_rus=(2, 20), range_dig=(0, 3), range_spc=(0, 3))
action = g.generate_action(amount=5)

commands_dict = {"command": patrols + stops + move_dirs + rotate_dirs + objects + follows + action}
wrong_dict = {"wrong_command": wrong}
fallback = {"nlu_fallback": fallback}

g.save(commands_dict, nlu_path)
g.save(wrong_dict, nlu_path)
g.save(fallback, nlu_path)
