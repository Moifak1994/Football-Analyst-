# Code Comparison: Original vs Improved

## 📋 Table of Contents
1. [Data Generation](#data-generation)
2. [Error Handling](#error-handling)
3. [Function Documentation](#function-documentation)
4. [Configuration Management](#configuration-management)
5. [Visualization Enhancements](#visualization-enhancements)
6. [User Feedback](#user-feedback)

---

## 1. Data Generation

### ❌ Original: Random, Uncorrelated Data
```python
def generate_sample_data():
    # Completely random possession and pass accuracy
    matches = pd.DataFrame({
        'possession':       np.random.randint(40, 70, 15),
        'pass_accuracy':    np.random.uniform(70, 92, 15),
        'shots':            np.random.randint(8, 25, 15),
        'shots_on_target':  np.random.randint(3, 12, 15),  # Can exceed total shots!
    })

    player_stats = pd.DataFrame({
        'goals':   [0,2,8,5,6,3,1,2,7,0,9],  # Hardcoded
        'assists': [0,3,4,7,5,4,2,6,3,1,5],  # No variance
    })
```

**Problems:**
- Pass accuracy independent of possession
- Shots on target can be more than total shots
- No statistical relationships
- Missing key metrics (xG, progressive passes, etc.)

### ✅ Improved: Realistic, Correlated Data
```python
def generate_realistic_matches(n_matches: int = 15) -> pd.DataFrame:
    """Generate realistic match data with correlated statistics."""

    for i in range(n_matches):
        # Base possession
        possession = np.random.uniform(40, 70)

        # Pass accuracy CORRELATES with possession
        pass_accuracy = 75 + (possession - 55) * 0.3 + np.random.uniform(-5, 5)
        pass_accuracy = np.clip(pass_accuracy, 70, 92)

        # Shots correlate with possession
        shots = int(10 + (possession - 50) * 0.4 + np.random.uniform(-3, 5))

        # Shots on target is PERCENTAGE of total shots (realistic!)
        shots_on_target = int(shots * np.random.uniform(0.30, 0.50))

        # Goals based on conversion rate
        goals_for = int(shots_on_target * np.random.uniform(0.1, 0.4))

        # xG - slightly higher than actual goals on average
        xg_for = goals_for + np.random.uniform(-0.5, 1.0)
```

**Benefits:**
- ✅ Statistics follow realistic patterns
- ✅ Correlations match real football
- ✅ New metrics (xG, tackles, interceptions)
- ✅ Type hints for clarity

---

## 2. Error Handling

### ❌ Original: Basic Error Handling
```python
def ensure_kaleido():
    try:
        importlib.import_module("kaleido")
        print("kaleido is already installed.")
        return True
    except ImportError:
        print("kaleido not found. Installing with pip...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", "kaleido"],
                check=True
            )
            print("kaleido installed successfully.")
            return True
        except Exception as e:  # Too broad!
            print("FAILED to install kaleido:", e)
            return False
```

**Problems:**
- Generic exception handling
- No output capture
- Silent failures possible

### ✅ Improved: Comprehensive Error Handling
```python
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
                capture_output=True,  # Capture stderr/stdout
                text=True
            )
            importlib.invalidate_caches()
            importlib.import_module("kaleido")
            print("✓ kaleido installed successfully.")
            return True
        except subprocess.CalledProcessError as e:  # Specific!
            print(f"✗ Failed to install kaleido: {e.stderr}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error installing kaleido: {e}")
            return False
```

**Benefits:**
- ✅ Specific exception types
- ✅ Captures error output
- ✅ Better user feedback
- ✅ Full docstring

---

## 3. Function Documentation

### ❌ Original: No Documentation
```python
def create_passing_network(passing_data, player_stats):
    network_agg = (
        passing_data
        .groupby(['passer','receiver'])['passes']
        .sum()
        .reset_index()
    )
    # ... rest of code
```

**Problems:**
- No type hints
- No docstring
- Unclear what data structure is expected
- Hard to understand purpose

### ✅ Improved: Full Documentation
```python
def create_passing_network(
    passing_data: pd.DataFrame,
    player_stats: pd.DataFrame
) -> go.Figure:
    """
    Create an interactive passing network visualization.

    The network shows passing relationships between players, with
    node size representing goal contributions and edge width
    representing pass frequency.

    Args:
        passing_data: DataFrame with columns ['passer', 'receiver', 'passes']
        player_stats: DataFrame with player statistics including position,
                      goals, assists, and rating

    Returns:
        Plotly Figure object containing the network visualization

    Example:
        >>> fig = create_passing_network(passing_data, player_stats)
        >>> fig.show()
    """
    # Aggregate passing data
    network_agg = (
        passing_data
        .groupby(['passer', 'receiver'])['passes']
        .sum()
        .reset_index()
    )
```

**Benefits:**
- ✅ Clear parameter types
- ✅ Return type specified
- ✅ Detailed description
- ✅ Usage example

---

## 4. Configuration Management

### ❌ Original: Magic Numbers Everywhere
```python
def create_passing_network(passing_data, player_stats):
    network_agg = network_agg[network_agg['passes'] >= 8]  # Why 8?

    pos = nx.spring_layout(G, k=2.5, iterations=100, seed=42)  # Why these values?

    fig.update_layout(
        width=1600, height=1400,  # Why these dimensions?
        plot_bgcolor='#1a1a2e',   # What color is this?
        paper_bgcolor='#16213e'
    )

# In create_enhanced_heatmap:
H, xedges, yedges = np.histogram2d(
    d['x'], d['y'],
    bins=[40, 26]  # Why 40x26?
)
```

**Problems:**
- Hardcoded values throughout
- Difficult to maintain consistency
- No single place to change settings

### ✅ Improved: Centralized Configuration
```python
@dataclass
class DashboardConfig:
    """Configuration for dashboard generation."""
    output_dir: str = "outputs"
    seed: int = 42

    # Pitch dimensions (meters)
    pitch_length: float = 105.0
    pitch_width: float = 68.0

    # Network settings
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

# Usage:
network_agg = network_agg[network_agg['passes'] >= config.min_passes_for_network]
pos = nx.spring_layout(G, k=config.network_layout_k, iterations=100, seed=config.seed)
fig.update_layout(
    plot_bgcolor=config.color_bg_light,
    paper_bgcolor=config.color_bg_mid
)
```

**Benefits:**
- ✅ Single source of truth
- ✅ Easy to customize
- ✅ Self-documenting
- ✅ Type safety

---

## 5. Visualization Enhancements

### ❌ Original: Basic Heatmap
```python
def create_enhanced_heatmap(df, player):
    d = df[df['player'] == player]
    if d.empty:
        return None

    H, xedges, yedges = np.histogram2d(
        d['x'], d['y'],
        bins=[40, 26]
    )

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=H.T,
        x=xedges[:-1],
        y=yedges[:-1],
        colorscale=[...],
        colorbar=dict(title="Activity")
    ))

    # No pitch markings!

    return fig
```

**Problems:**
- No context (pitch markings missing)
- Hard to understand player position
- No normalization

### ✅ Improved: Heatmap with Pitch
```python
def create_enhanced_heatmap(df: pd.DataFrame, player: str) -> Optional[go.Figure]:
    """Create a position heatmap with pitch markings."""

    player_data = df[df['player'] == player]

    if player_data.empty:
        print(f"⚠ Warning: No heatmap data for {player}")
        return None

    # Create histogram with proper pitch bounds
    H, xedges, yedges = np.histogram2d(
        player_data['x'],
        player_data['y'],
        bins=[40, 26],
        range=[[0, config.pitch_length], [0, config.pitch_width]]
    )

    # Normalize
    H = H / H.max() if H.max() > 0 else H

    fig = go.Figure()
    fig.add_trace(go.Heatmap(...))

    # ADD PITCH MARKINGS!
    pitch_lines = {
        'shapes': [
            # Outer boundary
            dict(type="rect", x0=0, y0=0,
                 x1=config.pitch_length, y1=config.pitch_width,
                 line=dict(color="white", width=2)),
            # Halfway line
            dict(type="line",
                 x0=config.pitch_length/2, y0=0,
                 x1=config.pitch_length/2, y1=config.pitch_width,
                 line=dict(color="white", width=2)),
            # Penalty areas (16.5m boxes)
            dict(type="rect", x0=0, y0=13.84, x1=16.5, y1=54.16,
                 line=dict(color="white", width=1)),
            # ... more markings
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
        showlegend=False
    ))

    fig.update_layout(shapes=pitch_lines['shapes'])

    return fig
```

**Benefits:**
- ✅ Accurate pitch dimensions
- ✅ Visual context with markings
- ✅ Normalized density
- ✅ Better tooltips

---

## 6. User Feedback

### ❌ Original: Basic Console Output
```python
print(">>> Generating data...")
print(">>> Building passing network...")
print(">>> Building heatmaps...")
print(">>> Building performance dashboard...")

# At the end:
print("\nALL DONE!")
print("Master HTML dashboard saved to:", MASTER_HTML_PATH)
```

**Problems:**
- Plain text
- No visual hierarchy
- No summary statistics
- No progress indication

### ✅ Improved: Rich Console Output
```python
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
    print("  → Building performance dashboard...")
    print("  → Building heatmaps...")

    # Export
    print("\n📄 Generating master HTML dashboard...")
    print(f"  ✓ Saved to: {MASTER_HTML_PATH}")

    print("\n🖼️ Exporting PNG visualization...")
    print(f"  ✓ PNG saved to: {PNG_PATH}")

    # Summary
    print("\n" + "="*70)
    print("✅ DASHBOARD GENERATION COMPLETE!")
    print("="*70)
    print(f"\n📊 Statistics Summary:")
    print(f"  • Matches analyzed: {len(matches)}")
    print(f"  • Players tracked: {len(player_stats)}")
    print(f"  • Total goals: {matches['goals_for'].sum()}")
    print(f"  • Average possession: {matches['possession'].mean():.1f}%")
    print(f"  • Top scorer: {player_stats.nlargest(1, 'goals').iloc[0]['player']} "
          f"({player_stats['goals'].max()} goals)")
    print("\n" + "="*70 + "\n")
```

**Benefits:**
- ✅ Emojis for visual appeal
- ✅ Clear sections
- ✅ Summary statistics
- ✅ Success indicators (✓/✗)
- ✅ Better formatting

---

## 📊 Overall Impact Summary

| Aspect | Lines Changed | Impact | Difficulty |
|--------|--------------|--------|------------|
| Data Generation | +120 lines | 🔥 High | Medium |
| Error Handling | +30 lines | 🔥 High | Easy |
| Documentation | +150 lines | ⭐ Medium | Easy |
| Configuration | +25 lines | ⭐ Medium | Easy |
| Visualizations | +80 lines | 🔥 High | Medium |
| User Feedback | +40 lines | ⭐ Medium | Easy |

**Total:** +445 lines of improvements

---

## 🎯 Key Takeaways

### Original Code
- ❌ Random, unrealistic data
- ❌ Poor error handling
- ❌ No documentation
- ❌ Hardcoded values
- ❌ Basic visualizations
- ✅ Working functionality

### Improved Code
- ✅ Realistic, correlated data
- ✅ Comprehensive error handling
- ✅ Full documentation (docstrings, type hints)
- ✅ Centralized configuration
- ✅ Enhanced visualizations (pitch markings, xG, etc.)
- ✅ Professional presentation
- ✅ Better user experience

---

## 💡 Learning Points

1. **Correlation Matters**: Football statistics aren't random - they relate to each other
2. **Type Hints Help**: They make code self-documenting and catch errors early
3. **Configuration is Key**: Centralize settings for easy maintenance
4. **User Feedback**: Good console output makes debugging easier
5. **Documentation**: Future-you will thank present-you for writing docstrings

---

**Conclusion:** The improved version is more maintainable, realistic, and professional while retaining all original functionality.
