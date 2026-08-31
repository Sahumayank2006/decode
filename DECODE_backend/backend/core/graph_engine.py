"""
DECODE – Graph Extraction Engine
Builds a knowledge graph from document entities and their co-occurrence /
dependency relationships. Exports as JSON, adjacency list, or base64 PNG.
"""

import io
import logging
import base64
import re
from collections import defaultdict, Counter
from itertools import combinations

import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

logger = logging.getLogger("decode.graph")

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


# ─────────────────────────────────────────────────────────────────────────────
# Entity co-occurrence graph
# ─────────────────────────────────────────────────────────────────────────────

ENTITY_COLORS = {
    "PERSON": "#4e79a7",
    "ORG": "#f28e2b",
    "GPE": "#59a14f",
    "LOC": "#76b7b2",
    "DATE": "#e15759",
    "MONEY": "#b07aa1",
    "PRODUCT": "#ff9da7",
    "EVENT": "#9c755f",
    "WORK_OF_ART": "#bab0ac",
    "LAW": "#d37295",
    "NORP": "#499894",
    "DEFAULT": "#aaaaaa",
}


def build_cooccurrence_graph(text: str,
                              window: int = 5,
                              min_freq: int = 1,
                              max_nodes: int = 80) -> nx.Graph:
    """
    Build entity co-occurrence graph.
    Two entities are connected if they appear within `window` sentences.
    """
    nlp = _get_nlp()
    # Chunk text to avoid spaCy's max length limit
    chunk_size = 100_000
    text = text[:500_000]

    G = nx.Graph()
    edge_weights: dict[tuple, int] = defaultdict(int)
    node_types: dict[str, str] = {}
    node_freq: Counter = Counter()

    # Process in chunks
    for start in range(0, len(text), chunk_size):
        chunk = text[start:start + chunk_size]
        doc = nlp(chunk)
        sentences = list(doc.sents)

        for i, sent in enumerate(sentences):
            # Entities in this sentence
            ents_in_sent = [ent for ent in sent.ents if len(ent.text.strip()) > 1]

            # Look-ahead window
            window_ents = ents_in_sent[:]
            for j in range(1, window):
                if i + j < len(sentences):
                    window_ents += [e for e in sentences[i + j].ents]

            for ent in ents_in_sent:
                name = ent.text.strip()
                node_types[name] = ent.label_
                node_freq[name] += 1
                if not G.has_node(name):
                    G.add_node(name, label=ent.label_, freq=1)
                else:
                    G.nodes[name]["freq"] = G.nodes[name].get("freq", 0) + 1

            # Co-occurrence edges
            for e1, e2 in combinations(window_ents, 2):
                n1, n2 = e1.text.strip(), e2.text.strip()
                if n1 != n2:
                    key = tuple(sorted([n1, n2]))
                    edge_weights[key] += 1

    # Filter low-frequency nodes
    low_freq = [n for n, f in node_freq.items() if f < min_freq]
    G.remove_nodes_from(low_freq)

    # Add edges
    for (n1, n2), weight in edge_weights.items():
        if G.has_node(n1) and G.has_node(n2):
            G.add_edge(n1, n2, weight=weight)

    # Trim to max_nodes (keep highest-degree nodes)
    if G.number_of_nodes() > max_nodes:
        degree_sorted = sorted(G.degree(), key=lambda x: x[1], reverse=True)
        keep = {n for n, _ in degree_sorted[:max_nodes]}
        remove = [n for n in G.nodes() if n not in keep]
        G.remove_nodes_from(remove)

    logger.info("Graph built: %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())
    return G, node_types


def build_dependency_graph(text: str, max_nodes: int = 60) -> nx.DiGraph:
    """
    Build a directed dependency graph from subject-verb-object triples.
    """
    nlp = _get_nlp()
    DG = nx.DiGraph()

    doc = nlp(text[:50_000])

    for token in doc:
        if token.dep_ in ("nsubj", "nsubjpass", "dobj", "attr", "pobj"):
            head = token.head.text
            dep = token.text
            rel = token.dep_

            if not DG.has_node(head):
                DG.add_node(head, pos=token.head.pos_)
            if not DG.has_node(dep):
                DG.add_node(dep, pos=token.pos_)
            DG.add_edge(head, dep, relation=rel)

    # Trim
    if DG.number_of_nodes() > max_nodes:
        degree_sorted = sorted(DG.degree(), key=lambda x: x[1], reverse=True)
        keep = {n for n, _ in degree_sorted[:max_nodes]}
        remove = [n for n in DG.nodes() if n not in keep]
        DG.remove_nodes_from(remove)

    return DG


# ─────────────────────────────────────────────────────────────────────────────
# Graph analytics
# ─────────────────────────────────────────────────────────────────────────────

def graph_analytics(G: nx.Graph) -> dict:
    """Compute centrality and community metrics."""
    if G.number_of_nodes() == 0:
        return {"nodes": 0, "edges": 0}

    analytics = {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "density": round(nx.density(G), 4),
        "is_connected": nx.is_connected(G),
    }

    if G.number_of_nodes() > 1:
        try:
            analytics["average_clustering"] = round(nx.average_clustering(G), 4)
        except Exception:
            pass

        # Centrality (top 10)
        deg_centrality = nx.degree_centrality(G)
        analytics["top_nodes_by_degree"] = [
            {"node": n, "centrality": round(c, 4)}
            for n, c in sorted(deg_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        try:
            bet = nx.betweenness_centrality(G, k=min(50, G.number_of_nodes()))
            analytics["top_nodes_by_betweenness"] = [
                {"node": n, "betweenness": round(c, 4)}
                for n, c in sorted(bet.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
        except Exception:
            pass

        # Communities
        try:
            from networkx.algorithms.community import greedy_modularity_communities
            communities = list(greedy_modularity_communities(G))
            analytics["communities"] = [
                {"id": i, "members": list(c)[:10]}
                for i, c in enumerate(communities[:10])
            ]
            analytics["community_count"] = len(communities)
        except Exception:
            pass

    return analytics


# ─────────────────────────────────────────────────────────────────────────────
# Visualization
# ─────────────────────────────────────────────────────────────────────────────

def _node_colors(G: nx.Graph, node_types: dict) -> list:
    colors = []
    for node in G.nodes():
        nt = node_types.get(node, "DEFAULT")
        colors.append(ENTITY_COLORS.get(nt, ENTITY_COLORS["DEFAULT"]))
    return colors


def render_graph_png(G: nx.Graph,
                     node_types: dict = None,
                     layout: str = "spring",
                     title: str = "Knowledge Graph",
                     figsize: tuple = (14, 10)) -> str:
    """
    Render the graph as a PNG and return it as a base64-encoded string.
    """
    if G.number_of_nodes() == 0:
        return ""

    fig, ax = plt.subplots(figsize=figsize, facecolor="#0f0f0f")
    ax.set_facecolor("#1a1a2e")
    ax.set_title(title, color="white", fontsize=14, pad=15)

    # Layout
    layout_fns = {
        "spring": lambda: nx.spring_layout(G, seed=42, k=0.8),
        "kamada_kawai": lambda: nx.kamada_kawai_layout(G),
        "circular": lambda: nx.circular_layout(G),
        "spectral": lambda: nx.spectral_layout(G),
        "shell": lambda: nx.shell_layout(G),
    }
    pos = layout_fns.get(layout, layout_fns["spring"])()

    node_colors = _node_colors(G, node_types or {}) if node_types is not None else "#4e79a7"

    # Edge weights
    weights = [G[u][v].get("weight", 1) for u, v in G.edges()]
    max_w = max(weights) if weights else 1
    edge_widths = [0.5 + 2.5 * (w / max_w) for w in weights]

    nx.draw_networkx_edges(G, pos, ax=ax, width=edge_widths,
                           alpha=0.4, edge_color="#888888")
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=400, alpha=0.9)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=7,
                            font_color="white", font_weight="bold")

    # Legend
    if node_types:
        unique_types = set(node_types.values())
        legend_patches = [
            plt.Line2D([0], [0], marker='o', color='w',
                       markerfacecolor=ENTITY_COLORS.get(t, ENTITY_COLORS["DEFAULT"]),
                       label=t, markersize=8)
            for t in sorted(unique_types)
        ]
        ax.legend(handles=legend_patches, loc="upper left",
                  facecolor="#333333", labelcolor="white", fontsize=7)

    ax.axis("off")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Graph → serialisable dict
# ─────────────────────────────────────────────────────────────────────────────

def graph_to_dict(G: nx.Graph, node_types: dict = None) -> dict:
    """Convert NetworkX graph to JSON-serialisable dict."""
    nodes = []
    for node in G.nodes(data=True):
        name = node[0]
        attrs = node[1]
        nodes.append({
            "id": name,
            "label": node_types.get(name, "UNKNOWN") if node_types else attrs.get("label", "UNKNOWN"),
            "freq": attrs.get("freq", 1),
            "degree": G.degree(name),
        })

    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({
            "source": u,
            "target": v,
            "weight": data.get("weight", 1),
        })

    return {"nodes": nodes, "edges": edges}


# ─────────────────────────────────────────────────────────────────────────────
# Full graph pipeline
# ─────────────────────────────────────────────────────────────────────────────

def run_graph_pipeline(text: str,
                       render: bool = True,
                       layout: str = "spring") -> dict:
    """
    Run the complete graph extraction pipeline.
    Returns: nodes, edges, analytics, and base64 PNG image.
    """
    logger.info("Graph pipeline start")

    G, node_types = build_cooccurrence_graph(text, window=5, min_freq=1, max_nodes=80)

    result = {
        "graph_data": graph_to_dict(G, node_types),
        "analytics": graph_analytics(G),
        "image_base64": "",
    }

    if render and G.number_of_nodes() > 0:
        result["image_base64"] = render_graph_png(G, node_types, layout=layout)

    logger.info("Graph pipeline done: %d nodes, %d edges",
                G.number_of_nodes(), G.number_of_edges())
    return result
