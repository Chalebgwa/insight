"""Simple AI agent that performs weighted-sum predictions.

The agent expects a path to a JSON file containing a list of weights.
"""

from __future__ import annotations

import json
from typing import List, Sequence


class AIAgent:
    """Load model weights and run predictions using a weighted sum."""

    def __init__(self, weights_path: str) -> None:
        self.weights = self._load_weights(weights_path)

    def _load_weights(self, path: str) -> List[float]:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            raise ValueError("Weights file must contain a list of numbers")
        return [float(w) for w in data]

    def predict(self, inputs: Sequence[float]) -> float:
        if len(inputs) != len(self.weights):
            raise ValueError("Input length must match number of weights")
        return sum(w * x for w, x in zip(self.weights, inputs))
