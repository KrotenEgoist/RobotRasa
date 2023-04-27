from pathlib import Path

from upgen import SampleGenerator


project_path = Path(__file__).parents[2]
data_path = project_path.joinpath("src/generator/dictionary")
nlu_path = project_path.joinpath("src/data")

g = SampleGenerator(data_path)

action = g.generate_action(amount=500)
g.save({"action": action}, nlu_path)

direction = g.generate_direction(amount=25)
g.save({"directions": direction}, nlu_path)

action_direction = g.generate_action_direction(amount=25)
g.save({"action+directions": action_direction}, nlu_path)

objects = g.generate_object(states=10, amount=20)
g.save({"objects": objects}, nlu_path)

action_objects = g.generate_action_object(states=20, amount=20)
g.save({"action+objects": action_objects}, nlu_path)

patrol = g.generate_patrol(amount=40)
g.save({"patrol": patrol}, nlu_path)

routes = g.generate_route(amount=40)
g.save({"routes": routes}, nlu_path)

patrol_routes = g.generate_patrol_route(amount=40)
g.save({"patrol+routes": patrol_routes}, nlu_path)

simple_action = g.generate_simple_action(amount=100)
g.save({"simple_action": simple_action}, nlu_path)
