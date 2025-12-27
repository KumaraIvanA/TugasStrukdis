from dataclasses import dataclass
from collections import defaultdict


@dataclass(frozen=True)
class Graph:
    adj_matrix: defaultdict[str, dict[str, bool]]

    def get_colors(self) -> dict[str, int]:
        return {}
