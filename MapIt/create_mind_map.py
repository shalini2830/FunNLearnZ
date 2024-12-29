import networkx as nx
import matplotlib.pyplot as plt

def create_mind_map(headings, subheadings):
    G = nx.Graph()
    G.add_node("Main Concept")

    # Add main headings and subheadings
    for heading in headings:
        G.add_node(heading)
        G.add_edge("Main Concept", heading)
        
        # Add related subheadings to each main heading
        for subheading in subheadings:
            if heading.lower() in subheading.lower():  # simple matching condition
                G.add_node(subheading)
                G.add_edge(heading, subheading)
    
    plt.figure(figsize=(12, 10))
    nx.draw(G, with_labels=True, node_size=3000, node_color="lightgreen", font_size=10, font_weight="bold", edge_color="gray")
    plt.title("Concept Map")
    plt.savefig("static/mind_map.png")  # Save the mind map image
