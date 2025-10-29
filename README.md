# Personality Graph Project

An interactive knowledge-graph prototype that converts criminal-suspect statements into a dynamic, Obsidian-like graph view to explore relationships between situations, emotions, actions, and motives. The project began as a static graph generator and was extended to a rich, physics-driven interactive visualization with collapsible nodes and continuous motion.

---

## Project overview

This repository contains two main scripts:

- `generate_synthetic_statement.py` — creates realistic, multi-paragraph synthetic statements (intro → event paragraphs → closing). The generator accepts `--events` and `--seed` to control output.
- `process_build_graph.py` — parses the statement text, extracts entities (situation, emotion, action, motive) with a lightweight heuristic extractor, builds a NetworkX directed graph, and renders an interactive, physics-driven visualization using `pyvis` (vis.js). The visualization opens in your browser as `knowledge_graph.html`.

The workflow is:
1. Generate (or provide) `criminal_statement.txt`.
2. Run the graph builder which extracts events/entities and builds a knowledge graph.
3. Visualize the graph in a browser with dynamic motion and expand/collapse behavior.

---

## Design (Concept)

Design 5 — Personality–Context–Outcome Graph (Dynamic Personality Model)

Use case: Capturing situational behavior — how personality changes across contexts (e.g., “in teams”, “under stress”).

Structure (example):

```
[Person]
 ├── has_trait → [Extraversion (Moderate)]
 ├── in_context → [Team Project]
 │      └── exhibits_behavior → [Leadership]
 │             └── leads_to → [Positive Group Outcome]
 ├── in_context → [Research Work]
 │      └── exhibits_behavior → [Independent Analysis]
```

Key relationships used in this design

- `in_context` — ties a person to a situation or environment
- `exhibits_behavior` — observed behavior in that context
- `leads_to` — outcome or consequence of the behavior in that context
- `modulates_in_context` — relation to indicate trait modulation by context

Advantages

- ✅ Reflects real human personality variability
- ✅ Useful in workplace or learning analytics
- ✅ Can integrate with temporal or graph embeddings for downstream modeling

---

## Architecture

The project is intentionally small and modular:

- `generate_synthetic_statement.py` — generator (text-only). Produces `criminal_statement.txt`.
- `process_build_graph.py` — extractor + graph builder + visualizer.
  - `extract_entities` — heuristic rule-based extractor that operates on sentence windows (no heavy NLP dependencies).
  - `build_knowledge_graph` — builds a NetworkX DiGraph of statements and their entities.
  - `visualize_graph` — uses `pyvis` to create a dynamic HTML visualization that:
    - Shows only root statements initially
    - Allows clicking a node to expand/collapse connected nodes
    - Uses physics simulation (Barnes-Hut) and custom JS to add continuous floating/random motion
    - Applies a dark Obsidian-like theme and node coloring by entity type

A simplified architecture diagram (ASCII):

```
[criminal_statement.txt] --> [extract_entities] --> [NetworkX DiGraph] --> [pyvis HTML generator]
                                                            |
                                                            v
                                                 [knowledge_graph.html (dynamic, interactive)]
```

Additionally, `figure_1.png` (first iteration static graph) can be placed at the repository root and referenced in this README as a visual comparison between the static and dynamic views. If you have that file, place it here as `figure_1.png`.

---

## Tools & Tech Stack

- Python 3.10+ (3.12 tested in dev environment)
- Libraries (see `requirements.txt`):
  - `networkx` — graph creation & manipulation
  - `pyvis` — interactive browser visualization built on vis.js

Optional (for higher quality NLP extraction, not currently required):
- `spaCy` (and appropriate model like `en_core_web_sm`) — for dependency parsing, NER, coreference

Front-end tech used via `pyvis`:
- vis.js — physics-based force simulations, event hooks, and DOM export to HTML
- Custom JS injected to implement randomly timed impulses / wobble and expand/collapse behavior

---

## How to run

1. (Optional) Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# If you add spaCy later: pip install spacy && python -m spacy download en_core_web_sm
```

2. Generate a synthetic, cohesive statement (example with 2 events)

```bash
python generate_synthetic_statement.py --events 2 --seed 42
```

This writes `criminal_statement.txt` to the repository root. Open it to see an intro, event paragraphs, and a closing paragraph.

3. Build and view the interactive graph

```bash
python process_build_graph.py
```

This will:
- Parse `criminal_statement.txt` into statement entities
- Build a knowledge graph (statement nodes and entity nodes)
- Produce `knowledge_graph.html` and open it in your default browser

Interacting with the graph:
- Root (Statement) nodes are visible initially
- Click any node to expand / collapse its neighbors
- Drag nodes to reposition
- Zoom and pan
- Nodes gently float and wobble for an Obsidian-like dynamic feel

---

## Figure 1 — Static graph (first iteration)

If you've kept the original static PNG from the project's early stage, place it in the repo as `figure_1.png` and it will be rendered alongside this README on GitHub. This README references the static figure to demonstrate the project's progression from static Matplotlib graphs to a dynamic vis.js powered layout.

Example (add `figure_1.png` to the repo root):

<img width="1000" height="800" alt="Figure_1" src="https://github.com/user-attachments/assets/8c7c267c-a10f-4103-8df9-75185f37d617" />


---

## Examples & Sample Output

Below is an example of the generator output (shortened):

> The following is the recorded statement given by the suspect during questioning.
>
> During the interrogation room, the suspect appeared calm and explained the plan calmly. When questioned about the reasons, he said he wanted recognition; at times his voice wavered and he seemed uncertain about some details. Officers noted changes in his tone and body language, which suggested complexity in his motives and emotions.
>
> The recorded account was logged and appended to the case file for further review.

The extractor will identify events and map them to nodes like `Statement_1`, `Situation: the interrogation room`, `Emotion: calm`, `Action: explained the plan calmly`, and `Motive: wanted recognition`.

---

## Design decisions & notes

- Rule-based extraction keeps the toolchain lightweight and quick to iterate. It is tuned to the generator's phrasing and short real-world-style statements.
- `pyvis` + `vis.js` was chosen because it supports physics, continuous motion, and easy export to a standalone HTML file without spinning up a web server.
- The custom JS injected into the generated HTML implements continuous random impulses and a gentle wobble to make nodes never fully settle (Obsidian-like feeling). It also handles expand/collapse by toggling node `hidden` states.

Trade-offs:
- This approach is fast to prototype but not as robust on arbitrary real-world text as a small NLP pipeline would be.
- If you need large-scale ingestion or higher extraction accuracy, consider integrating spaCy + a simple classifier or rule-tuning step.

---

## Next steps (suggested)

- (Optional) Integrate spaCy for more accurate extraction (NER, dependency parsing, and coreference resolution).
- Persist graphs to a small graph database (e.g., Neo4j, ArangoDB) for queries and embedding training.
- Add a small web front-end (Flask/FastAPI + d3/vis) to load different statement files and allow saving modified graphs.
- Add unit tests for the extractor and graph builder.
- Add interactive filters (by node type, by trait/context) in the HTML UI.

---

## Troubleshooting

- If `knowledge_graph.html` fails to render or is blank, ensure `pyvis` is installed and that `criminal_statement.txt` exists and is non-empty.
- If node motion appears static, check that your browser allows running the embedded JavaScript and that the generated HTML contains the injected JS (open and inspect the file in a text editor).

---


