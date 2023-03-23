from pathlib import Path

from src.generator.gen import Generator


project_path = Path(__file__).parents[2]
data_path = project_path.joinpath("src/generator/dictionary")
nlu_path = project_path.joinpath("src/data")

g = Generator(data_path)

amount = 10

patrols = g.generate_patrol(amount=amount)
g.save(patrols, nlu_path)

stops = g.generate_stop(amount=amount)
g.save(stops, nlu_path)

move_dirs = g.generate_move_dir(amount=amount)
g.save(move_dirs, nlu_path)

rotate_dirs = g.generate_rotate_dir(amount=amount)
g.save(rotate_dirs, nlu_path)

objects = g.generate_objects(amount=amount)
g.save(objects, nlu_path)

follows = g.generate_follow(amount=amount)
g.save(follows, nlu_path)
