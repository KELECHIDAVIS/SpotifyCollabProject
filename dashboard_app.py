import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Spotify Collaboration Network", layout="wide")

# ─── Graph Loader ─────────────────────────────────────────────────────────────

def load_gexf_manual(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {'g': 'http://gexf.net/1.3'}

    attr_map = {}
    for attr in root.findall('.//g:attribute', ns):
        attr_map[attr.attrib['id']] = attr.attrib['title']

    G = nx.Graph()

    for node in root.findall('.//g:node', ns):
        node_id = node.attrib['id']
        attrs = {'label': node.attrib.get('label', node_id)}
        for attval in node.findall('.//g:attvalue', ns):
            title = attr_map.get(attval.attrib['for'])
            if title:
                attrs[title] = attval.attrib['value']
        pos_elem = node.find('g:position', ns)
        if pos_elem is not None:
            attrs['x'] = float(pos_elem.attrib['x'])
            attrs['y'] = float(pos_elem.attrib['y'])
        G.add_node(node_id, **attrs)

    for edge in root.findall('.//g:edge', ns):
        G.add_edge(edge.attrib['source'], edge.attrib['target'])

    return G

@st.cache_resource
def load_graphs():
    G_partial = load_gexf_manual("filtered_graph.gexf")
    G_full = load_gexf_manual("complete_graph.gexf")
    return G_partial, G_full

with st.spinner("Loading graphs..."):
    G_partial, G_full = load_graphs()

# ─── Layout ───────────────────────────────────────────────────────────────────

st.title("Spotify Artist Collaboration Network")
st.write("This network shows collaborations between artists whose songs made it to Spotify's weekly charts.")

tab1, tab2, tab3, tab4 = st.tabs([
    "Introduction",
    "Network Overview",
    "Artist Path Finder",
    "Genre Brokers",
])

# ─── Tab 1: Introduction ──────────────────────────────────────────────────────

with tab1:
    st.header("Introduction")

    st.markdown("""
    ### What is this?
    This dashboard explores a collaboration network built from Spotify's weekly chart data.
    Each **node** is an artist. Each **edge** connects two artists who have collaborated on
    a charting song. The network spans **148,380 artists** and **296,763 collaborations**
    across 70+ countries.

    ### Research Questions
    - Do music collaborations exhibit **six degrees of separation**?
    - Which artists serve as **bridges between genres**?
    """)

    st.divider()

    # Key stats row
    st.subheader("Key Network Statistics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Artists", "156,326")
    c2.metric("Total Collaborations", "300,386")
    c3.metric("Avg. Shortest Path", "6.18 hops")
    c4.metric("Six Degrees?", "Yes")

    st.caption(
        "The average shortest path of 6.18 hops across 148,380 artists closely matches "
        "the classical six degrees of separation hypothesis."
    )

    st.divider()

    # Genre pie chart
    st.subheader("Genre Breakdown (Full Network)")
    st.write(
        "Nodes are assigned to broad genre communities detected via modularity analysis in Gephi. "
        "Hip Hop and its regional variants dominate the network, while Electronic artists "
        "are a small community but disproportionately central as brokers."
    )

    genre_counts = {
        "Electronic": 23931,
        "Latin": 13765,
        "Hip Hop": 12826,
        "Brazilian Funk": 8500,
        "Classical/Misc": 6943,
        "Bollywood": 6563,
        "Scandinavian Hip Hop": 5757,
        "German Hip Hop": 5702,
        "French Hip Hop": 4524,
        "Dutch Hip Hop": 3802,
        "European Dance Pop": 3802,
        "Italian Hip Hop": 3275,
        "Romanian Pop": 3125,
        "Russian Hip Hop": 3096,
        "Southeast Asian": 3069,
        "South African Pop": 2983,
        "Polish Hip Hop": 2796,
        "Traditional Pop": 2788,
        "Turkish Hip Hop": 2364,
        "C-Pop": 2248,
        "Finnish Hip Hop": 2243,
        "Czech Hip Hop": 2120,
        "V-Pop": 2045,
        "Greek Hip Hop": 2032,
        "K-Pop": 1836,
        "J-Pop": 1680,
        "Thai Hip Hop": 1587,
        "Egyptian/Arab Pop": 1569,
        "Israeli Pop": 1482,
        "Portuguese Hip Hop": 1471,
        "Latvian/Lithuanian Pop": 1252,
        "Other": 7204,   # 148380 - 141176
    }

    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1])
    labels = [g[0] for g in sorted_genres]
    values = [g[1] for g in sorted_genres]
    total = sum(values)

    fig_bar = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        text=[f"{v/total*100:.1f}%" for v in values],
        textposition='outside',
        marker=dict(
            color=values,
            colorscale='Tealgrn',
            showscale=False,
        )
    ))
    fig_bar.update_layout(
        template='plotly_dark',
        height=750,
        margin=dict(t=20, b=20, l=180, r=80),
        xaxis=dict(title="Number of Artists", showgrid=True),
        yaxis=dict(title="", tickfont=dict(size=12)),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ─── Tab 2: Network Overview ──────────────────────────────────────────────────

with tab2:
    st.header("Network Overview")
    st.write("Visualization coming next.")

# ─── Tab 3: Artist Path Finder ────────────────────────────────────────────────

with tab3:
    st.header("Artist Path Finder")
    st.write("Interactive feature coming next.")

# ─── Tab 4: Genre Brokers ─────────────────────────────────────────────────────

with tab4:
    st.header("Genre Brokers")
    st.write("Betweenness centrality table coming next.")