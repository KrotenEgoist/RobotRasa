from pathlib import Path

from upgen import SampleGenerator


project_path = Path(__file__).parents[2]
data_path = project_path.joinpath("src/generator/dictionary")
nlu_path = project_path.joinpath("src/data")

g = SampleGenerator(data_path)

# команды движения и поворота
move_dir = g.generate_move_dir(amount=10, start=1, end=50)
print(f"Создано {len(move_dir)} примеров команд move_dir")
move_to = g.generate_move_to(states=10, amount=15)
print(f"Создано {len(move_to)} примеров команд move_to")
rotate_dir = g.generate_rotate_dir(amount=10, start=1, end=360)
print(f"Создано {len(rotate_dir)} примеров команд rotate_dir")
g.save({"command_move_subject": move_dir + rotate_dir + move_to}, nlu_path)

# команды с объектами
objects = g.generate_objects(states=10, amount=5)
print(f"Создано {len(objects)} примеров команд objects")
g.save({"command_objects": objects}, nlu_path)
