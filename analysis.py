"""UK household spending by category, from ONS quarterly data.

Reads data/ons_household_spending.csv, works out quarter-on-quarter,
year-on-year and since-Q4-2019 change for each spending group, and
writes two charts to charts/ and a table to data/growth_by_category.csv.
"""
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/ons_household_spending.csv")
wide = df.pivot(index="quarter", columns="category", values="real_spending_gbp_million").sort_index()

latest, prev, year_ago, base = wide.index[-1], wide.index[-2], wide.index[-5], wide.index[0]


def change(ref):
    return ((wide.loc[latest] / wide.loc[ref] - 1) * 100).round(1)


growth = pd.DataFrame(
    {
        "level_gbp_million": wide.loc[latest],
        "qoq_pct": change(prev),
        "yoy_pct": change(year_ago),
        "since_q4_2019_pct": change(base),
    }
)
growth = pd.concat([growth.loc[["Total"]], growth.drop("Total").sort_values("yoy_pct", ascending=False)])
growth.to_csv("data/growth_by_category.csv")
print(f"Latest quarter: {latest}")
print(growth.to_string())

# Chart 1: year-on-year change by category
bars = growth.drop("Total").sort_values("yoy_pct")
fig, ax = plt.subplots(figsize=(7, 5))
ax.barh(bars.index, bars["yoy_pct"], color=["#b3261e" if v < 0 else "#2f6f8f" for v in bars["yoy_pct"]])
for y, v in enumerate(bars["yoy_pct"]):
    ax.text(v + (0.15 if v >= 0 else -0.15), y, f"{v:+.1f}", va="center", ha="left" if v >= 0 else "right", fontsize=8)
ax.axvline(0, color="#555", lw=0.8)
ax.set_xlabel(f"Change in real spending, {latest} vs {year_ago} (%)")
ax.set_title("UK household spending by category, year on year")
ax.margins(x=0.12)
fig.tight_layout()
fig.savefig("charts/yoy_by_category.png", dpi=150)

# Chart 2: index against Q4 2019
index = wide / wide.loc[base] * 100
fig, ax = plt.subplots(figsize=(7, 4.5))
for col in ["Total", "Communication", "Education", "Restaurants & hotels", "Alcohol & tobacco"]:
    ax.plot(index.index, index[col], lw=2.5 if col == "Total" else 1.6, label=col)
ax.axhline(100, color="#999", lw=0.8, ls="--")
ticks = [q for q in index.index if q.endswith("Q1")]
ax.set_xticks(ticks)
ax.set_xticklabels([q[:4] for q in ticks])
ax.set_ylabel(f"Real spending, {base} = 100")
ax.set_title("Real household spending against Q4 2019")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig("charts/index_since_q4_2019.png", dpi=150)
