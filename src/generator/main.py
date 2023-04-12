from pathlib import Path

from upgen import SampleGenerator


project_path = Path(__file__).parents[2]
data_path = project_path.joinpath("src/generator/dictionary")
nlu_path = project_path.joinpath("src/data")

g = SampleGenerator(data_path)

action = g.generate_action(amount=250)
g.save({"action": action}, nlu_path)

direction = g.generate_direction(amount=10)
g.save({"directions": direction}, nlu_path)

action_direction = g.generate_action_direction(amount=10)
g.save({"action+directions": action_direction}, nlu_path)

objects = g.generate_object(states=10, amount=10)
g.save({"objects": objects}, nlu_path)

action_objects = g.generate_action_object(states=10, amount=10)
g.save({"action+objects": action_objects}, nlu_path)
