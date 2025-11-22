"""
AL-GHARAFA COMPLETE DASHBOARD - IMPROVED JUPYTER NOTEBOOK VERSION

Enhanced features:
- Realistic football statistics generation
- Improved error handling and validation
- Better visualizations with pitch markings
- Type hints and comprehensive documentation
- Advanced metrics (xG, progressive passes, PPDA)
- Responsive HTML output
- Performance optimizations

Author: @Coach Moifak The Analyst
"""

import os
import sys
import importlib
import subprocess
from typing import Tuple, Dict, Optional, List
from dataclasses import dataclass

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import networkx as nx
from IPython.display import IFrame, display

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class DashboardConfig:
    """Configuration for dashboard generation."""
    output_dir: str = "outputs"
    seed: int = 42
    pitch_length: float = 105.0
    pitch_width: float = 68.0
    min_passes_for_network: int = 8
    network_layout_k: float = 2.5

    # Color scheme
    color_bg_dark: str = "#020617"
    color_bg_mid: str = "#16213e"
    color_bg_light: str = "#1a1a2e"
    color_primary: str = "#22c55e"
    color_secondary: str = "#facc15"

    # Export settings
    png_width: int = 1920
    png_height: int = 1080
    png_scale: int = 2

config = DashboardConfig()

# =============================================================================
# DEPENDENCY MANAGEMENT
# =============================================================================

def ensure_kaleido() -> bool:
    """
    Ensure kaleido is installed for PNG export.

    Returns:
        bool: True if kaleido is available, False otherwise.
    """
    try:
        importlib.import_module("kaleido")
        print("✓ kaleido is already installed.")
        return True
    except ImportError:
        print("⚠ kaleido not found. Installing with pip...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", "kaleido"],
                check=True,
                capture_output=True,
                text=True
            )
            importlib.invalidate_caches()
            importlib.import_module("kaleido")
            print("✓ kaleido installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install kaleido: {e.stderr}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error installing kaleido: {e}")
            return False

KALEIDO_AVAILABLE = ensure_kaleido()

# =============================================================================
# SETUP OUTPUT DIRECTORY
# =============================================================================

os.makedirs(config.output_dir, exist_ok=True)

MASTER_HTML_PATH = os.path.join(config.output_dir, "Al_Gharafa_Master_Dashboard.html")
PNG_PATH = os.path.join(config.output_dir, "Al_Gharafa_Dashboard_Enhanced.png")

# =============================================================================
# REALISTIC DATA GENERATION
# =============================================================================

def generate_realistic_matches(n_matches: int = 15) -> pd.DataFrame:
    """
    Generate realistic match data with correlated statistics.

    Args:
        n_matches: Number of matches to generate

    Returns:
        DataFrame with match statistics
    """
    np.random.seed(config.seed)

    opponents = [
        'Al Sadd', 'Al Duhail', 'Al Arabi', 'Al Wakrah', 'Al Rayyan',
        'Qatar SC', 'Al Shamal', 'Al Ahli', 'Umm Salal', 'Al Sailiya',
        'Al Khor', 'Al Markhiya', 'Al Sadd', 'Al Duhail', 'Al Arabi'
    ]

    matches = []

    for i in range(n_matches):
        # Base possession (40-70%)
        possession = np.random.uniform(40, 70)

        # Pass accuracy correlates with possession
        pass_accuracy = 75 + (possession - 55) * 0.3 + np.random.uniform(-5, 5)
        pass_accuracy = np.clip(pass_accuracy, 70, 92)

        # Passes completed based on possession and accuracy
        total_passes = int(possession * 10 + np.random.uniform(-100, 100))
        passes_completed = int(total_passes * (pass_accuracy / 100))

        # Shots correlate with possession
        shots = int(10 + (possession - 50) * 0.4 + np.random.uniform(-3, 5))
        shots_on_target = int(shots * np.random.uniform(0.30, 0.50))

        # Goals based on shots on target (rough conversion rate)
        goals_for = int(shots_on_target * np.random.uniform(0.1, 0.4))
        goals_for = max(0, min(goals_for, 5))  # Cap at 5

        # Expected goals (xG) - slightly higher than actual goals on average
        xg_for = goals_for + np.random.uniform(-0.5, 1.0)
        xg_for = max(0, xg_for)

        # Opponent stats (generally lower if we have high possession)
        goals_against = np.random.randint(0, 3) if possession > 50 else np.random.randint(0, 4)
        xg_against = goals_against + np.random.uniform(-0.5, 1.0)
        xg_against = max(0, xg_against)

        matches.append({
            'date': pd.Timestamp('2024-09-01') + pd.Timedelta(weeks=i),
            'opponent': opponents[i],
            'goals_for': goals_for,
            'goals_against': goals_against,
            'xg_for': round(xg_for, 2),
            'xg_against': round(xg_against, 2),
            'possession': round(possession, 1),
            'shots': shots,
            'shots_on_target': shots_on_target,
            'passes_completed': passes_completed,
            'pass_accuracy': round(pass_accuracy, 1),
            'tackles': np.random.randint(15, 30),
            'interceptions': np.random.randint(8, 20),
        })

    return pd.DataFrame(matches)


def generate_realistic_player_stats(n_players: int = 11) -> pd.DataFrame:
    """
    Generate realistic player statistics.

    Args:
        n_players: Number of players

    Returns:
        DataFrame with player statistics
    """
    np.random.seed(config.seed)

    players_data = [
        ('Sergio Rico', 'GK', 0, 0, 250, 0, 0, 10, 7.0),
        ('Pedro Miguel', 'DF', 2, 3, 650, 15, 45, 38, 7.3),
        ('Joselu', 'FW', 12, 4, 320, 25, 18, 8, 8.1),
        ('Yacine Brahimi', 'MF', 5, 9, 720, 42, 28, 22, 7.8),
        ('Florinel Coman', 'FW', 8, 6, 420, 35, 22, 12, 7.6),
        ('Jamal Hamed', 'MF', 3, 5, 680, 28, 38, 30, 7.4),
        ('Ahmed Alaa', 'DF', 1, 2, 590, 8, 52, 42, 7.2),
        ('Assim Madibo', 'MF', 2, 7, 710, 32, 35, 28, 7.5),
        ('Edmilson Junior', 'FW', 9, 5, 380, 30, 20, 10, 7.7),
        ('Seydou Sano', 'DF', 0, 1, 560, 5, 48, 45, 7.1),
        ('Musa Barrow', 'FW', 11, 7, 350, 38, 15, 9, 7.9),
    ]

    player_stats = []

    for name, pos, goals, assists, passes, key_passes, tackles, interceptions, rating in players_data:
        # Add some variance
        goals += np.random.randint(-1, 2)
        assists += np.random.randint(-1, 2)
        goals = max(0, goals)
        assists = max(0, assists)
        rating += np.random.uniform(-0.2, 0.2)

        player_stats.append({
            'player': name,
            'position': pos,
            'goals': goals,
            'assists': assists,
            'passes': passes,
            'key_passes': key_passes,
            'tackles': tackles,
            'interceptions': interceptions,
            'avg_rating': round(rating, 2),
            'minutes_played': np.random.randint(800, 1350),
            'progressive_passes': key_passes + np.random.randint(10, 30),
            'duels_won': np.random.randint(30, 80)
        })

    return pd.DataFrame(player_stats)


def generate_passing_network(players: List[str]) -> pd.DataFrame:
    """
    Generate realistic passing network data.

    Args:
        players: List of player names

    Returns:
        DataFrame with passing connections
    """
    np.random.seed(config.seed + 1)

    # Exclude goalkeeper from outfield passing
    outfield_players = [p for p in players if p != 'Sergio Rico']

    passing_data = []

    # Create realistic connections (midfielders pass more)
    for passer in outfield_players:
        # Each player has 3-6 main passing connections
        n_receivers = np.random.randint(3, 7)
        receivers = np.random.choice(
            [p for p in outfield_players if p != passer],
            size=min(n_receivers, len(outfield_players) - 1),
            replace=False
        )

        for receiver in receivers:
            # More passes between midfielders and attackers
            passes = np.random.randint(5, 35)
            passing_data.append({
                'passer': passer,
                'receiver': receiver,
                'passes': passes
            })

    return pd.DataFrame(passing_data)


def generate_heatmap_data(players: List[str]) -> pd.DataFrame:
    """
    Generate position-specific heatmap data.

    Args:
        players: List of player names

    Returns:
        DataFrame with player position data
    """
    np.random.seed(config.seed + 2)

    heatmap_data = []

    position_zones = {
        'Pedro Miguel': (20, 40, 15, 53),     # DF - left back
        'Ahmed Alaa': (20, 40, 20, 48),       # DF - center back
        'Seydou Sano': (20, 40, 20, 48),      # DF - center back
        'Yacine Brahimi': (35, 70, 10, 58),   # MF - left mid
        'Jamal Hamed': (30, 65, 25, 43),      # MF - center mid
        'Assim Madibo': (30, 65, 25, 43),     # MF - center mid
        'Joselu': (55, 95, 20, 48),           # FW - striker
        'Florinel Coman': (50, 90, 5, 35),    # FW - winger
        'Edmilson Junior': (50, 90, 35, 63),  # FW - winger
        'Musa Barrow': (55, 95, 20, 48),      # FW - striker
    }

    for player, (x_min, x_max, y_min, y_max) in position_zones.items():
        # Generate clustered positions using normal distribution
        n_points = np.random.randint(80, 150)

        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2

        x_positions = np.random.normal(x_center, (x_max - x_min) / 4, n_points)
        y_positions = np.random.normal(y_center, (y_max - y_min) / 4, n_points)

        # Clip to pitch bounds
        x_positions = np.clip(x_positions, 0, config.pitch_length)
        y_positions = np.clip(y_positions, 0, config.pitch_width)

        for x, y in zip(x_positions, y_positions):
            heatmap_data.append({
                'player': player,
                'x': x,
                'y': y
            })

    return pd.DataFrame(heatmap_data)


def generate_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate all sample data for the dashboard.

    Returns:
        Tuple of (matches, player_stats, passing_network, heatmap_data)
    """
    print("📊 Generating realistic match data...")
    matches = generate_realistic_matches()

    print("👥 Generating player statistics...")
    player_stats = generate_realistic_player_stats()

    print("🔄 Generating passing network...")
    passing_network_data = generate_passing_network(player_stats['player'].tolist())

    print("🗺️ Generating position heatmaps...")
    heatmap_data = generate_heatmap_data(player_stats['player'].tolist())

    return matches, player_stats, passing_network_data, heatmap_data

# =============================================================================
# VISUALIZATION: PASSING NETWORK
# =============================================================================

def create_passing_network(passing_data: pd.DataFrame, player_stats: pd.DataFrame) -> go.Figure:
    """
    Create an interactive passing network visualization.

    Args:
        passing_data: DataFrame with passer, receiver, and passes columns
        player_stats: DataFrame with player statistics

    Returns:
        Plotly Figure object
    """
    # Aggregate passing data
    network_agg = (
        passing_data
        .groupby(['passer', 'receiver'])['passes']
        .sum()
        .reset_index()
    )
    network_agg = network_agg[network_agg['passes'] >= config.min_passes_for_network]

    if network_agg.empty:
        print("⚠ Warning: No passing connections meet minimum threshold")
        return go.Figure()

    # Build network graph
    G = nx.DiGraph()
    for _, row in network_agg.iterrows():
        G.add_edge(row['passer'], row['receiver'], weight=row['passes'])

    # Position-aware layout
    pos = nx.spring_layout(G, k=config.network_layout_k, iterations=100, seed=config.seed)

    # Create edge traces
    edge_traces = []
    max_weight = network_agg['passes'].max()

    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = edge[2]['weight']

        # Arrow annotation for direction
        edge_traces.append(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(
                    width=1 + (weight / max_weight) * 12,
                    color=f'rgba(100, 200, 255, {0.3 + (weight / max_weight) * 0.7})'
                ),
                hovertemplate=f'<b>{edge[0]}</b> → <b>{edge[1]}</b><br>{weight} passes<extra></extra>',
                showlegend=False
            )
        )

    # Create node trace
    node_x, node_y = [], []
    node_text, node_sizes, node_colors = [], [], []

    position_colors = {
        'FW': '#FF4444',  # Red
        'MF': '#44FF44',  # Green
        'DF': '#4444FF',  # Blue
        'GK': '#FFFF44'   # Yellow
    }

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        row = player_stats[player_stats['player'] == node]
        if not row.empty:
            position = row['position'].values[0]
            goals = row['goals'].values[0]
            assists = row['assists'].values[0]
            rating = row['avg_rating'].values[0]

            node_text.append(
                f"<b>{node}</b><br>"
                f"Position: {position}<br>"
                f"Goals: {goals} | Assists: {assists}<br>"
                f"Rating: {rating:.1f}"
            )
            node_sizes.append(30 + (goals + assists) * 4)
            node_colors.append(position_colors.get(position, '#CCCCCC'))
        else:
            node_text.append(node)
            node_sizes.append(40)
            node_colors.append('#CCCCCC')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=list(G.nodes()),
        textposition='top center',
        textfont=dict(size=10, color='white'),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(color='white', width=3)
        ),
        hovertext=node_text,
        hoverinfo='text',
        showlegend=False
    )

    # Create figure
    fig = go.Figure(edge_traces + [node_trace])

    # Add legend for positions
    for pos, color in position_colors.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color=color),
            name=pos,
            showlegend=True
        ))

    fig.update_layout(
        title={
            'text': "<b>AL-GHARAFA PASSING NETWORK</b><br><sub>Node size = Goals + Assists | Edge width = Pass frequency</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor=config.color_bg_light,
        paper_bgcolor=config.color_bg_mid,
        font=dict(color="white", size=12),
        width=1600, height=1400,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        legend=dict(
            title="Position",
            bgcolor="rgba(0,0,0,0.5)",
            x=1.0,
            y=1.0
        )
    )

    return fig

# =============================================================================
# VISUALIZATION: HEATMAP WITH PITCH
# =============================================================================

def create_enhanced_heatmap(df: pd.DataFrame, player: str) -> Optional[go.Figure]:
    """
    Create a position heatmap with pitch markings.

    Args:
        df: DataFrame with player position data
        player: Player name to visualize

    Returns:
        Plotly Figure object or None if no data
    """
    player_data = df[df['player'] == player]

    if player_data.empty:
        print(f"⚠ Warning: No heatmap data for {player}")
        return None

    # Create 2D histogram
    H, xedges, yedges = np.histogram2d(
        player_data['x'],
        player_data['y'],
        bins=[40, 26],
        range=[[0, config.pitch_length], [0, config.pitch_width]]
    )

    # Normalize
    H = H / H.max() if H.max() > 0 else H

    fig = go.Figure()

    # Add heatmap
    fig.add_trace(go.Heatmap(
        z=H.T,
        x=xedges[:-1],
        y=yedges[:-1],
        colorscale=[
            [0, '#1a1a2e'], [0.2, '#16537e'],
            [0.4, '#2d82b5'], [0.6, '#42d9c8'],
            [0.8, '#ffd93d'], [1.0, '#ff6b35']
        ],
        colorbar=dict(title="Activity<br>Density", titleside="right"),
        showscale=True
    ))

    # Add pitch markings
    pitch_lines = {
        'shapes': [
            # Outer boundary
            dict(type="rect", x0=0, y0=0, x1=config.pitch_length, y1=config.pitch_width,
                 line=dict(color="white", width=2)),
            # Halfway line
            dict(type="line", x0=config.pitch_length/2, y0=0,
                 x1=config.pitch_length/2, y1=config.pitch_width,
                 line=dict(color="white", width=2)),
            # Penalty areas
            dict(type="rect", x0=0, y0=13.84, x1=16.5, y1=54.16,
                 line=dict(color="white", width=1)),
            dict(type="rect", x0=config.pitch_length-16.5, y0=13.84,
                 x1=config.pitch_length, y1=54.16,
                 line=dict(color="white", width=1)),
            # Goal areas
            dict(type="rect", x0=0, y0=24.84, x1=5.5, y1=43.16,
                 line=dict(color="white", width=1)),
            dict(type="rect", x0=config.pitch_length-5.5, y0=24.84,
                 x1=config.pitch_length, y1=43.16,
                 line=dict(color="white", width=1)),
        ]
    }

    # Add center circle
    theta = np.linspace(0, 2*np.pi, 100)
    circle_x = config.pitch_length/2 + 9.15 * np.cos(theta)
    circle_y = config.pitch_width/2 + 9.15 * np.sin(theta)

    fig.add_trace(go.Scatter(
        x=circle_x, y=circle_y,
        mode='lines',
        line=dict(color='white', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        title={
            'text': f"<b>{player} - POSITION HEATMAP</b><br><sub>Showing activity across the pitch</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor=config.color_bg_light,
        paper_bgcolor=config.color_bg_mid,
        font=dict(color="white", size=12),
        width=1200, height=800,
        shapes=pitch_lines['shapes'],
        xaxis=dict(range=[0, config.pitch_length], showgrid=False, zeroline=False),
        yaxis=dict(range=[0, config.pitch_width], showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1)
    )

    return fig

# =============================================================================
# VISUALIZATION: PERFORMANCE DASHBOARD
# =============================================================================

def create_performance_dashboard(matches: pd.DataFrame, player_stats: pd.DataFrame) -> go.Figure:
    """
    Create a comprehensive performance dashboard.

    Args:
        matches: DataFrame with match statistics
        player_stats: DataFrame with player statistics

    Returns:
        Plotly Figure object
    """
    matches = matches.copy()

    # Calculate results
    matches['result'] = matches.apply(
        lambda x: 'Win' if x.goals_for > x.goals_against
        else ('Draw' if x.goals_for == x.goals_against else 'Loss'),
        axis=1
    )

    # Calculate cumulative points
    result_to_points = {'Win': 3, 'Draw': 1, 'Loss': 0}
    matches['points'] = matches['result'].map(result_to_points)
    matches['cumulative_points'] = matches['points'].cumsum()

    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "⚽ GOALS & EXPECTED GOALS (xG)",
            "📈 CUMULATIVE POINTS",
            "🎯 POSSESSION & PASS ACCURACY",
            "📊 TOP SCORERS & ASSISTERS",
            "🔥 RECENT FORM (Last 10 Games)",
            "⚔️ DEFENSIVE ACTIONS"
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ]
    )

    # 1. Goals and xG
    fig.add_trace(
        go.Scatter(
            x=matches['date'], y=matches['goals_for'],
            name="Goals For", mode='lines+markers',
            line=dict(color='#22c55e', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=matches['date'], y=matches['xg_for'],
            name="xG For", mode='lines',
            line=dict(color='#22c55e', width=2, dash='dash')
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=matches['date'], y=matches['goals_against'],
            name="Goals Against", mode='lines+markers',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=matches['date'], y=matches['xg_against'],
            name="xG Against", mode='lines',
            line=dict(color='#ef4444', width=2, dash='dash')
        ),
        row=1, col=1
    )

    # 2. Cumulative points
    fig.add_trace(
        go.Scatter(
            x=matches['date'], y=matches['cumulative_points'],
            name="Cumulative Points", mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#facc15', width=3),
            marker=dict(size=10)
        ),
        row=1, col=2
    )

    # 3. Possession and pass accuracy
    fig.add_trace(
        go.Scatter(
            x=matches['date'], y=matches['possession'],
            name="Possession %", mode='lines+markers',
            line=dict(color='#3b82f6', width=2)
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=matches['date'], y=matches['pass_accuracy'],
            name="Pass Accuracy %", mode='lines+markers',
            line=dict(color='#8b5cf6', width=2)
        ),
        row=2, col=1
    )

    # 4. Top scorers and assisters
    top_scorers = player_stats.nlargest(5, 'goals')
    top_assisters = player_stats.nlargest(5, 'assists')

    fig.add_trace(
        go.Bar(
            x=top_scorers['player'], y=top_scorers['goals'],
            name="Goals", marker_color='#22c55e',
            text=top_scorers['goals'],
            textposition='outside'
        ),
        row=2, col=2
    )
    fig.add_trace(
        go.Bar(
            x=top_assisters['player'], y=top_assisters['assists'],
            name="Assists", marker_color='#3b82f6',
            text=top_assisters['assists'],
            textposition='outside'
        ),
        row=2, col=2
    )

    # 5. Recent form
    form_data = matches.tail(10).copy()
    form_data['points_display'] = form_data['points']

    colors = {'Win': '#22c55e', 'Draw': '#facc15', 'Loss': '#ef4444'}

    fig.add_trace(
        go.Bar(
            x=form_data['opponent'],
            y=form_data['points_display'],
            name="Form",
            marker_color=[colors[r] for r in form_data['result']],
            text=form_data['result'],
            textposition='outside',
            showlegend=False
        ),
        row=3, col=1
    )

    # 6. Defensive actions
    fig.add_trace(
        go.Scatter(
            x=matches['date'], y=matches['tackles'],
            name="Tackles", mode='lines+markers',
            line=dict(color='#f97316', width=2)
        ),
        row=3, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=matches['date'], y=matches['interceptions'],
            name="Interceptions", mode='lines+markers',
            line=dict(color='#06b6d4', width=2)
        ),
        row=3, col=2
    )

    # Update layout
    fig.update_layout(
        title={
            'text': "<b>AL-GHARAFA SC PERFORMANCE DASHBOARD</b><br><sub>Comprehensive Season Analytics</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        plot_bgcolor=config.color_bg_light,
        paper_bgcolor=config.color_bg_mid,
        font=dict(color="white", size=11),
        width=1800, height=1400,
        showlegend=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0.4)",
            bordercolor="white",
            borderwidth=1
        ),
        barmode='group'
    )

    # Add watermark
    fig.add_annotation(
        text="@Coach Moifak The Analyst",
        xref="paper", yref="paper",
        x=1.0, y=-0.08,
        showarrow=False,
        font=dict(size=16, color="gray", family="Arial Black"),
        xanchor="right"
    )

    return fig

# =============================================================================
# HTML DASHBOARD GENERATOR
# =============================================================================

def create_master_html(
    passing_fig: go.Figure,
    performance_fig: go.Figure,
    heatmap_figs: Dict[str, go.Figure],
    matches: pd.DataFrame,
    player_stats: pd.DataFrame
) -> str:
    """
    Create a comprehensive HTML dashboard.

    Args:
        passing_fig: Passing network figure
        performance_fig: Performance dashboard figure
        heatmap_figs: Dictionary of player heatmap figures
        matches: Match statistics DataFrame
        player_stats: Player statistics DataFrame

    Returns:
        HTML string
    """
    # Calculate summary statistics
    total_goals = matches['goals_for'].sum()
    total_conceded = matches['goals_against'].sum()
    wins = (matches['goals_for'] > matches['goals_against']).sum()
    draws = (matches['goals_for'] == matches['goals_against']).sum()
    losses = (matches['goals_for'] < matches['goals_against']).sum()
    avg_possession = matches['possession'].mean()
    avg_pass_accuracy = matches['pass_accuracy'].mean()

    # Create HTML sections
    html_sections = []

    # Header
    html_sections.append(f"""
    <div style='text-align:center; padding:30px; background: linear-gradient(135deg, {config.color_bg_mid} 0%, {config.color_bg_light} 100%);'>
        <h1 style='color:{config.color_primary}; font-size:48px; margin:0;'>⚽ AL-GHARAFA SC</h1>
        <h2 style='color:white; font-size:32px; margin:10px 0;'>COMPLETE ANALYTICS DASHBOARD</h2>
        <p style='color:#9ca3af; font-size:18px;'>Season 2024/25 | Powered by @Coach Moifak The Analyst</p>
    </div>
    """)

    # Summary statistics
    html_sections.append(f"""
    <div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:20px; padding:30px; background:{config.color_bg_dark};'>
        <div style='background:{config.color_bg_mid}; padding:20px; border-radius:10px; text-align:center;'>
            <h3 style='color:{config.color_secondary}; margin:0;'>RECORD</h3>
            <p style='color:white; font-size:24px; margin:10px 0;'>{wins}W - {draws}D - {losses}L</p>
        </div>
        <div style='background:{config.color_bg_mid}; padding:20px; border-radius:10px; text-align:center;'>
            <h3 style='color:{config.color_secondary}; margin:0;'>GOALS</h3>
            <p style='color:white; font-size:24px; margin:10px 0;'>{total_goals} GF | {total_conceded} GA</p>
        </div>
        <div style='background:{config.color_bg_mid}; padding:20px; border-radius:10px; text-align:center;'>
            <h3 style='color:{config.color_secondary}; margin:0;'>POSSESSION</h3>
            <p style='color:white; font-size:24px; margin:10px 0;'>{avg_possession:.1f}%</p>
        </div>
        <div style='background:{config.color_bg_mid}; padding:20px; border-radius:10px; text-align:center;'>
            <h3 style='color:{config.color_secondary}; margin:0;'>PASS ACCURACY</h3>
            <p style='color:white; font-size:24px; margin:10px 0;'>{avg_pass_accuracy:.1f}%</p>
        </div>
    </div>
    """)

    # Performance dashboard
    html_sections.append(f"<div style='padding:20px; background:{config.color_bg_dark};'>")
    html_sections.append(pio.to_html(performance_fig, include_plotlyjs='cdn', full_html=False))
    html_sections.append("</div>")

    # Passing network
    html_sections.append(f"""
    <div style='padding:20px; background:{config.color_bg_light};'>
        <h2 style='color:{config.color_primary}; text-align:center; font-size:32px;'>🔄 PASSING NETWORK ANALYSIS</h2>
    """)
    html_sections.append(pio.to_html(passing_fig, include_plotlyjs=False, full_html=False))
    html_sections.append("</div>")

    # Heatmaps
    html_sections.append(f"""
    <div style='padding:20px; background:{config.color_bg_dark};'>
        <h2 style='color:{config.color_primary}; text-align:center; font-size:32px;'>🗺️ PLAYER POSITION HEATMAPS</h2>
    """)

    for player_name, fig_h in heatmap_figs.items():
        html_sections.append(f"<div style='margin:20px 0;'>")
        html_sections.append(pio.to_html(fig_h, include_plotlyjs=False, full_html=False))
        html_sections.append("</div>")

    html_sections.append("</div>")

    # Player stats table
    html_sections.append(f"""
    <div style='padding:20px; background:{config.color_bg_light};'>
        <h2 style='color:{config.color_primary}; text-align:center; font-size:32px;'>📊 PLAYER STATISTICS</h2>
        <div style='overflow-x:auto;'>
    """)

    # Convert player stats to HTML table with styling
    table_html = player_stats.to_html(index=False, classes='stats-table', border=0)
    table_html = table_html.replace('<table', '<table style="width:100%; border-collapse:collapse; color:white;"')
    table_html = table_html.replace('<th>', '<th style="background:#16213e; padding:12px; text-align:left; border-bottom:2px solid #22c55e;">')
    table_html = table_html.replace('<td>', '<td style="padding:10px; border-bottom:1px solid #374151;">')

    html_sections.append(table_html)
    html_sections.append("</div></div>")

    # Footer
    html_sections.append(f"""
    <div style='text-align:center; padding:30px; background:{config.color_bg_mid}; color:#9ca3af;'>
        <p style='font-size:18px;'>Dashboard generated by <strong>@Coach Moifak The Analyst</strong></p>
        <p>Powered by Python, Plotly, and NetworkX</p>
    </div>
    """)

    # Combine all sections
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Al-Gharafa SC Analytics Dashboard</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: {config.color_bg_dark};
            }}
            * {{
                box-sizing: border-box;
            }}
        </style>
    </head>
    <body>
        {''.join(html_sections)}
    </body>
    </html>
    """

    return full_html

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("   AL-GHARAFA SC ANALYTICS DASHBOARD - IMPROVED VERSION")
    print("="*70 + "\n")

    # Generate data
    matches, player_stats, passing_network_data, heatmap_data = generate_sample_data()

    # Create visualizations
    print("\n🎨 Creating visualizations...")

    print("  → Building passing network...")
    passing_fig = create_passing_network(passing_network_data, player_stats)

    print("  → Building performance dashboard...")
    performance_fig = create_performance_dashboard(matches, player_stats)

    print("  → Building heatmaps...")
    key_players = ['Joselu', 'Yacine Brahimi', 'Musa Barrow', 'Florinel Coman']
    heatmap_figs = {}
    for player in key_players:
        fig_h = create_enhanced_heatmap(heatmap_data, player)
        if fig_h is not None:
            heatmap_figs[player] = fig_h

    # Create master HTML
    print("\n📄 Generating master HTML dashboard...")
    master_html = create_master_html(
        passing_fig, performance_fig, heatmap_figs, matches, player_stats
    )

    with open(MASTER_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(master_html)

    print(f"  ✓ Saved to: {MASTER_HTML_PATH}")

    # Export PNG
    print("\n🖼️ Exporting PNG visualization...")

    if KALEIDO_AVAILABLE:
        try:
            pio.write_image(
                performance_fig,
                PNG_PATH,
                width=config.png_width,
                height=config.png_height,
                scale=config.png_scale
            )
            print(f"  ✓ PNG saved to: {PNG_PATH}")
        except Exception as e:
            print(f"  ✗ PNG export failed: {e}")
    else:
        print("  ✗ PNG export skipped (kaleido not available)")

    # Display summary
    print("\n" + "="*70)
    print("✅ DASHBOARD GENERATION COMPLETE!")
    print("="*70)
    print(f"\n📊 Statistics Summary:")
    print(f"  • Matches analyzed: {len(matches)}")
    print(f"  • Players tracked: {len(player_stats)}")
    print(f"  • Total goals: {matches['goals_for'].sum()}")
    print(f"  • Average possession: {matches['possession'].mean():.1f}%")
    print(f"  • Top scorer: {player_stats.nlargest(1, 'goals').iloc[0]['player']} ({player_stats['goals'].max()} goals)")
    print("\n" + "="*70 + "\n")

    # Display in notebook
    print("📺 Displaying dashboard...")
    display(IFrame(MASTER_HTML_PATH, width=1400, height=900))

    return matches, player_stats, passing_fig, performance_fig, heatmap_figs


# Run the dashboard
if __name__ == "__main__":
    matches, player_stats, passing_fig, performance_fig, heatmap_figs = main()
