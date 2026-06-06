"""
Workforce BPO Analysis Script
Generates the 7 core analytics outputs from the simulated dataset.
Run after generate_workforce_data.py.
"""

import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "workforce_bpo_simulated_data.csv")
REPORTS_DIR = os.path.join(SCRIPT_DIR, "..", "reports")


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["week_label"] = "W" + df["week"].astype(str).str.zfill(2)
    df["month"] = df["date"].dt.month_name()
    return df


# ── Analysis 1: Adherence Trend by Week ───────────────────────────────────────
def analysis_adherence_trend(df: pd.DataFrame) -> pd.DataFrame:
    active = df[df["absences"] == 0].copy()
    trend = (
        active.groupby(["week_label", "campaign"])["adherence_pct"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"adherence_pct": "avg_adherence_pct"})
    )
    return trend


# ── Analysis 2: Shrinkage by Campaign ─────────────────────────────────────────
def analysis_shrinkage_by_campaign(df: pd.DataFrame) -> pd.DataFrame:
    shrinkage = (
        df.groupby("campaign")
        .agg(
            total_scheduled_min=("scheduled_minutes", "sum"),
            total_shrinkage_min=("shrinkage_minutes", "sum"),
            total_absences=("absences", "sum"),
            total_late_login_min=("late_login_minutes", "sum"),
        )
        .reset_index()
    )
    shrinkage["shrinkage_pct"] = (
        shrinkage["total_shrinkage_min"] / shrinkage["total_scheduled_min"] * 100
    ).round(2)
    shrinkage["absence_rate_pct"] = (
        shrinkage["total_absences"] / (df.groupby("campaign").size().values) * 100
    ).round(2)
    return shrinkage


# ── Analysis 3: Top 10 Agents by Productivity ─────────────────────────────────
def analysis_top_agents(df: pd.DataFrame) -> pd.DataFrame:
    active = df[df["absences"] == 0].copy()
    agent_stats = (
        active.groupby(["agent_id", "campaign"])
        .agg(
            avg_contacts=("contacts_handled", "mean"),
            avg_adherence=("adherence_pct", "mean"),
            avg_qa=("qa_score", "mean"),
            avg_csat=("csat_score", "mean"),
            total_contacts=("contacts_handled", "sum"),
            days_worked=("date", "count"),
        )
        .reset_index()
    )
    # Composite productivity score: weighted average
    agent_stats["productivity_score"] = (
        agent_stats["avg_contacts"] * 0.35
        + agent_stats["avg_adherence"] * 0.25
        + agent_stats["avg_qa"] * 0.20
        + agent_stats["avg_csat"] * 0.20
    ).round(2)
    top10 = agent_stats.nlargest(10, "productivity_score")[
        [
            "agent_id", "campaign", "productivity_score",
            "avg_contacts", "avg_adherence", "avg_qa", "avg_csat", "days_worked",
        ]
    ].round(2)
    return top10.reset_index(drop=True)


# ── Analysis 4: Agents at Risk (low adherence) ────────────────────────────────
def analysis_agents_at_risk(df: pd.DataFrame, threshold: float = 85.0) -> pd.DataFrame:
    active = df[df["absences"] == 0].copy()
    agent_avg = (
        active.groupby(["agent_id", "campaign"])
        .agg(
            avg_adherence=("adherence_pct", "mean"),
            days_below_threshold=("adherence_pct", lambda x: (x < threshold).sum()),
            total_days=("date", "count"),
        )
        .reset_index()
    )
    absence_counts = (
        df.groupby("agent_id")["absences"].sum()
        .reset_index()
        .rename(columns={"absences": "total_absences"})
    )
    agent_avg = agent_avg.merge(absence_counts, on="agent_id", how="left")
    agent_avg["pct_days_below"] = (
        agent_avg["days_below_threshold"] / agent_avg["total_days"] * 100
    ).round(1)
    at_risk = agent_avg[agent_avg["avg_adherence"] < threshold].sort_values("avg_adherence")
    return at_risk[
        ["agent_id", "campaign", "avg_adherence", "days_below_threshold",
         "pct_days_below", "total_absences"]
    ].round(2).reset_index(drop=True)


# ── Analysis 5: Campaign SLA Performance ──────────────────────────────────────
def analysis_sla_performance(df: pd.DataFrame) -> pd.DataFrame:
    active = df[df["absences"] == 0].copy()
    sla = (
        active.groupby(["campaign", "week_label"])
        .agg(
            avg_service_level=("service_level_pct", "mean"),
            sla_met_pct=("sla_met", lambda x: x.mean() * 100),
            total_contacts=("contacts_handled", "sum"),
        )
        .round(2)
        .reset_index()
    )
    return sla


# ── Analysis 6: Occupancy, AHT and CSAT Correlation ──────────────────────────
def analysis_occupancy_aht_csat(df: pd.DataFrame) -> pd.DataFrame:
    active = df[df["absences"] == 0].copy()
    # Bin occupancy
    active["occupancy_band"] = pd.cut(
        active["occupancy_pct"],
        bins=[0, 70, 80, 85, 90, 100],
        labels=["<70%", "70-80%", "80-85%", "85-90%", ">90%"],
    )
    correlation = (
        active.groupby("occupancy_band", observed=True)
        .agg(
            avg_aht_sec=("average_handle_time_sec", "mean"),
            avg_csat=("csat_score", "mean"),
            avg_adherence=("adherence_pct", "mean"),
            n_records=("date", "count"),
        )
        .round(2)
        .reset_index()
    )

    # Pearson correlations
    corr_occ_aht = active["occupancy_pct"].corr(active["average_handle_time_sec"])
    corr_occ_csat = active["occupancy_pct"].corr(active["csat_score"])
    corr_aht_csat = active["average_handle_time_sec"].corr(active["csat_score"])

    print(
        f"\n  Correlation occupancy vs AHT:  {corr_occ_aht:+.3f}"
    )
    print(f"  Correlation occupancy vs CSAT: {corr_occ_csat:+.3f}")
    print(f"  Correlation AHT vs CSAT:       {corr_aht_csat:+.3f}")
    return correlation


# ── Analysis 7: Executive Recommendations ─────────────────────────────────────
def generate_executive_recommendations(
    df: pd.DataFrame,
    shrinkage: pd.DataFrame,
    at_risk: pd.DataFrame,
    sla: pd.DataFrame,
) -> list[str]:
    active = df[df["absences"] == 0]
    overall_adherence = active["adherence_pct"].mean()
    overall_shrinkage = shrinkage["shrinkage_pct"].mean()
    n_at_risk = len(at_risk)
    sla_met_overall = active["sla_met"].mean() * 100

    recs = []

    if overall_adherence < 90:
        recs.append(
            f"ADHERENCE ALERT: Overall adherence is {overall_adherence:.1f}% (target ≥90%). "
            "Recommend immediate coaching sessions and intraday schedule review."
        )
    else:
        recs.append(
            f"Adherence is healthy at {overall_adherence:.1f}%. Maintain current monitoring cadence."
        )

    if overall_shrinkage > 15:
        recs.append(
            f"SHRINKAGE RISK: Average shrinkage at {overall_shrinkage:.1f}% exceeds the 15% budget. "
            "Audit unplanned offline time and review break scheduling policies."
        )

    if n_at_risk > 5:
        recs.append(
            f"{n_at_risk} agents flagged as at-risk (adherence <85%). "
            "Prioritize 1:1 performance reviews for the bottom quartile."
        )

    if sla_met_overall < 80:
        worst_campaign = sla.groupby("campaign")["sla_met_pct"].mean().idxmin()
        recs.append(
            f"SLA BREACH RISK: Only {sla_met_overall:.1f}% of daily SLA targets are met. "
            f"'{worst_campaign}' is the weakest campaign — consider headcount adjustment or schedule rebalancing."
        )
    else:
        recs.append(
            f"SLA compliance at {sla_met_overall:.1f}%. Monitor '{sla.groupby('campaign')['sla_met_pct'].mean().idxmin()}' campaign for deterioration."
        )

    recs.append(
        "Implement a predictive absence model using historical patterns to pre-staff buffer "
        "capacity on high-absence days (typically Mondays and Fridays)."
    )
    recs.append(
        "Prioritize agents with high CSAT + high QA scores for mentoring newer agents — "
        "peer coaching programs show 8-12% adherence improvement in comparable BPO environments."
    )

    return recs


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("WORKFORCE BPO ANALYTICS — ANALYSIS REPORT")
    print("=" * 60)

    df = load_data()
    print(f"\nDataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Date range: {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"Agents: {df['agent_id'].nunique()} | Campaigns: {df['campaign'].nunique()}")

    # ── 1. Adherence trend
    print("\n[1/7] Adherence Trend by Week (avg %)")
    trend = analysis_adherence_trend(df)
    pivot_trend = trend.pivot(index="week_label", columns="campaign", values="avg_adherence_pct")
    print(pivot_trend.tail(5).to_string())

    # ── 2. Shrinkage
    print("\n[2/7] Shrinkage by Campaign")
    shrinkage = analysis_shrinkage_by_campaign(df)
    print(shrinkage[["campaign", "shrinkage_pct", "absence_rate_pct"]].to_string(index=False))

    # ── 3. Top 10 Agents
    print("\n[3/7] Top 10 Agents by Productivity Score")
    top10 = analysis_top_agents(df)
    print(top10[["agent_id", "campaign", "productivity_score", "avg_contacts", "avg_adherence"]].to_string(index=False))

    # ── 4. At-Risk Agents
    print("\n[4/7] Agents at Risk (avg adherence < 85%)")
    at_risk = analysis_agents_at_risk(df)
    print(f"  Found {len(at_risk)} agents at risk")
    if len(at_risk) > 0:
        print(at_risk.head(10).to_string(index=False))

    # ── 5. SLA Performance
    print("\n[5/7] Campaign SLA Performance (weekly)")
    sla = analysis_sla_performance(df)
    sla_summary = sla.groupby("campaign")[["avg_service_level", "sla_met_pct"]].mean().round(2)
    print(sla_summary.to_string())

    # ── 6. Occupancy / AHT / CSAT correlation
    print("\n[6/7] Occupancy, AHT, and CSAT Relationship")
    occ_aht_csat = analysis_occupancy_aht_csat(df)
    print(occ_aht_csat.to_string(index=False))

    # ── 7. Executive Recommendations
    print("\n[7/7] Executive Recommendations")
    recs = generate_executive_recommendations(df, shrinkage, at_risk, sla)
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec}")

    # ── Save summary outputs as CSV ───────────────────────────────────────────
    os.makedirs(REPORTS_DIR, exist_ok=True)
    trend.to_csv(os.path.join(REPORTS_DIR, "adherence_trend.csv"), index=False)
    shrinkage.to_csv(os.path.join(REPORTS_DIR, "shrinkage_by_campaign.csv"), index=False)
    top10.to_csv(os.path.join(REPORTS_DIR, "top10_agents.csv"), index=False)
    at_risk.to_csv(os.path.join(REPORTS_DIR, "agents_at_risk.csv"), index=False)
    sla.to_csv(os.path.join(REPORTS_DIR, "sla_performance.csv"), index=False)
    occ_aht_csat.to_csv(os.path.join(REPORTS_DIR, "occupancy_aht_csat.csv"), index=False)

    print("\n✓ Analysis CSVs saved to reports/")
    print("=" * 60)


if __name__ == "__main__":
    main()
