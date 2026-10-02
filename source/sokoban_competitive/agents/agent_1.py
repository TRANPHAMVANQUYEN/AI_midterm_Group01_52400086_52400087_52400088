import time
from collections import deque

from sokoban_competitive.agents.base_agent import BaseAgent


class Agent1(BaseAgent):
	name = "Agent 1 - BFS"

	def search(self, environment, state, agent_index, deadline):
		starting_score = environment.score(state, agent_index)
		fallback = self.fallback_action(environment, state, agent_index)
		queue = deque([(state, None)])
		visited = {self.state_key(state, agent_index)}
		best_action = fallback
		best_distance = self.heuristic(environment, state, agent_index)

		while queue and time.perf_counter() < deadline:
			current_state, first_action = queue.popleft()
			for next_state, action in environment.get_single_agent_successors(
				current_state, agent_index
			):
				if first_action is None and self.repeats_recent_walk(
					state, next_state, agent_index
				):
					continue
				next_score = environment.score(next_state, agent_index)
				if first_action is None and next_score < starting_score:
					continue
				if next_score > starting_score:
					return first_action or action

				key = self.state_key(next_state, agent_index)
				if key in visited:
					continue
				visited.add(key)
				next_first_action = first_action or action
				distance = self.heuristic(environment, next_state, agent_index)
				if distance < best_distance:
					best_distance = distance
					best_action = next_first_action
				queue.append((next_state, next_first_action))

		return best_action
