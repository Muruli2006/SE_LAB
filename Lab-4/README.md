# Maze Runner Lab

This project is a single-topic top-down Maze Runner game using **Pygame**. It introduces students to procedural maze generation, pathfinding, limited visibility, persistent score tracking, and difficulty-based maze sizes, using a small and readable object-oriented codebase.

---

## What's Provided

A working Maze Runner game with:

* A player that moves around a procedurally generated maze
* A maze generated fresh for each game
* An exit that the player must reach
* Keyboard controls for player movement
* A basic Pygame game interface

The project has **four features** left for you to implement. You are expected to **analyze**, **interact with an AI assistant**, and **complete the game** by implementing all four tasks.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**

---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```text
py -3.12 -m pip install -r requirements.txt
```

3. Run the game:

```text
py -3.12 main.py
```

**Controls:** W / A / S / D or Arrow Keys to move.

---

## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Shortest Path Hint

> Add a BFS solver to the maze game. When **H** is pressed, highlight the shortest path from the player's current position to the exit by drawing colored squares on each cell in the path. Press **H** again to toggle the path off.

The solver should find a valid shortest path through the generated maze while respecting the maze walls.

---

### Task 2: Fog of War

> Add fog of war to the maze game. Only show maze cells within a radius of **3 cells** around the player; the rest of the maze should be dark.

Use a dark overlay over the maze and reveal the area around the player using a transparent circular region.

The visible region should move as the player moves.

---

### Task 3: Timer and Top 5 Leaderboard

> After the player solves the maze, save their completion time to a list containing up to **5 entries**, sorted in ascending order. Display the leaderboard on the win screen. Persist the results in a JSON file called **`leaderboard.json`**.

The timer should start when a new maze is generated and stop when the player reaches the exit.

Only the best five completion times should be retained.

---

### Task 4: Difficulty Tiers

> Add a difficulty selection screen before the maze is generated. Show three options: **Easy, Medium, and Hard**, with different maze dimensions. Allow the player to select a difficulty and then start the maze.

Required maze sizes:

* **Easy:** 10 × 8
* **Medium:** 15 × 13
* **Hard:** 20 × 18

The selected difficulty determines the size of the newly generated maze.

---

## Expected Behavior

* Pressing **H** should show the shortest path from the player to the exit and pressing it again should hide the path.
* Only the area within approximately **3 cells** around the player should be visible; distant maze cells should remain dark.
* The timer should record the completion time and the **top 5** times should be stored in `leaderboard.json`.
* The difficulty selection screen should provide **Easy (10×8), Medium (15×13), and Hard (20×18)** options.
* The maze should be generated fresh whenever a new game is started or **R** is pressed.
* The game should display the completion time and leaderboard after the player reaches the exit.

---

## Controls

| Key     | Function                  |
| ------- | ------------------------- |
| W / ↑   | Move Up                   |
| S / ↓   | Move Down                 |
| A / ←   | Move Left                 |
| D / →   | Move Right                |
| H       | Toggle Shortest Path Hint |
| R       | Generate a New Maze       |
| M / ESC | Return to Difficulty Menu |

---

## Folder Structure

```text
maze-runner/
├── main.py
├── requirements.txt
├── game/
│   ├── __init__.py
│   ├── game_engine.py
│   ├── maze.py
│   └── player.py
└── README.md
```

---

## Lab 4 Submission Folder

The submission folder for this lab contains:

```text
Lab-4/
├── Chat_History/
├── Updated_Code/
├── Videos/
└── README.md
```

### Updated Code

```text
Updated_Code/
├── main.py
├── requirements.txt
├── leaderboard.json
└── game/
    ├── __init__.py
    ├── game_engine.py
    ├── maze.py
    └── player.py
```

### Videos

```text
Videos/
├── before.mp4
└── after.mp4
```

### Chat History

The `Chat_History` folder contains the complete LLM interaction documenting the implementation of all four tasks.

---

## Technologies Used

* Python
* Pygame
* Breadth-First Search (BFS)
* JSON
* Object-Oriented Programming

---

## Submission Checklist

Submission contains the following deliverables:

* A **10-second video before changes**, showing the original Maze Runner game.
* A **10-second video after changes**, showing the implemented features working.
* The **complete Chat/LLM history** used during development.
* Updated source code containing all four completed tasks.
* `leaderboard.json` containing the persistent leaderboard data.
* `README.md` describing the project and implemented features.

---

## Final Implementation

The completed Maze Runner includes:

1. **Shortest Path Hint using BFS**
2. **Fog of War with a 3-cell visibility radius**
3. **Timer with persistent Top 5 leaderboard**
4. **Easy, Medium, and Hard difficulty tiers**

All features are integrated into the existing Pygame Maze Runner project while maintaining fresh maze generation and the original player movement functionality.
