import time
from collections import deque

from sokoban_competitive.competitive_state import CompetitiveState
from sokoban_single.models.action import Direction


class BaseAgent:
	name = "Search"

	def __init__(self):
		self.recent_positions = deque(maxlen=8)

	def choose_action(
		self,
		environment,
		state: CompetitiveState,
		agent_index: int,
		time_limit: float = 1.0,
	) -> Direction | None:
		current_position = state.agent_positions[agent_index]
		if not self.recent_positions or self.recent_positions[-1] != current_position:
			self.recent_positions.append(current_position)
		deadline = time.perf_counter() + min(max(time_limit, 0.0), 1.0)
		return self.search(environment, state, agent_index, deadline)

	def repeats_recent_walk(self, state, next_state, agent_index: int) -> bool:
		return (
			next_state.boxes == state.boxes
			and next_state.agent_positions[agent_index] in self.recent_positions
		)

	def search(self, environment, state, agent_index, deadline):
		raise NotImplementedError

	@staticmethod
	def state_key(state: CompetitiveState, agent_index: int):
		return (
			state.agent_positions[agent_index],
			tuple(sorted(state.boxes)),
			state.goal_owners,
		)

	@staticmethod
	def heuristic(environment, state: CompetitiveState, agent_index: int) -> int:
		owners = dict(state.goal_owners)
		available_targets = {
			target
			for target in environment.targets
			if owners.get(target) != agent_index
		}
		if not available_targets:
			return 0

		agent_position = state.agent_positions[agent_index]
		best_distance = float("inf")
		for box in state.boxes:
			distance_to_box = abs(agent_position[0] - box[0]) + abs(
				agent_position[1] - box[1]
			)
			for target in available_targets:
				distance_to_target = abs(box[0] - target[0]) + abs(
					box[1] - target[1]
				)
				best_distance = min(
					best_distance, distance_to_box + distance_to_target
				)
		return int(best_distance)

	def fallback_action(self, environment, state, agent_index):
		successors = environment.get_single_agent_successors(state, agent_index)
		if not successors:
			return None
		current_score = environment.score(state, agent_index)
		safe_successors = [
			item
			for item in successors
			if environment.score(item[0], agent_index) >= current_score
		]
		if not safe_successors:
			return None
		fresh_successors = [
			item
			for item in safe_successors
			if not self.repeats_recent_walk(state, item[0], agent_index)
		]
		if fresh_successors:
			safe_successors = fresh_successors

		_, best_action = min(
			safe_successors,
			key=lambda item: (
				-environment.score(item[0], agent_index),
				environment.score(item[0], 1 - agent_index),
				self.heuristic(environment, item[0], agent_index),
			),
		)
		return best_action
