"""Paper tables and figures, generated only from reports/tables/*.csv and the processed data.

Usage: PYTHONPATH=. python src/reporting_paper.py
Output: reports/paper/tables.md, reports/paper/fig*.png
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.utils.paths import FEATURES_DAILY_PARQUET, REPORTS_DIR, TABLES_DIR

OUT = REPORTS_DIR / "paper"
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3de"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "text.color": INK, "xtick.color": MUTED,
                     "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 100,
                     "savefig.dpi": 200, "savefig.bbox": "tight"})
t = lambda name: pd.read_csv(TABLES_DIR / f"{name}.csv")


def forest():
    r = t("reddit_robustness")
    rows = []
    for m, lab in (("weighted", "Score-weighted"), ("unweighted", "Unweighted"), ("unweighted_exwsb", "Unweighted, no r/wallstreetbets")):
        for spec, y, d in (("outcome", "d10y_bp", "10y"), ("with_2y", "d10y_bp", "10y, controlling for 2y"), ("outcome", "d2y_bp", "2y"), ("outcome", "dslope_bp", "10y-2y slope")):
            x = r[(r.measure == m) & (r.spec == spec) & (r.outcome == y) & (r["var"] == "r")].iloc[0]
            rows.append((lab, d, x.coef_bp_per_sd, x.se))
    fig, axs = plt.subplots(1, 3, figsize=(9.5, 2.6), sharex=True, sharey=True)
    for ax, lab in zip(axs, dict.fromkeys(r_[0] for r_ in rows)):
        sub = [x for x in rows if x[0] == lab][::-1]
        for i, (_, d, b, se) in enumerate(sub):
            ax.plot([b - 1.96 * se, b + 1.96 * se], [i, i], color=BLUE, lw=2)
            ax.plot(b, i, "o", color=BLUE, ms=8, mec="white", mew=1.5)
        ax.axvline(0, color=MUTED, lw=0.8)
        ax.set_yticks(range(len(sub)), [x[1] for x in sub])
        ax.set_title(lab, fontsize=9, loc="left")
        ax.grid(axis="x", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    fig.supxlabel("Same-day change (bp) per 1 SD of Reddit tone, 95% CI", fontsize=9, color=MUTED, y=-0.04)
    fig.savefig(OUT / "fig1_reddit_tone.png")
    plt.close(fig)


def leadlag():
    r = t("lead_lag").query("window == '2025+'")
    panels = [("reddit_tone", "Reddit tone"), ("reddit_dir", "Reddit direction"), ("press_timed_dir", "Press direction, clock times"),
              ("press_placeholder_dir", "Press direction, date only*")]
    fig, axs = plt.subplots(1, 4, figsize=(11, 2.8), sharey=True)
    for ax, (m, lab) in zip(axs, panels):
        g = r[r.measure == m].sort_values("k")
        ax.errorbar(g.k, g.coef_bp_per_sd, yerr=1.96 * g.se, fmt="o", color=BLUE, ms=7, mec="white", mew=1.2, elinewidth=2)
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_title(f"{lab}\n(n={int(g.n.max())})", fontsize=8.5, loc="left")
        ax.set_xticks(range(-2, 3))
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    axs[0].set_ylabel("bp per 1 SD")
    fig.supxlabel("Yield change on day t+k, text on day t.  k<0: text follows yields.  *dated to the next yield day by construction", fontsize=8.5, color=MUTED, y=-0.06)
    fig.savefig(OUT / "fig2_lead_lag.png")
    plt.close(fig)


def events():
    r = t("event_study")
    fig, ax = plt.subplots(figsize=(5, 3))
    x = range(len(r))
    for off, c, lab, col in ((-0.17, "event_mean_bp", f"Macro release (n={r.n_events.iloc[0]})", BLUE), (0.17, "baseline_mean_bp", "Same clock time, no event", ORANGE)):
        bars = ax.bar([i + off for i in x], r[c], width=0.3, color=col, label=lab)
        ax.bar_label(bars, fmt="%.1f", fontsize=8, color=INK, padding=2)
    ax.set_xticks(list(x), [f"{h} min" for h in r.horizon_min])
    ax.set_ylabel("Mean |10y futures move| (bp of price)")
    ax.set_ylim(0, r.event_mean_bp.max() * 1.3)
    ax.legend(frameon=False, fontsize=8, loc="upper left", ncols=2)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.savefig(OUT / "fig3_event_study.png")
    plt.close(fig)


def coverage():
    f = pd.read_parquet(FEATURES_DAILY_PARQUET).set_index("date").loc["2025-01-01":]
    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    m = f.n_press.groupby(f.index.to_period("M")).sum()
    ax.bar(range(len(m)), m, color=BLUE, width=0.75)
    ax.set_xticks(range(0, len(m), 3), [p.strftime("%b %Y") for p in m.index[::3]])
    ax.set_ylabel("Press articles per month")
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.savefig(OUT / "fig4_press_coverage.png")
    plt.close(fig)


def md(df, cols):
    df = df[cols].copy()
    for c in df.select_dtypes("number"):
        df[c] = df[c].map(lambda v: "" if pd.isna(v) else (f"{int(v):,}" if c in ("n", "n_events", "n_baseline", "horizon_min", "k") else ("<0.001" if c.startswith("p") and v < 0.001 else f"{v:.3f}")))
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + ["| " + " | ".join(map(str, r)) + " |" for r in df.fillna("").values])


def tables():
    d, r, w, h, e, c, l = (t(x) for x in ("daily_regression", "reddit_robustness", "news_vs_reddit_windows", "hourly_regression", "event_study", "yield_direction_eval", "lead_lag"))
    std = ["coef_bp_per_sd", "se", "p", "p_holm", "n"]
    S = ["# Paper tables (auto-generated; do not edit)", "",
         "## T1 Daily 10y, news and Reddit, 2025+", md(d[d.spec == "news_vs_reddit_2025+"], ["controls", "var", *std]), "",
         "## T2 Long news-only sample", md(d[d.spec == "news_only"], ["controls", "var", *std]), "",
         "## T3 News vs. Reddit by window (joint block tests)", md(w[w.kind == "block"], ["window", "controls", "var", "p", "p_holm", "n"]), "",
         "## T4 Main window 2025-11-24+, coefficients", md(w[(w.kind == "coef") & w.window.str.contains("main") & (w.news_set == "press")], ["controls", "var", *std[:-1], "mde80", "n"]), "",
         "## T5 Reddit robustness", md(r, ["measure", "spec", "outcome", "var", *std]), "",
         "## T6 Lead/lag, 2025+", md(l[l.window == "2025+"], ["measure", "k", *std]), "",
         "## T7 Out of sample", md(d[d.spec.str.startswith("oos")].rename(columns={"coef_bp_per_sd": "value"}), ["spec", "controls", "var", "value", "n"]), "",
         "## T8 Hourly, predictive horizons", md(h[h.outcome.isin(["y1", "y2", "y4"])], ["spec", "outcome", "var", *std]), "",
         "## T9 Event study", md(e, ["horizon_min", "n_events", "n_baseline", "event_mean_bp", "baseline_mean_bp", "slot_matched_diff_bp", "perm_p_one_sided"]), "",
         "## T10 Yield-direction classifier vs. hand labels", md(c, ["model", "A_hand_macro_f1", "A_hand_ci_lo", "A_hand_ci_hi", "A_hand_kappa", "A_hand_down_f1", "C_batch3_macro_f1"]), ""]
    (OUT / "tables.md").write_text("\n".join(S))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in (forest, leadlag, events, coverage, tables):
        fn()
    print(f"wrote {sorted(p.name for p in OUT.iterdir())}")
