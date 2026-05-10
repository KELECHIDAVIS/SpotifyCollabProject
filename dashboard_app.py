import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(page_title="Collaboration Network Dashboard", layout="wide")

@st.cache_data
def load_partial_graph_with_positions():
    G = nx.read_gexf("filtered_graph.gexf")
    
    pos = {}
    for node, data in G.nodes(data=True):
        viz = data.get('viz', {})
        x = viz.get('position', {}).get('x', 0)
        y = viz.get('position', {}).get('y', 0)
        pos[node] = (float(x), float(y))
    
    return G, pos

G_partial, pos_partial = load_partial_graph_with_positions() # From filtered_graph.gexf

@st.cache_data
def load_complete_graph_with_positions():
    G = nx.read_gexf("complete_graph.gexf")
    
    pos = {}
    for node, data in G.nodes(data=True):
        viz = data.get('viz', {})
        x = viz.get('position', {}).get('x', 0)
        y = viz.get('position', {}).get('y', 0)
        pos[node] = (float(x), float(y))
    
    return G, pos

G, pos = load_complete_graph_with_positions() # From complete_graph.gexf

largest_cc = max(nx.connected_components(G), key=len)

# Get GCC from complete graph
gcc = G.subgraph(largest_cc).copy()

partial_genre_color_map = {
    "Electronic": "#00C4FF",
    "Latin": "#FF683C",
    "Hip Hop": "#2CD500",
    "Brazilian Funk": "#FF7BFF",
    "Classical/Misc": "#DDBE65",
    "Bollywood": "#FF65A1",
    "UK Hip Hop/South African Pop": "#D04B3C",
    "Dutch Hip Hop": "#E27339",
    "French Hip Hop": "#00008B",
    "Polish/Czech Hip Hop": "#C72E26",
    "German Hip Hop": "#F5CD46",
    "Italian Hip Hop": "#7F3841",
    "K-Pop": "#A491EF",
    "Other": "#C0C0C0"
}

complete_genre_color_map = {
    "Electronic": "#00C4FF",
    "Latin": "#FF683C",
    "Hip Hop": "#2CD500",
    "Brazilian Funk": "#FF7BFF",
    "Classical/Misc": "#DDBE65",
    "Bollywood": "#FF65A1",
    "Scandinavian Hip Hop": "#DDBE65",
    "German Hip Hop": "#F5CD46",
    "French Hip Hop": "#00008B",
    "Dutch Hip Hop": "#E27339",
    "European Dance Pop": "#FF3179",
    "Italian Hip Hop": "#40904E",
    "Romanian Pop": "#2D6072",
    "Russian Hip Hop": "#67B3B7",
    "Southeast Asian": "#D2436D",
    "South African Pop": "#D04B3C",
    "Polish Hip Hop": "#C72E26",
    "Traditional Pop": "#B395A3",
    "Turkish Hip Hop": "#965F29",
    "C-Pop": "#F13B34",
    "Finnish Hip Hop": "#0F2E68",
    "Czech Hip Hop": "#009270",
    "V-Pop": "#2F6D34",
    "Greek Hip Hop": "#1C44B7",
    "K-Pop": "#A491EF",
    "J-Pop": "#FF92FF",
    "Thai Hip Hop": "#FF8092",
    "Egyptian/Arab Pop": "#F2B460",
    "Israeli Pop": "#3273B3",
    "Portuguese Hip Hop": "#9BC2BE",
    "Latvian/Lithuanian Pop": "#92393C",
    "Other": "#C0C0C0"
}

def build_network_figure(G, pos, graph_size, genre_color_map=complete_genre_color_map):
    node_x, node_y, node_text = [], [], []
    node_size = []
    node_colors = []

    for node, data in G.nodes(data=True):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        genre_str = data.get('Genre', 'Other')
        node_colors.append(genre_color_map[genre_str])
        
        degree = int(data.get('Total Degree', 1))
        artist_name = data.get('name', node)
        
        node_size.append(degree)
        node_text.append(
            f"<b>{artist_name}</b><br>"
            f"Genre: {genre_str}<br>"
            f"Degree: {degree}"
        )

    max_degree = max(node_size) if node_size else 1
    node_border_widths = [((d / max_degree) * 2) + 0.5 for d in node_size]

    node_trace = go.Scatter(
        x=node_x, y=node_y, 
        mode='markers', 
        hoverinfo='text', 
        text=node_text,
        showlegend=False,
        marker=dict(
            color=node_colors,
            size=node_size,
            sizemode='area',
            sizeref=2. * max(node_size) / (30**2),
            line=dict(
                width=node_border_widths,
            ),
            opacity=1.0
        )
    )

    edge_groups = {color: {'x': [], 'y': []} for color in genre_color_map.values()}

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        start_node_genre = G.nodes[edge[0]].get('Genre', 'Other')
        color = genre_color_map.get(start_node_genre, "#C0C0C0")
        
        edge_groups[color]['x'].extend([x0, x1, None])
        edge_groups[color]['y'].extend([y0, y1, None])

    edge_traces = []
    for color, coords in edge_groups.items():
        if coords['x']:
            # Make edges from "Other" much less visible
            trace_opacity = 0.000001 if color == "#C0C0C0" else 1.0

            trace = go.Scatter(
                x=coords['x'], y=coords['y'],
                line=dict(width=0.3, color=color),
                hoverinfo='none',
                mode='lines',
                opacity=trace_opacity,
                showlegend=False
            )
            edge_traces.append(trace)

    legend_traces = []
    for genre, color in genre_color_map.items():
        legend_traces.append(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=color),
            legendgroup=genre,
            showlegend=True,
            name=genre
        ))

    fig = go.Figure(
        data=edge_traces + [node_trace] + legend_traces,
        layout=go.Layout(
            width=graph_size,
            height=graph_size,
            template='plotly_dark',
            showlegend=True,
            legend=dict(
                yanchor="middle",
                y=0.6,
                xanchor="left",
                x=1.02,
            ),
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1)
        )
    )

    return fig

st.title("Spotify Artist Collaboration Network")
st.write("This network shows collaborations between artists whose songs made it to Spotify's weekly charts.")

tab1, tab2, tab3, tab4 = st.tabs([
    "Introduction",
    "Overview",
    "Artist Path Finder",
    "Genre Brokers",
])

with tab1:
    st.header("Introduction")

    st.markdown("""
    ### Research Questions
    - Do music collaborations show **six degrees of separation**?
    - Which artists serve as **brokers between genres**?
    """)

    st.markdown("""
    ##### This figure shows the top ~1% of nodes (*50+ degrees*) from the total network:
    """)

    fig_partial = build_network_figure(G_partial, pos_partial, 1000, partial_genre_color_map)
    fig_partial.update_yaxes(range=[-1000, 500])
    st.plotly_chart(fig_partial, width="content")

with tab2:
    st.header("Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Nodes", G.number_of_nodes())
    c2.metric("Edges", G.number_of_edges())
    c3.metric("Communities", len(complete_genre_color_map) - 1)

    with st.spinner("Loading graph..."):
        fig = build_network_figure(G, pos, 1000, complete_genre_color_map)
        
    with st.spinner("Rendering..."):
        st.plotly_chart(fig, width="stretch")

    

with tab3:
    st.header("Artist Path Finder")

with tab4:
    st.header("Genre Brokers")

