
async function solveProblem() {
    const initial = document.getElementById("initial").value;
    const goal = document.getElementById("goal").value;
    const button = document.getElementById("solveBtn");
    const status = document.getElementById("status");
    const steps = document.getElementById("steps");

    button.disabled = true;
    status.textContent = "Planning in progress...";
    steps.replaceChildren();
    document.getElementById("stepCount").textContent = "…";
    document.getElementById("resultStatus").textContent = "Working";

    try {
        const response = await fetch("/solve", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ initial, goal })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong.");
        }

        document.getElementById("stepCount").textContent = data.count;
        document.getElementById("resultStatus").textContent = "Success";
        status.textContent = data.message;

        if (data.moves.length === 0) {
            const message = document.createElement("p");
            message.className = "empty";
            message.textContent = "The initial state already matches the goal.";
            steps.appendChild(message);
        }

        data.moves.forEach(move => {
            const row = document.createElement("div");
            row.className = "step";

            const number = document.createElement("span");
            number.className = "number";
            number.textContent = String(move.step).padStart(2, "0");

            const description = document.createElement("span");
            description.textContent = move.action;

            row.append(number, description);
            steps.appendChild(row);
        });

    } catch (error) {
        document.getElementById("stepCount").textContent = "—";
        document.getElementById("resultStatus").textContent = "Error";
        status.textContent = error.message;

        const message = document.createElement("p");
        message.className = "empty";
        message.textContent = "Please check your block arrangements and try again.";
        steps.appendChild(message);
    } finally {
        button.disabled = false;
    }
}
