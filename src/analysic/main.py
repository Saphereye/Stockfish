"""
nmp_analysis.py  – fast version using Polars + presentation-grade plots

Usage:
    uv run main.py nmp_log.csv              # full data
    uv run main.py nmp_log.csv --dedup      # drop duplicate rows first
"""

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import polars as pl

# ── CLI args ──────────────────────────────────────────────────────────────────
args = sys.argv[1:]
if not args:
    print("Usage: main.py <csv_path> [--dedup]")
    sys.exit(1)

CSV_PATH = args[0]
DEDUP    = "--dedup" in args

BIN_LO, BIN_HI, N_BINS = -200, 200, 20
BINS     = np.linspace(BIN_LO, BIN_HI, N_BINS + 1)
BIN_MIDS = (BINS[:-1] + BINS[1:]) / 2

EVAL_BIN_SIZE = 25   # cp per bucket for plot 4
EVAL_LO, EVAL_HI = -300, 300

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = "#0f1117"
PANEL_BG = "#1a1d27"
GRID_C   = "#2a2d3a"
TEXT_C   = "#e8eaf0"
MUTED_C  = "#6b7280"
ACCENT   = "#4f9cf9"
ACCENT2  = "#f97316"
ACCENT3  = "#22d3a0"
ZERO_C   = "#475569"

plt.rcParams.update({
    "figure.facecolor": BG,   "axes.facecolor":  PANEL_BG,
    "axes.edgecolor":   GRID_C, "axes.labelcolor": MUTED_C,
    "axes.titlecolor":  TEXT_C, "axes.grid":       True,
    "axes.titlesize":   11,     "axes.titleweight": "bold",
    "axes.labelsize":   9,      "grid.color":      GRID_C,
    "grid.linewidth":   0.6,    "xtick.color":     MUTED_C,
    "ytick.color":      MUTED_C, "xtick.labelsize": 8,
    "ytick.labelsize":  8,      "text.color":      TEXT_C,
    "font.family":      "monospace",
})

# ── 1. Load and count lines ───────────────────────────────────────────────────
t0 = time.perf_counter()

# First, count total lines in the file (fast, no parsing)
print("="*60)
print("STEP 1: File Statistics")
print("="*60)
print("Counting total lines in file...")
with open(CSV_PATH, 'r') as f:
    total_lines = sum(1 for _ in f)
print(f"Total lines in file (including header): {total_lines:,}")
print(f"Total data rows (excluding header): {total_lines - 1:,}")

# Define the exact schema we expect
schema = {
    "depth": pl.Int32,
    "root_depth": pl.Int32, 
    "null_margin": pl.Int32,
    "eval_margin": pl.Int32,
    "ply": pl.Int32,
}

print("\n" + "="*60)
print("STEP 2: CSV Parsing")
print("="*60)
print("Loading CSV...")
print("Note: Rows with incorrect column count will be automatically truncated")

# Load with truncate_ragged_lines=True to skip bad rows
lf = pl.scan_csv(
    CSV_PATH,
    has_header=True,
    schema=schema,  # Explicit schema ensures correct types
    truncate_ragged_lines=True,  # Skip extra columns in bad rows
)

# Count how many rows were successfully parsed
print("Counting successfully parsed rows...")
parsed_rows = lf.select(pl.len()).collect().item()
print(f"Successfully parsed rows: {parsed_rows:,}")

# Count rows with nulls before dropping - FIXED SYNTAX
print("Checking for null values...")
# Check each column for nulls
null_counts = {}
for col in schema.keys():
    null_count = lf.filter(pl.col(col).is_null()).select(pl.len()).collect().item()
    if null_count > 0:
        null_counts[col] = null_count

rows_with_nulls = sum(null_counts.values()) if null_counts else 0
if null_counts:
    print(f"Rows with null values by column:")
    for col, count in null_counts.items():
        print(f"  {col}: {count:,} rows")
else:
    print("No null values found in any column")

# Drop nulls
lf = lf.drop_nulls()
rows_after_dropping_nulls = lf.select(pl.len()).collect().item()
print(f"Rows after dropping nulls: {rows_after_dropping_nulls:,}")

# Calculate parsing statistics
total_data_rows = total_lines - 1
malformed_rows = total_data_rows - parsed_rows
null_rows_dropped = rows_with_nulls

print(f"\n--- Parsing Summary ---")
print(f"Total data rows in file:  {total_data_rows:,}")
print(f"Successfully parsed:      {parsed_rows:,} ({parsed_rows/total_data_rows*100:.6f}%)")
print(f"Malformed rows skipped:   {malformed_rows:,} ({malformed_rows/total_data_rows*100:.6f}%)")
print(f"Rows with nulls dropped:  {null_rows_dropped:,} ({null_rows_dropped/total_data_rows*100:.6f}%)")
print(f"Valid rows for analysis:  {rows_after_dropping_nulls:,} ({rows_after_dropping_nulls/total_data_rows*100:.6f}%)")

# Apply filters
print("\n" + "="*60)
print("STEP 3: Data Filtering")
print("="*60)
print("Applying range filters...")
print("  - depth between 1 and 60")
print("  - null_margin between -2000 and 2000")
print("  - eval_margin between -2000 and 2000")

# Store count before filtering
count_before_filter = rows_after_dropping_nulls

# Apply filters
lf = lf.filter(
    (pl.col("depth").is_between(1, 60)) &
    (pl.col("null_margin").is_between(-2000, 2000)) &
    (pl.col("eval_margin").is_between(-2000, 2000))
)

filtered_rows = lf.select(pl.len()).collect().item()
filtered_out = count_before_filter - filtered_rows

print(f"Rows before range filters: {count_before_filter:,}")
print(f"Rows after range filters:  {filtered_rows:,}")
print(f"Rows filtered out:         {filtered_out:,} ({filtered_out/count_before_filter*100:.4f}%)")

# Apply deduplication if requested
if DEDUP:
    print("\n" + "="*60)
    print("STEP 4: Deduplication")
    print("="*60)
    print("Removing duplicate rows...")
    
    # Store original count
    original_count = filtered_rows
    
    # Apply dedup
    lf = lf.unique()
    
    # Count after dedup
    deduped_rows = lf.select(pl.len()).collect().item()
    duplicates_removed = original_count - deduped_rows
    
    print(f"Rows before dedup:  {original_count:,}")
    print(f"Rows after dedup:   {deduped_rows:,}")
    print(f"Duplicates removed: {duplicates_removed:,} ({duplicates_removed/original_count*100:.6f}%)")
    
    final_rows = deduped_rows
else:
    final_rows = filtered_rows
    print("\nNo deduplication requested (use --dedup flag to remove duplicates)")

# Final dataset for analysis (re-apply filters after dedup just to be safe)
lf = lf.filter(
    (pl.col("depth").is_between(1, 60)) &
    (pl.col("null_margin").is_between(-2000, 2000)) &
    (pl.col("eval_margin").is_between(-2000, 2000))
)

# ── 2. Core aggregations ──────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 5: Analysis")
print("="*60)
print("Computing core aggregations...")
core = (
    lf.group_by("depth")
    .agg([
        pl.len().alias("count"),
        pl.col("null_margin").mean().alias("avg_margin"),
        (pl.col("null_margin") > 0).mean().alias("cutoff_rate"),
    ])
    .sort("depth")
    .collect(engine="streaming")
)

t_core = time.perf_counter()
total_rows_analyzed = core["count"].sum()
print(f"Core aggregation done in {t_core - t0:.2f}s")
print(f"Total rows in final analysis: {total_rows_analyzed:,}")

# Validate row count consistency
if total_rows_analyzed != final_rows:
    print(f"⚠️  Warning: Row count mismatch! Analysis: {total_rows_analyzed:,}, Expected: {final_rows:,}")

depths_sorted = core["depth"].to_numpy()
n_depths = len(depths_sorted)
avg_margin = core["avg_margin"].to_numpy()
cutoff_rate = core["cutoff_rate"].to_numpy()
counts = core["count"].to_numpy()

# ── 3. Histogram aggregation ─────────────────────────────────────────────────
print("Computing histogram...")
hist_df = (
    lf.with_columns(
        pl.col("null_margin")
        .cut(breaks=BINS[1:-1].tolist(),
             labels=[str(i) for i in range(N_BINS)],
             left_closed=True)
        .alias("bin_idx")
    )
    .group_by(["depth", "bin_idx"])
    .agg(pl.len().alias("bin_count"))
    .collect(engine="streaming")
)

t_hist = time.perf_counter()
print(f"Histogram aggregation done in {t_hist - t_core:.2f}s")

depth_index = {d: i for i, d in enumerate(depths_sorted.tolist())}

hist_matrix = np.zeros((n_depths, N_BINS), dtype=np.int64)
for row in hist_df.iter_rows(named=True):
    di = depth_index.get(row["depth"])
    bi = int(row["bin_idx"]) if row["bin_idx"] is not None else -1
    if di is not None and 0 <= bi < N_BINS:
        hist_matrix[di, bi] = row["bin_count"]

row_sums = hist_matrix.sum(axis=1, keepdims=True)
hist_norm = np.where(row_sums > 0, hist_matrix / row_sums, 0.0)

# ── 4. Eval margin aggregation ────────────────────────────────────────────────
print("Computing eval margin aggregation...")
eval_cutoff = (
    lf.with_columns(
        (pl.col("eval_margin") // EVAL_BIN_SIZE * EVAL_BIN_SIZE)
        .alias("eval_bucket")
    )
    .filter(pl.col("eval_bucket").is_between(EVAL_LO, EVAL_HI))
    .group_by("eval_bucket")
    .agg([
        pl.len().alias("count"),
        (pl.col("null_margin") > 0).mean().alias("cutoff_rate"),
    ])
    .sort("eval_bucket")
    .collect(engine="streaming")
)

t_eval = time.perf_counter()
print(f"Eval margin aggregation done in {t_eval - t_hist:.2f}s")

eval_x = eval_cutoff["eval_bucket"].to_numpy().astype(float) + EVAL_BIN_SIZE / 2
eval_cr = eval_cutoff["cutoff_rate"].to_numpy()

# ── 5. Derived stats ──────────────────────────────────────────────────────────
def zero_crossings_of(y, x):
    crossings = []
    for ci in np.where(np.diff(np.sign(y)))[0]:
        x1, x2 = x[ci], x[ci+1]
        y1, y2 = y[ci], y[ci+1]
        crossings.append(x1 + (0 - y1) * (x2 - x1) / (y2 - y1) if y2 != y1 else x1)
    return crossings

crossing_depths = zero_crossings_of(avg_margin, depths_sorted)
crossing_depths_cutoff = zero_crossings_of(cutoff_rate - 0.5, depths_sorted)
max_cutoff_idx = np.argmax(cutoff_rate)
max_cutoff_depth = depths_sorted[max_cutoff_idx]
max_cutoff_value = cutoff_rate[max_cutoff_idx]

# ── 6. Plot ───────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 6: Generating Visualizations")
print("="*60)
print("Creating plots...")
fig = plt.figure(figsize=(16, 12), facecolor=BG)
fig.suptitle("Null Move Pruning — Search Tree Analysis",
             fontsize=16, fontweight="bold", color=TEXT_C, y=0.98)

gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.28,
              left=0.08, right=0.95, top=0.92, bottom=0.10)
ax0 = fig.add_subplot(gs[0, 0])
ax1 = fig.add_subplot(gs[0, 1])
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[1, 1])

def clean_spines(ax):
    for sp in ax.spines.values():
        sp.set_edgecolor(GRID_C)

# Plot 0 – invocations
bars = ax0.bar(depths_sorted, counts / 1e6, color=ACCENT, alpha=0.85, width=0.75, zorder=3)
peak_i = np.argmax(counts)
bars[peak_i].set_color(ACCENT2)
bars[peak_i].set_alpha(1.0)
ax0.annotate(f"peak: depth {depths_sorted[peak_i]}",
             xy=(depths_sorted[peak_i], counts[peak_i] / 1e6),
             xytext=(depths_sorted[peak_i] + 3, counts[peak_i] / 1e6 * 0.85),
             fontsize=7.5, color=ACCENT2,
             arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=0.8, alpha=0.7))
ax0.set_title("NMP Invocations by Depth")
ax0.set_xlabel("Search Depth")
ax0.set_ylabel("Invocations (M)")
ax0.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
clean_spines(ax0)

# Plot 1 – avg null margin
ax1.plot(depths_sorted, avg_margin, color=ACCENT3, lw=2.0, zorder=3)
ax1.scatter(depths_sorted, avg_margin, color=ACCENT3, s=15, zorder=4, alpha=0.7)
ax1.axhline(0, linestyle="--", color=ZERO_C, lw=1.0, zorder=2, alpha=0.7)
ax1.fill_between(depths_sorted, avg_margin, 0, where=(avg_margin < 0), alpha=0.12, color=ACCENT3)
ax1.fill_between(depths_sorted, avg_margin, 0, where=(avg_margin >= 0), alpha=0.20, color=ACCENT2)
for cd in crossing_depths:
    ax1.axvline(cd, linestyle=":", color=ACCENT2, lw=1.2, alpha=0.6, zorder=5)
if crossing_depths:
    ax1.text(0.02, 0.98, f"Zero crossings: {', '.join(f'{d:.1f}' for d in crossing_depths)}",
             transform=ax1.transAxes, fontsize=6.5, color=ACCENT2, verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG, alpha=0.8))
ax1.set_title("Avg Null Margin by Depth")
ax1.set_xlabel("Search Depth")
ax1.set_ylabel("Avg Null Margin (cp)")
clean_spines(ax1)

# Plot 2 – cutoff success rate
ax2.plot(depths_sorted, cutoff_rate, color=ACCENT, lw=2.0, zorder=3)
ax2.scatter(depths_sorted, cutoff_rate, color=ACCENT, s=15, zorder=4, alpha=0.7)
ax2.axhline(0.5, linestyle="--", color=ACCENT2, lw=1.2, zorder=2, alpha=0.7)
ax2.fill_between(depths_sorted, cutoff_rate, 0.5, where=(cutoff_rate >= 0.5), alpha=0.20, color=ACCENT3)
ax2.fill_between(depths_sorted, cutoff_rate, 0.5, where=(cutoff_rate < 0.5), alpha=0.12, color=ACCENT2)
for cd in crossing_depths_cutoff:
    ax2.axvline(cd, linestyle=":", color=ACCENT2, lw=1.2, alpha=0.6, zorder=5)
ax2.scatter([max_cutoff_depth], [max_cutoff_value], color=ACCENT2, s=60, zorder=7,
            marker='*', edgecolors='white', linewidths=1)
if crossing_depths_cutoff:
    ax2.text(0.02, 0.98, f"50% crossings: {', '.join(f'{d:.1f}' for d in crossing_depths_cutoff)}",
             transform=ax2.transAxes, fontsize=6.5, color=ACCENT2, verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG, alpha=0.8))
ax2.text(0.98, 0.02, f"Max: {max_cutoff_value*100:.1f}% at d={max_cutoff_depth:.0f}",
         transform=ax2.transAxes, fontsize=7, color=ACCENT2,
         horizontalalignment='right', verticalalignment='bottom',
         bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG, alpha=0.8))
ax2.set_ylim(0, 1)
ax2.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
ax2.set_title("Cutoff Success Rate by Depth")
ax2.set_xlabel("Search Depth")
ax2.set_ylabel("Success Rate")
clean_spines(ax2)

# Plot 3 – cutoff rate vs eval margin
ax3.plot(eval_x, eval_cr, color=ACCENT3, lw=2.0, zorder=3)
ax3.scatter(eval_x, eval_cr, color=ACCENT3, s=15, zorder=4, alpha=0.7)
ax3.axhline(0.5, linestyle="--", color=ACCENT2, lw=1.2, zorder=2, alpha=0.7)
ax3.axvline(0, linestyle="--", color=ZERO_C, lw=1.0, zorder=2, alpha=0.7)
ax3.fill_between(eval_x, eval_cr, 0.5, where=(eval_cr >= 0.5), alpha=0.20, color=ACCENT3)
ax3.fill_between(eval_x, eval_cr, 0.5, where=(eval_cr < 0.5), alpha=0.12, color=ACCENT2)
eval_crossings = zero_crossings_of(eval_cr - 0.5, eval_x)
for cd in eval_crossings:
    ax3.axvline(cd, linestyle=":", color=ACCENT2, lw=1.2, alpha=0.6, zorder=5)
if eval_crossings:
    ax3.text(0.02, 0.98, f"50% crossings: {', '.join(f'{d:.0f}cp' for d in eval_crossings)}",
             transform=ax3.transAxes, fontsize=6.5, color=ACCENT2, verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG, alpha=0.8))
ax3.set_ylim(0, 1)
ax3.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
ax3.set_title("Cutoff Success Rate vs Eval Margin")
ax3.set_xlabel("staticEval - beta (cp)")
ax3.set_ylabel("Success Rate")
clean_spines(ax3)

# ── 7. Summary footer ─────────────────────────────────────────────────────────
summary = (f"Avg Margin Zero Crossings: {', '.join(f'{d:.1f}' for d in crossing_depths)} | "
           f"Cutoff 50% Crossings: {', '.join(f'{d:.1f}' for d in crossing_depths_cutoff)} | "
           f"Max Cutoff: {max_cutoff_value*100:.1f}% @ d={max_cutoff_depth:.0f}")
fig.text(0.5, 0.02, summary, fontsize=7, color=MUTED_C, ha='center',
         bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG, edgecolor=GRID_C, alpha=0.8))

# ── 8. Final Statistics Report ─────────────────────────────────────────────────
print("\n" + "="*60)
print("FINAL STATISTICS REPORT")
print("="*60)
print(f"📊 File Statistics:")
print(f"   Total lines in file:        {total_lines:,}")
print(f"   Total data rows:            {total_data_rows:,}")
print(f"")
print(f"📈 Parsing Statistics:")
print(f"   Successfully parsed:        {parsed_rows:,} ({parsed_rows/total_data_rows*100:.6f}%)")
print(f"   Malformed rows skipped:     {malformed_rows:,} ({malformed_rows/total_data_rows*100:.6f}%)")
print(f"   Rows with nulls dropped:    {null_rows_dropped:,} ({null_rows_dropped/total_data_rows*100:.6f}%)")
print(f"   Valid rows for analysis:    {rows_after_dropping_nulls:,} ({rows_after_dropping_nulls/total_data_rows*100:.6f}%)")
print(f"")
print(f"🔍 Filtering Statistics:")
print(f"   After range filters:        {filtered_rows:,}")
if DEDUP:
    print(f"   After deduplication:        {deduped_rows:,}")
    print(f"   Duplicates removed:         {duplicates_removed:,} ({duplicates_removed/filtered_rows*100:.6f}%)")
print(f"   Final rows in analysis:     {total_rows_analyzed:,}")
print(f"")
print(f"🎯 Analysis Results:")
print(f"   Avg Margin Zero Crossings:   {[f'{d:.1f}' for d in crossing_depths]}")
print(f"   Cutoff 50% Crossings:        {[f'{d:.1f}' for d in crossing_depths_cutoff]}")
print(f"   Eval Margin 50% Crossings:   {[f'{d:.0f}cp' for d in eval_crossings]}")
print(f"   Maximum Cutoff Rate:         {max_cutoff_value*100:.1f}% at depth {max_cutoff_depth}")
print("="*60)

out = "nmp_analysis.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG)
print(f"\n✅ Saved {out}  (total execution time: {time.perf_counter() - t0:.2f}s)")
