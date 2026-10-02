from dataclasses import dataclass


Position = tuple[int, int]


@dataclass(frozen=True)
class CompetitiveState:
	agent_positions: tuple[Position, Position]
	boxes: frozenset[Position]
	round_number: int = 0
	goal_owners: tuple[tuple[Position, int], ...] = ()
