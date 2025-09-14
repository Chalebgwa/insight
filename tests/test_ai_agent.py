import os, sys, json, tempfile, pytest; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.ai_agent import AIAgent


def test_ai_agent_predict():
    weights = [0.5, 1.5, -1.0]
    with tempfile.NamedTemporaryFile("w", delete=False) as fh:
        json.dump(weights, fh)
        path = fh.name
    try:
        agent = AIAgent(path)
        assert agent.predict([2, 2, 2]) == pytest.approx(2.0)
    finally:
        os.remove(path)


def test_ai_agent_mismatched_input():
    weights = [1.0, 2.0]
    with tempfile.NamedTemporaryFile("w", delete=False) as fh:
        json.dump(weights, fh)
        path = fh.name
    try:
        agent = AIAgent(path)
        with pytest.raises(ValueError):
            agent.predict([1.0])
    finally:
        os.remove(path)
