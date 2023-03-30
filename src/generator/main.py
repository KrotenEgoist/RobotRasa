from pathlib import Path

from src.generator.gen import Generator


project_path = Path(__file__).parents[2]
data_path = project_path.joinpath("src/generator/dictionary")
nlu_path = project_path.joinpath("src/data")

g = Generator(data_path)

# patrols = g.generate_patrol(amount=20)
# g.save(patrols, nlu_path)
#
# stops = g.generate_stop(amount=100)
# g.save(stops, nlu_path)
#
# move_dirs = g.generate_move_dir(amount=5)
# g.save(move_dirs, nlu_path)
#
# rotate_dirs = g.generate_rotate_dir(amount=5)
# g.save(rotate_dirs, nlu_path)
#
# objects = g.generate_objects(states=4, amount=5)
# g.save(objects, nlu_path)
#
# follows = g.generate_follow(amount=100)
# g.save(follows, nlu_path)
#
# wrong = g.generate_wrong(amount=100)
# g.save(wrong, nlu_path)
#
# fallback = g.generate_fallback(range_eng=(0, 0), range_rus=(2, 20), range_dig=(0, 3), range_spc=(0, 3))
# g.save(fallback, nlu_path)

action = g.generate_action()
g.save(action, nlu_path)
