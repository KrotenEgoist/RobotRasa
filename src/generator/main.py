from pathlib import Path

from gen import Generator


project_path = Path(__file__).parents[2]
data_path = project_path.joinpath("src/generator/dictionary")
nlu_path = project_path.joinpath("src/data")

g = Generator(data_path)

move_dir = g.generate_move_dir(amount=100, start=1, end=50)
move_to = g.generate_move_to(states=10, amount=200)
g.save({"command_move_subject": move_dir + move_to}, nlu_path)
