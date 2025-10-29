import re
import networkx as nx
from pyvis.network import Network
import json
import webbrowser
from pathlib import Path

def extract_entities(statement_text):
    """
    Heuristic extraction for multi-paragraph, realistic statements.

    Approach:
      - Split text into sentences.
      - Slide a window of up to 3 consecutive sentences and look for keywords/patterns
        that indicate situation, emotion, action, and motive.
      - Create one "statement" per event-like window when at least two entity types are found.

    This is intentionally lightweight (rule-based) so it doesn't add heavy NLP deps.
    """
    entities = []

    # Sentence split (keeps punctuation)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', statement_text.strip()) if s.strip()]

    # Keywords lists (mirror generator choices but tolerant)
    emotion_words = ["angry", "anxious", "calm", "nervous", "remorseful", "defensive", "distraught"]
    action_phrases = [
        "shouted at the officer",
        "refused to cooperate",
        "apologized repeatedly",
        "blamed his partner",
        "explained the plan calmly",
        "avoided eye contact",
        "sobbed quietly",
    ]
    motive_phrases = [
        "needed money",
        "wanted revenge",
        "acted impulsively",
        "was pressured by peers",
        "was afraid of consequences",
        "wanted recognition",
        "felt cornered",
    ]

    seen = set()

    for i in range(len(sentences)):
        # Combine up to 3 sentences to capture context
        window = ' '.join(sentences[i:i+3])

        situation = None
        emotion = None
        action = None
        motive = None

        # Situation: look for 'During <X>,' or 'During <X>.' or 'During <X> the' patterns
        sit_match = re.search(r"[Dd]uring\s+([^,.;]+)[,\.]", window)
        if sit_match:
            situation = sit_match.group(1).strip()
        else:
            # fallback: when/while
            sit_match = re.search(r"\b(when|while|in)\s+([^,.;]+)[,\.]", window, flags=re.I)
            if sit_match:
                situation = sit_match.group(2).strip()

        # Emotion
        emo_match = re.search(r"appeared\s+(\w+)", window, flags=re.I)
        if emo_match and emo_match.group(1).lower() in emotion_words:
            emotion = emo_match.group(1).lower()
        else:
            # look for 'seemed X' or 'was X'
            emo_match = re.search(r"\b(seemed|was)\s+(\w+)\b", window, flags=re.I)
            if emo_match and emo_match.group(2).lower() in emotion_words:
                emotion = emo_match.group(2).lower()

        # Action - look for known action phrases
        for a in action_phrases:
            if a in window:
                action = a
                break

        # Motive - look for explicit phrasings
        for m in motive_phrases:
            if m in window:
                motive = m
                break
        if not motive:
            # look for 'said he <...>' or 'mentioned he <...>'
            m_match = re.search(r"(?:said|mentioned) (?:that )?(?:he|the suspect)\s+([^.;,]+)", window, flags=re.I)
            if m_match:
                motive_candidate = m_match.group(1).strip()
                # keep short motives
                if len(motive_candidate.split()) <= 6:
                    motive = motive_candidate

        # If we found at least two entity types, add as an event
        found = {k: v for k, v in [('situation', situation), ('emotion', emotion), ('action', action), ('motive', motive)] if v}
        if len(found) >= 2:
            key = (situation or '') + '||' + (emotion or '') + '||' + (action or '') + '||' + (motive or '')
            if key not in seen:
                seen.add(key)
                entities.append({
                    'situation': situation or '',
                    'emotion': emotion or '',
                    'action': action or '',
                    'motive': motive or ''
                })

    return entities


def build_knowledge_graph(entities):
    G = nx.DiGraph()

    for idx, e in enumerate(entities):
        node_id = f"Statement_{idx+1}"
        G.add_node(node_id, label="Statement")
        G.add_node(e["situation"], label="Situation")
        G.add_node(e["emotion"], label="Emotion")
        G.add_node(e["action"], label="Action")
        G.add_node(e["motive"], label="Motive")

        G.add_edge(node_id, e["situation"], relation="happened_during")
        G.add_edge(node_id, e["emotion"], relation="showed_emotion")
        G.add_edge(node_id, e["action"], relation="performed_action")
        G.add_edge(node_id, e["motive"], relation="had_motive")

    return G


def create_dynamic_network():
    # Create a network with physics enabled
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#282a36",
        font_color="#f8f8f2",
        directed=True
    )
    
    # Configure physics for continuous random motion
    physics = {
        "enabled": True,
        "solver": "barnesHut",
        "barnesHut": {
            "gravitationalConstant": -2000,
            "centralGravity": 0.1,
            "springLength": 200,
            "springConstant": 0.04,
            "damping": 0.09,
            "avoidOverlap": 1
        },
        "minVelocity": 0.1,  # Lower minimum velocity to allow continued motion
        "maxVelocity": 10,    # Limit maximum velocity for smoother motion
        "stabilization": {
            "enabled": False  # Disable stabilization to allow continuous motion
        },
        "timestep": 0.2,     # Smaller timestep for smoother motion
        "adaptiveTimestep": True
    }
    
    # Configure other options
    options = {
        "nodes": {
            "shape": "dot",
            "borderWidth": 2,
            "borderWidthSelected": 3,
            "size": 25,
            "color": {
                "border": "#2b2b2b",
                "background": "#97c2fc"
            },
            "font": {"size": 14, "color": "#f8f8f2"},
            "shadow": {"enabled": True}
        },
        "edges": {
            "color": {"color": "rgba(255, 255, 255, 0.2)", "highlight": "#ffffff"},
            "width": 1,
            "smooth": {"type": "continuous"},
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}},
            "shadow": {"enabled": True}
        },
        "interaction": {
            "hover": True,
            "navigationButtons": True,
            "keyboard": True
        },
        "physics": physics
    }
    
    net.set_options(json.dumps(options))
    return net

def visualize_graph(G):
    # Create dynamic network
    net = create_dynamic_network()
    
    # Color scheme
    color_map = {
        'Statement': '#7C88FF',  # Bright blue
        'Situation': '#FFB86C',  # Soft orange
        'Emotion': '#50FA7B',    # Neon green
        'Action': '#FF5555',     # Soft red
        'Motive': '#BD93F9'      # Purple
    }
    
    # Add nodes
    for node, data in G.nodes(data=True):
        node_type = data.get('label', 'Unknown')
        is_root = node_type == 'Statement'
        
        # Calculate size based on connections
        size = 25 if is_root else 20
        
        # Format a friendly label for statement nodes so they show their number
        if isinstance(node, str) and node.startswith("Statement_"):
            parts = node.split("_", 1)
            label_text = f"{parts[0]} {parts[1]}" if len(parts) > 1 else node
        else:
            label_text = node

        # Add node with custom properties
        net.add_node(
            node,
            label=label_text,
            color=color_map.get(node_type, '#FFFFFF'),
            title=f"Type: {node_type}<br>Click to expand/collapse",
            size=size,
            mass=2 if is_root else 1,
            hidden=not is_root  # Only root nodes visible initially
        )
    
    # Add edges with custom styling
    for source, target, data in G.edges(data=True):
        net.add_edge(
            source,
            target,
            title=data.get('relation', ''),
            color={'color': 'rgba(255, 255, 255, 0.2)'},
            smooth={'type': 'continuous'}
        )
    
    # Add custom JavaScript for node expansion/collapse
    custom_js = """
    // Function to get connected nodes
    function getConnectedNodes(nodeId) {
        var connectedNodes = new Set();
        var edges = network.body.data.edges.get();
        edges.forEach(function(edge) {
            if (edge.from === nodeId) connectedNodes.add(edge.to);
            if (edge.to === nodeId) connectedNodes.add(edge.from);
        });
        return Array.from(connectedNodes);
    }
    
    // Add random motion to nodes
    function applyRandomForce() {
        var nodes = network.body.data.nodes.get();
        nodes.forEach(function(node) {
            if (!node.hidden) {
                var randomAngle = Math.random() * 2 * Math.PI;
                var randomMagnitude = Math.random() * 50;
                var forceX = randomMagnitude * Math.cos(randomAngle);
                var forceY = randomMagnitude * Math.sin(randomAngle);
                
                if (network.body.nodes[node.id]) {
                    var nodeObj = network.body.nodes[node.id];
                    if (nodeObj.options.fixed) return;  // Skip if node is fixed
                    
                    // Apply random force
                    nodeObj.setForce(forceX, forceY);
                }
            }
        });
    }
    
    // Continuous random motion
    setInterval(applyRandomForce, 1000);  // Apply random forces every second
    
    // Add slight wobble effect
    function addWobble() {
        var nodes = network.body.data.nodes.get();
        nodes.forEach(function(node) {
            if (!node.hidden) {
                var wobbleMagnitude = 5;
                var dx = (Math.random() - 0.5) * wobbleMagnitude;
                var dy = (Math.random() - 0.5) * wobbleMagnitude;
                
                if (network.body.nodes[node.id]) {
                    var nodeObj = network.body.nodes[node.id];
                    if (nodeObj.options.fixed) return;
                    
                    // Apply gentle wobble
                    nodeObj.x += dx;
                    nodeObj.y += dy;
                }
            }
        });
        network.redraw();
        requestAnimationFrame(addWobble);
    }
    
    // Start the wobble animation
    addWobble();
    
    // Handle node clicking for expand/collapse
    network.on("click", function(params) {
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0];
            var connectedNodes = getConnectedNodes(nodeId);
            var nodes = network.body.data.nodes.get();
            
            connectedNodes.forEach(function(connId) {
                var node = nodes.find(n => n.id === connId);
                if (node) {
                    network.body.data.nodes.update({
                        id: connId,
                        hidden: !node.hidden
                    });
                }
            });
        }
    });
    
    // Add smooth transitions when nodes appear/disappear
    network.on("beforeDrawing", function(ctx) {
        var nodes = network.body.nodes;
        for (var nodeId in nodes) {
            var node = nodes[nodeId];
            if (node.options.hidden) {
                if (typeof node.opacity === 'undefined') node.opacity = 1;
                node.opacity = Math.max(0, node.opacity - 0.1);
            } else {
                if (typeof node.opacity === 'undefined') node.opacity = 0;
                node.opacity = Math.min(1, node.opacity + 0.1);
            }
        }
    });
    """
    
    # Generate the HTML file
    html_path = Path.cwd() / "knowledge_graph.html"
    net.save_graph(str(html_path))
    
    # Inject custom CSS for dark theme
    with open(html_path, 'r') as f:
        content = f.read()
    
    dark_theme_css = """
    <style>
        body { background-color: #282a36; margin: 0; }
        #mynetwork {
            width: 100vw !important;
            height: 100vh !important;
            background-color: #282a36;
        }
    </style>
    """
    
    content = content.replace('</head>', f'{dark_theme_css}</head>')
    content = content.replace('</body>', f'<script>{custom_js}</script></body>')
    
    with open(html_path, 'w') as f:
        f.write(content)
    
    # Open in browser
    webbrowser.open(f'file://{html_path}')


if __name__ == "__main__":
    with open("criminal_statement.txt", "r") as f:
        text = f.read()

    entities = extract_entities(text)
    G = build_knowledge_graph(entities)
    visualize_graph(G)
    print("✅ Graph generated and displayed.")
