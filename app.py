
from flask import Flask, render_template, request, jsonify
from collections import deque

app = Flask(__name__)


# Convert stack input into a state
# Example: A B means A is on B, and B is on TABLE
def parse_stacks(text):
    state = {}

    for line in text.strip().splitlines():
        blocks = line.upper().split()

        for i, block in enumerate(blocks):
            if block in state:
                raise ValueError(f"Block {block} appears more than once")

            state[block] = blocks[i + 1] if i + 1 < len(blocks) else "TABLE"

    if not state:
        raise ValueError("Please enter at least one block")

    return state


def get_clear(state):
    occupied = set(state.values())
    return set(state) - occupied


# Generate actions using STRIPS-style preconditions and effects
def get_actions(state):
    clear = get_clear(state)
    actions = []

    for block in sorted(clear):
        old_support = state[block]

        # A block can be moved onto the table
        if old_support != "TABLE":
            actions.append((block, "TABLE"))

        # Or onto another clear block
        for target in sorted(clear):
            if target != block and target != old_support:
                actions.append((block, target))

    return actions


def apply_action(state, action):
    block, target = action
    new_state = state.copy()
    new_state[block] = target
    return new_state


# Find a plan from initial state to goal state
def plan(initial, goal):
    if set(initial) != set(goal):
        raise ValueError(
            "Initial and goal states must contain the same blocks"
        )

    start = tuple(sorted(initial.items()))
    target = tuple(sorted(goal.items()))

    queue = deque([(start, [])])
    visited = {start}

    while queue:
        current, path = queue.popleft()
        state = dict(current)

        if current == target:
            return path

        for action in get_actions(state):
            new_state = apply_action(state, action)
            new_key = tuple(sorted(new_state.items()))

            if new_key not in visited:
                visited.add(new_key)
                queue.append((new_key, path + [action]))

    return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/solve", methods=["POST"])
def solve():
    try:
        data = request.get_json()

        initial = parse_stacks(data["initial"])
        goal = parse_stacks(data["goal"])

        if set(initial) != set(goal):
            return jsonify({
                "error": "Use exactly the same blocks in both states."
            }), 400

        # Validate that the support relationships form valid stacks
        for state in (initial, goal):
            for block in state:
                seen = set()
                current = block

                while current != "TABLE":
                    if current not in state or current in seen:
                        raise ValueError(
                            "Invalid arrangement: check block order."
                        )
                    seen.add(current)
                    current = state[current]

        result = plan(initial, goal)

        if result is None:
            return jsonify({"error": "No plan found."}), 400

        moves = []
        for i, (block, target) in enumerate(result, start=1):
            destination = (
                "the table" if target == "TABLE"
                else f"block {target}"
            )
            moves.append({
                "step": i,
                "action": f"Move block {block} onto {destination}"
            })

        return jsonify({
            "moves": moves,
            "count": len(moves),
            "message": "Goal already achieved!"
            if not moves else "Plan generated successfully!"
        })

    except (ValueError, KeyError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True)
