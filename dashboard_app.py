import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Spotify Collaboration Network", layout="wide")

# ─── Graph Loader ─────────────────────────────────────────────────────────────

def load_gexf_manual(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {
        'g': 'http://gexf.net/1.3',
        'viz': 'http://gexf.net/1.3/viz'
    }

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

        # Handle both viz:position (complete_graph) and bare position (filtered_graph)
        pos_elem = node.find('viz:position', ns)
        if pos_elem is None:
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
    c1.metric("Total Artists", "148,380")
    c2.metric("Total Collaborations", "296,763")
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
    st.plotly_chart(fig_bar, width='stretch')

# ─── Shared color maps ────────────────────────────────────────────────────────

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

def build_network_figure(G, genre_color_map):
    node_x, node_y, node_text, node_size, node_colors = [], [], [], [], []

    for node, data in G.nodes(data=True):
        node_x.append(data.get('x', 0))
        node_y.append(data.get('y', 0))

        genre_str = data.get('Genre', 'Other')
        node_colors.append(genre_color_map.get(genre_str, "#C0C0C0"))

        degree = int(float(data.get('Total Degree', 1)))
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
            sizeref=2. * max_degree / (30**2),
            line=dict(width=node_border_widths),
            opacity=1.0
        )
    )

    edge_groups = {color: {'x': [], 'y': []} for color in genre_color_map.values()}
    for edge in G.edges():
        x0 = G.nodes[edge[0]].get('x', 0)
        y0 = G.nodes[edge[0]].get('y', 0)
        x1 = G.nodes[edge[1]].get('x', 0)
        y1 = G.nodes[edge[1]].get('y', 0)
        genre = G.nodes[edge[0]].get('Genre', 'Other')
        color = genre_color_map.get(genre, "#C0C0C0")
        edge_groups[color]['x'].extend([x0, x1, None])
        edge_groups[color]['y'].extend([y0, y1, None])

    edge_traces = []
    for color, coords in edge_groups.items():
        if coords['x']:
            edge_traces.append(go.Scatter(
                x=coords['x'], y=coords['y'],
                line=dict(width=0.3, color=color),
                hoverinfo='none',
                mode='lines',
                opacity=0.000001 if color == "#C0C0C0" else 1.0,
                showlegend=False
            ))

    legend_traces = [
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color),
            legendgroup=genre,
            showlegend=True,
            name=genre
        )
        for genre, color in genre_color_map.items()
    ]

    fig = go.Figure(
        data=edge_traces + [node_trace] + legend_traces,
        layout=go.Layout(
            height=900,
            template='plotly_dark',
            showlegend=True,
            legend=dict(yanchor="middle", y=0.5, xanchor="left", x=1.01),
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       scaleanchor="x", scaleratio=1)
        )
    )
    return fig

# ─── Tab 2: Network Overview ──────────────────────────────────────────────────

with tab2:
    st.header("Network Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Nodes", G_full.number_of_nodes())
    c2.metric("Edges", G_full.number_of_edges())
    c3.metric("Genre Communities", len(complete_genre_color_map) - 1)

    st.divider()

    view_option = st.radio(
        "Select graph view:",
        ["Top 1% by Degree (fast)", "Full Network (slow)"],
        horizontal=True
    )

    if view_option == "Top 1% by Degree (fast)":
        st.markdown(
            "Showing the top ~1% of artists by degree (50+ collaborations). "
            "Node size reflects total degree. Colors represent genre communities."
        )
        with st.spinner("Rendering graph..."):
            fig = build_network_figure(G_partial, partial_genre_color_map)
        st.plotly_chart(fig, width='stretch')
    else:
        st.markdown(
            "Showing the full collaboration network with all 148,380 artists. "
            "This may take a moment to render."
        )
        with st.spinner("Rendering full graph -- this may take a while..."):
            fig = build_network_figure(G_full, complete_genre_color_map)
        st.plotly_chart(fig, width='stretch')

# ─── Tab 3: Artist Path Finder ────────────────────────────────────────────────

@st.cache_data
def build_name_index(_G):
    """Build lowercase name -> node_id map and sorted name list for fuzzy matching."""
    name_to_id = {}
    for node_id, data in _G.nodes(data=True):
        name = data.get('name', '').strip()
        if name:
            name_to_id[name.lower()] = node_id
    return name_to_id, sorted(name_to_id.keys())

def fuzzy_find(query, name_to_id, all_names):
    """Return (node_id, matched_name) or (None, None) if no close match."""
    q = query.strip().lower()
    if q in name_to_id:
        return name_to_id[q], q
    import difflib
    matches = difflib.get_close_matches(q, all_names, n=1, cutoff=0.6)
    if matches:
        return name_to_id[matches[0]], matches[0]
    return None, None

with tab3:
    st.header("Artist Path Finder")

    st.markdown("""
    Type in any two artists and this tool finds the shortest collaboration path between them.
    Our network has an average shortest path of **6.18 hops** -- nearly identical to the
    classical six degrees of separation. Try it for yourself!

    > **Tip:** Use the artist's name as it appears on Spotify. Slight misspellings are handled automatically.
    """)

    name_to_id, all_names = build_name_index(G_full)

    col1, col2 = st.columns(2)
    with col1:
        artist_a = st.text_input("First artist", placeholder="e.g. Diplo")
    with col2:
        artist_b = st.text_input("Second artist", placeholder="e.g. Beyoncé")

    if st.button("Find Path", type="primary"):
        if not artist_a or not artist_b:
            st.warning("Please enter both artist names.")
        else:
            id_a, matched_a = fuzzy_find(artist_a, name_to_id, all_names)
            id_b, matched_b = fuzzy_find(artist_b, name_to_id, all_names)

            if id_a is None:
                st.error(f"Could not find an artist matching **{artist_a}** in the network.")
            elif id_b is None:
                st.error(f"Could not find an artist matching **{artist_b}** in the network.")
            else:
                # Show fuzzy match corrections
                if matched_a != artist_a.strip().lower():
                    st.info(f"Interpreted **{artist_a}** as **{matched_a.title()}**")
                if matched_b != artist_b.strip().lower():
                    st.info(f"Interpreted **{artist_b}** as **{matched_b.title()}**")

                try:
                    path = nx.shortest_path(G_full, id_a, id_b)
                    hops = len(path) - 1

                    if hops == 0:
                        st.success("These are the same artist!")
                    else:
                        st.success(
                            f"Found a path of **{hops} hop{'s' if hops != 1 else ''}** -- "
                            f"{'well within' if hops <= 6 else 'just above'} six degrees of separation!"
                        )

                        st.markdown("#### Collaboration Chain")
                        for i, node_id in enumerate(path):
                            data = G_full.nodes[node_id]
                            name = data.get('name', node_id)
                            genre = data.get('Genre', 'Unknown')
                            color = complete_genre_color_map.get(genre, '#C0C0C0')
                            if i == 0:
                                label = "START"
                            elif i == len(path) - 1:
                                label = "END"
                            else:
                                label = f"Hop {i}"

                            st.markdown(
                                f"<div style='padding:10px; margin:4px 0; border-left: 4px solid {color}; "
                                f"background:#1e1e1e; border-radius:4px;'>"
                                f"<span style='color:#aaa; font-size:12px'>{label}</span><br>"
                                f"<span style='font-size:18px; font-weight:bold'>{name}</span> "
                                f"<span style='color:{color}; font-size:13px'>● {genre}</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            if i < len(path) - 1:
                                st.markdown(
                                    "<div style='text-align:center; color:#555; font-size:20px'>↓ collaborated with</div>",
                                    unsafe_allow_html=True
                                )

                        st.caption(
                            f"The average shortest path in this network is 6.18 hops. "
                            f"Your result of {hops} hop{'s' if hops != 1 else ''} "
                            f"{'supports' if hops <= 7 else 'is an outlier to'} the small world hypothesis."
                        )

                except nx.NetworkXNoPath:
                    st.error(
                        "No path found between these two artists. "
                        "They may be in disconnected parts of the network."
                    )

# ─── Tab 4: Genre Brokers ─────────────────────────────────────────────────────

@st.cache_data
def get_top_brokers(_G, n=20):
    rows = []
    for node_id, data in _G.nodes(data=True):
        bc = data.get('Betweenness Centrality')
        name = data.get('name', node_id)
        genre = data.get('Genre', 'Other')
        degree = data.get('Total Degree', 0)
        if bc is not None and name:
            rows.append({
                'Artist': name,
                'Genre': genre,
                'Betweenness Centrality': float(bc),
                'Total Degree': int(float(degree)),
            })
    rows.sort(key=lambda x: x['Betweenness Centrality'], reverse=True)
    return rows[:n]

with tab4:
    st.header("Genre Brokers")

    st.markdown("""
    **Betweenness centrality** measures how often an artist appears on the shortest path
    between two other artists. High betweenness means the artist acts as a bridge --
    remove them and many collaboration chains break.

    Our key finding: despite Electronic music representing only **4.07%** of the network,
    EDM producers dominate the top brokers list. Genre-fluid producers like Diplo, R3HAB,
    and David Guetta routinely collaborate across Hip Hop, Pop, Latin, and R&B -- making
    them the connective tissue of the global music industry.
    """)

    st.divider()

    brokers = get_top_brokers(G_partial, n=20)

    # Controls
    top_n = st.slider("Number of artists to show", min_value=5, max_value=20, value=10, step=1)
    brokers_subset = brokers[:top_n]

    # Bar chart
    names = [r['Artist'] for r in brokers_subset]
    bc_vals = [r['Betweenness Centrality'] for r in brokers_subset]
    genres = [r['Genre'] for r in brokers_subset]
    colors = [complete_genre_color_map.get(g, '#C0C0C0') for g in genres]

    fig_brokers = go.Figure(go.Bar(
        x=bc_vals[::-1],
        y=names[::-1],
        orientation='h',
        marker=dict(color=colors[::-1]),
        text=genres[::-1],
        textposition='inside',
        hovertemplate='<b>%{y}</b><br>Betweenness: %{x:,.0f}<br>Genre: %{text}<extra></extra>',
    ))
    fig_brokers.update_layout(
        template='plotly_dark',
        height=max(400, top_n * 45),
        margin=dict(t=20, b=40, l=20, r=20),
        xaxis=dict(title="Betweenness Centrality", showgrid=True),
        yaxis=dict(title="", tickfont=dict(size=12)),
    )
    st.plotly_chart(fig_brokers, width='stretch')

    st.caption(
        "Bar color reflects the artist's genre community. "
        "Notice how Electronic (blue) dominates despite being a small fraction of the total network."
    )

    st.divider()

    # Table
    st.subheader("Full Rankings Table")
    import pandas as pd
    if brokers_subset:
        df = pd.DataFrame(brokers_subset)
        df.index = range(1, len(df) + 1)
        df['Betweenness Centrality'] = df['Betweenness Centrality'].apply(lambda x: f'{x:,.0f}')
        df['Total Degree'] = df['Total Degree'].apply(lambda x: f'{x:,}')
        st.dataframe(df, width='stretch')
    else:
        st.warning("No broker data found. Make sure the graph loaded correctly.")

    st.markdown("""
    #### Why EDM Producers?
    Electronic music producers operate differently from artists in genre-specific scenes.
    A Hip Hop artist typically collaborates within Hip Hop. An EDM producer releases
    tracks featuring artists from every genre. One week a Latin singer, the next a
    K-Pop idol, the next an R&B vocalist. This genre-fluid workflow places them on the
    shortest path between communities that would otherwise be far apart, giving them
    outsized centrality relative to their community size.
    """)