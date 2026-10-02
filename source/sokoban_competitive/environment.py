from pathlib import Path

from common.board import Board
from sokoban_competitive.competitive_state import CompetitiveState, Position
from sokoban_single.models.action import Action, Direction


class CompetitiveEnvironment:
	def __init__(self, map_path: str | Path):
		self.map_path = Path(map_path)
		self.board = Board(str(self.map_path))
		lines = self.map_path.read_text(encoding="utf-8").splitlines()
		self.height = self.board.height
		self.width = self.board.width
		self.walls = set(self.board.walls)
		agent_two: Position | None = None
		boxes = set(self.board.initial_boxes_pos)

		for row_index, line in enumerate(lines):
			for col_index, cell in enumerate(line):
				position = (row_index, col_index)
				if cell == "#":
					self.walls.add(position)
				elif cell == "X":
					agent_two = position

		if self.board.initial_agent_pos is None or agent_two is None:
			raise ValueError("The map must contain both agents: A and X.")
		if not boxes:
			raise ValueError("The map must contain at least one box: B.")
		if not self.board.target:
			raise ValueError("The map must contain at least one D target.")

		self.targets = set(self.board.target)
		self.initial_state = CompetitiveState(
			agent_positions=(self.board.initial_agent_pos, agent_two),
			boxes=frozenset(boxes),
		)

	def is_wall(self, position: Position) -> bool:
		row, col = position
		return (
			row < 0
			or row >= self.height
			or col < 0
			or col >= self.width
			or position in self.walls
		)

	def score(self, state: CompetitiveState, agent_index: int) -> int:
		return sum(
			1
			for position, owner in state.goal_owners
			if owner == agent_index and position in state.boxes and position in self.targets
		)

	def scores(self, state: CompetitiveState) -> tuple[int, int]:
		return self.score(state, 0), self.score(state, 1)

	def get_single_agent_successors(
		self, state: CompetitiveState, agent_index: int
	) -> list[tuple[CompetitiveState, Direction]]:
		successors = []
		agent_position = state.agent_positions[agent_index]
		other_position = state.agent_positions[1 - agent_index]

		for direction in Direction:
			row_delta, col_delta = Action.get_delta(direction)
			next_position = (
				agent_position[0] + row_delta,
				agent_position[1] + col_delta,
			)
			if self.is_wall(next_position) or next_position == other_position:
				continue

			next_boxes = set(state.boxes)
			if next_position in state.boxes:
				box_destination = (
					next_position[0] + row_delta,
					next_position[1] + col_delta,
				)
				if (
					self.is_wall(box_destination)
					or box_destination in state.boxes
					or box_destination == other_position
				):
					continue
				next_boxes.remove(next_position)
				next_boxes.add(box_destination)
				next_owners = dict(state.goal_owners)
				next_owners.pop(next_position, None)
				if box_destination in self.targets:
					next_owners[box_destination] = agent_index
			else:
				next_owners = dict(state.goal_owners)

			next_agents = list(state.agent_positions)
			next_agents[agent_index] = next_position
			next_state = CompetitiveState(
				agent_positions=(next_agents[0], next_agents[1]),
				boxes=frozenset(next_boxes),
				round_number=state.round_number,
				goal_owners=tuple(sorted(next_owners.items())),
			)
			successors.append((next_state, direction))

		return successors

	def resolve_round(
		self,
		state: CompetitiveState,
		actions: tuple[Direction | None, Direction | None]
		| list[Direction | None],
	) -> CompetitiveState:
		intents: list[dict | None] = []

		for agent_index, direction in enumerate(actions):
			if direction is None:
				intents.append(None)
				continue

			row_delta, col_delta = Action.get_delta(direction)
			start = state.agent_positions[agent_index]
			destination = (start[0] + row_delta, start[1] + col_delta)
			other_position = state.agent_positions[1 - agent_index]
			if self.is_wall(destination) or destination == other_position:
				intents.append(None)
				continue

			box_destination = None
			if destination in state.boxes:
				box_destination = (
					destination[0] + row_delta,
					destination[1] + col_delta,
				)
				if (
					self.is_wall(box_destination)
					or box_destination in state.boxes
					or box_destination in state.agent_positions
				):
					intents.append(None)
					continue

			intents.append(
				{
					"agent_destination": destination,
					"box_start": destination if box_destination is not None else None,
					"box_destination": box_destination,
				}
			)

		first, second = intents
		if first is not None and second is not None:
			same_agent_destination = (
				first["agent_destination"] == second["agent_destination"]
			)
			same_box = first["box_start"] is not None and (
				first["box_start"] == second["box_start"]
			)
			same_box_destination = first["box_destination"] is not None and (
				first["box_destination"] == second["box_destination"]
			)
			player_meets_pushed_box = (
				first["agent_destination"] == second["box_destination"]
				or second["agent_destination"] == first["box_destination"]
			)
			if (
				same_agent_destination
				or same_box
				or same_box_destination
				or player_meets_pushed_box
			):
				losing_agent = 1 - (state.round_number % 2)
				intents[losing_agent] = None

		next_agents = list(state.agent_positions)
		next_boxes = set(state.boxes)
		next_owners = dict(state.goal_owners)
		for agent_index, intent in enumerate(intents):
			if intent is None:
				continue
			next_agents[agent_index] = intent["agent_destination"]
			if intent["box_start"] is not None:
				next_boxes.remove(intent["box_start"])
				next_boxes.add(intent["box_destination"])
				next_owners.pop(intent["box_start"], None)
				if intent["box_destination"] in self.targets:
					next_owners[intent["box_destination"]] = agent_index

		return CompetitiveState(
			agent_positions=(next_agents[0], next_agents[1]),
			boxes=frozenset(next_boxes),
			round_number=state.round_number + 1,
			goal_owners=tuple(sorted(next_owners.items())),
		)
