import time

from sokoban_competitive.agents.base_agent import BaseAgent


class Agent2(BaseAgent):
	name = "Agent 2 - DFS"

	def search(self, environment, state, agent_index, deadline):
		starting_score = environment.score(state, agent_index)
		fallback = self.fallback_action(environment, state, agent_index)
		depth_limit = 1
		start_key = self.state_key(state, agent_index)

		while time.perf_counter() < deadline:
			frontier = [(state, None, 0, frozenset({start_key}))]

			while frontier and time.perf_counter() < deadline:
				current_state, first_action, depth, path_keys = frontier.pop()
				if depth >= depth_limit:
					continue

				successors = environment.get_single_agent_successors(
					current_state, agent_index
				)
				for next_state, action in reversed(successors):
					if first_action is None and self.repeats_recent_walk(
						state, next_state, agent_index
					):
						continue
					next_score = environment.score(next_state, agent_index)
					if first_action is None and next_score < starting_score:
						continue
					if next_score > starting_score:
						return first_action or action

					next_key = self.state_key(next_state, agent_index)
					if next_key in path_keys:
						continue
					frontier.append(
						(
							next_state,
							first_action or action,
							depth + 1,
							path_keys | {next_key},
						)
					)

			depth_limit += 1

		return fallback

	def fallback_action(self, environment, state, agent_index):
		successors = environment.get_single_agent_successors(state, agent_index)
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

		_, action = min(
			safe_successors,
			key=lambda item: (
				-environment.score(item[0], agent_index),
				environment.score(item[0], 1 - agent_index),
				item[0].boxes != state.boxes,
			),
		)
		return action
