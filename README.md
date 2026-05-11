# Spotify Artist Collaboration Network Dashboard

**CS 4230 — Information Networks**
**Team Members:** Jacob Buck, Kelechi Duru, Jayden Nguyen

---

## Overview

This dashboard explores a collaboration network built from Spotify's weekly chart data.
Each node is an artist and each edge connects two artists who have collaborated on a
charting song. The network spans 156326 artists and 300386 collaborations across 70+
countries. The dashboard investigates two research questions:

- Do music collaborations exhibit six degrees of separation?
- Which artists serve as bridges between genre communities?

---

## Project Structure

```
spotify_collabs/
├── dashboard_app.py        # Main Streamlit application
├── requirements.txt        # Python dependencies
├── filtered_graph.gexf     # Top 1% of nodes by degree (on GitHub)
└── complete_graph.gexf     # Full network — see note below
```

### Important Note on Data Files

`filtered_graph.gexf` (the top ~1% of artists by degree, ~4MB) is included in the
GitHub repository and in this zip folder.

`complete_graph.gexf` (the full 148,380-node network, ~125MB) **exceeds GitHub's 100MB
file size limit** and could not be hosted there. It is included in the submitted zip
folder alongside the source code. If you cloned the repository rather than using the
zip, you will need to obtain `complete_graph.gexf` separately and place it in the same
directory as `dashboard_app.py` before running the app.

Both `.gexf` files must be present in the same directory as `dashboard_app.py` for the
dashboard to run correctly.

---

## Setup and Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Step 1 — Clone or unzip the project

If using the submitted zip file, extract it to a folder of your choice:

```bash
unzip spotify_collabs.zip
cd spotify_collabs
```

If cloning from GitHub (note: you will still need `complete_graph.gexf` from the zip):

```bash
git clone https://github.com/KELECHIDAVIS/SpotifyCollabProject.git
cd SpotifyCollabProject/spotify_collabs
```

### Step 2 — Create a virtual environment

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Confirm data files are present

Make sure both graph files are in the same directory as `dashboard_app.py`:

```bash
ls *.gexf
# Should show:
# complete_graph.gexf
# filtered_graph.gexf
```

If `complete_graph.gexf` is missing, copy it from the submitted zip folder into this
directory before proceeding.

### Step 5 — Run the dashboard

```bash
streamlit run dashboard_app.py
```

The app will open automatically in your browser at `http://localhost:8501`.
The first load takes ~15-30 seconds while both graphs are parsed and cached.
Subsequent interactions are fast.

---

## Dashboard Tabs

| Tab | Description |
|-----|-------------|
| Introduction | Project background, research questions, key stats, genre breakdown chart |
| Network Overview | Interactive Plotly visualization of the collaboration network, togglable between the top 1% view (fast) and the full network (slow) |
| Artist Path Finder | Enter any two artist names to find the shortest collaboration chain between them. Supports fuzzy name matching for slight misspellings |
| Genre Brokers | Top artists by betweenness centrality with bar chart and ranked table, with analysis of why EDM producers dominate |

---

## Dependencies

All dependencies are listed in `requirements.txt`. Key packages:

| Package | Purpose |
|---------|---------|
| streamlit | Dashboard framework |
| networkx | Graph data structure and shortest path algorithm |
| plotly | Interactive network and chart visualizations |
| pandas | Data table rendering |
| difflib | Fuzzy artist name matching (standard library, no install needed) |

### Note on NetworkX and GEXF

NetworkX 3.3+ has a known bug where it fails to parse GEXF 1.3 files exported by
Gephi, throwing `No <graph> element in GEXF file` regardless of the file's validity.
This dashboard works around the issue entirely by using Python's built-in
`xml.etree.ElementTree` to parse the `.gexf` files and manually construct NetworkX
graph objects. No downgrade of NetworkX is required.

---

## Troubleshooting

**App crashes on startup with a file not found error**
Make sure both `filtered_graph.gexf` and `complete_graph.gexf` are in the same
directory as `dashboard_app.py`. See the data files note above.

**Full network view is very slow or crashes the browser**
The full network has 148,380 nodes and 296,763 edges. Rendering it in Plotly is
memory-intensive. We recommend using the "Top 1% by Degree" toggle for most
exploration and only switching to the full view on a machine with at least 8GB RAM.

**Artist not found in the Path Finder**
Not every artist in the original dataset made it into the network. The graph only
includes artists whose songs appeared on Spotify's weekly charts. Try a more
mainstream artist name or check the spelling.

**Port 8501 already in use**
Run on a different port:
```bash
streamlit run dashboard_app.py --server.port 8502
```