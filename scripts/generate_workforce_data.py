"""
Workforce BPO Simulated Data Generator
Generates 90 days of realistic BPO operational data for 80 agents across 3 campaigns.
All data is synthetic — no real company or employee information.
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

# ── Configuration ──────────────────────────────────────────────────────────────
SEED = 42
N_AGENTS = 80
N_DAYS = 90
START_DATE = date(2026, 3, 8)

CAMPAIGNS = {
    "Tech Support": {
        "agents": list(range(1, 31)),          # agents 001-030
        "base_aht_sec": 420,
        "base_contacts": 45,
        "sla_target": 0.80,
        "qa_mean": 82.0,
        "csat_mean": 78.0,
    },
    "Billing & Collections": {
        "agents": list(range(31, 61)),         # agents 031-060
        "base_aht_sec": 360,
        "base_contacts": 55,
        "sla_target": 0.85,
        "qa_mean": 85.0,
        "csat_mean": 72.0,
    },
    "Customer Retention": {
        "agents": list(range(61, 81)),         # agents 061-080
        "base_aht_sec": 540,
        "base_contacts": 35,
        "sla_target": 0.75,
        "qa_mean": 88.0,
        "csat_mean": 84.0,
    },
}

SHIFTS = ["Morning (06:00-14:00)", "Afternoon (14:00-22:00)", "Night (22:00-06:00)"]
SCHEDULED_MINUTES = 480  # 8-hour shift

rng = np.random.default_rng(SEED)


def assign_shift(agent_id: int, day_of_week: int) -> str:
    """Rotate shifts weekly per agent group."""
    week_offset = (agent_id % 3 + day_of_week) % 3
    return SHIFTS[week_offset]


def generate_agent_profile(agent_id: int) -> dict:
    """Create a persistent performance profile for each agent."""
    return {
        "adherence_base": rng.uniform(0.80, 0.99),
        "aht_multiplier": rng.uniform(0.85, 1.20),
        "qa_bias": rng.uniform(-8, 8),
        "csat_bias": rng.uniform(-6, 6),
        "absence_rate": rng.uniform(0.01, 0.08),
        "late_login_propensity": rng.uniform(0, 0.15),
        "overtime_propensity": rng.uniform(0, 0.20),
    }


def generate_daily_row(
    date_val: date,
    agent_id: int,
    campaign: str,
    campaign_cfg: dict,
    profile: dict,
) -> dict:
    absence = int(rng.random() < profile["absence_rate"])

    if absence:
        # Absent agent: minimal/zero metrics
        return {
            "date": date_val.isoformat(),
            "agent_id": f"AGT-{agent_id:03d}",
            "campaign": campaign,
            "shift": assign_shift(agent_id, date_val.weekday()),
            "scheduled_minutes": SCHEDULED_MINUTES,
            "worked_minutes": 0,
            "adherence_pct": 0.0,
            "shrinkage_minutes": SCHEDULED_MINUTES,
            "occupancy_pct": 0.0,
            "contacts_handled": 0,
            "average_handle_time_sec": 0,
            "qa_score": None,
            "csat_score": None,
            "absences": 1,
            "late_login_minutes": 0,
            "overtime_minutes": 0,
            "service_level_pct": 0.0,
            "sla_met": False,
        }

    # Adherence — daily variation ±5pp around agent base
    adherence_pct = float(
        np.clip(profile["adherence_base"] + rng.normal(0, 0.025), 0.60, 1.00)
    )
    worked_minutes = round(SCHEDULED_MINUTES * adherence_pct)

    # Shrinkage: time not productive (breaks, trainings, offline)
    shrinkage_base = SCHEDULED_MINUTES * rng.uniform(0.08, 0.18)
    shrinkage_minutes = round(min(shrinkage_base, SCHEDULED_MINUTES - worked_minutes + shrinkage_base * 0.3))

    # Occupancy: proportion of worked time spent on contacts
    occupancy_pct = float(np.clip(rng.normal(0.82, 0.05), 0.65, 0.96))

    # AHT with agent multiplier and day-of-week variation
    dow_factor = 1.05 if date_val.weekday() == 0 else 1.0  # Mondays busier
    aht_sec = round(
        campaign_cfg["base_aht_sec"] * profile["aht_multiplier"] * dow_factor
        + rng.normal(0, 20)
    )
    aht_sec = max(60, aht_sec)

    # Contacts handled derived from occupancy and AHT
    productive_minutes = worked_minutes * occupancy_pct
    contacts_handled = max(0, round(productive_minutes * 60 / aht_sec))
    # Add realistic noise
    contacts_handled = max(0, contacts_handled + rng.integers(-3, 4))

    # QA score — correlated with AHT (higher AHT can mean more thorough service)
    aht_qa_bonus = (aht_sec - campaign_cfg["base_aht_sec"]) / 100
    qa_score = float(
        np.clip(
            rng.normal(campaign_cfg["qa_mean"] + profile["qa_bias"] + aht_qa_bonus, 4),
            50, 100,
        )
    )

    # CSAT — correlated with QA and AHT (very long calls reduce satisfaction)
    aht_csat_penalty = max(0, (aht_sec - campaign_cfg["base_aht_sec"] * 1.3) / 200)
    csat_score = float(
        np.clip(
            rng.normal(
                campaign_cfg["csat_mean"]
                + profile["csat_bias"]
                + (qa_score - campaign_cfg["qa_mean"]) * 0.3
                - aht_csat_penalty,
                5,
            ),
            40, 100,
        )
    )

    # Late login
    is_late = rng.random() < profile["late_login_propensity"]
    late_login_minutes = round(rng.uniform(1, 25)) if is_late else 0

    # Overtime
    has_overtime = rng.random() < profile["overtime_propensity"]
    overtime_minutes = round(rng.uniform(15, 60)) if has_overtime else 0

    # Service level — influenced by adherence, occupancy, and campaign target
    sl_base = campaign_cfg["sla_target"] + (adherence_pct - 0.90) * 0.5
    service_level_pct = float(np.clip(rng.normal(sl_base, 0.07), 0.40, 1.00))
    sla_met = bool(service_level_pct >= campaign_cfg["sla_target"])

    return {
        "date": date_val.isoformat(),
        "agent_id": f"AGT-{agent_id:03d}",
        "campaign": campaign,
        "shift": assign_shift(agent_id, date_val.weekday()),
        "scheduled_minutes": SCHEDULED_MINUTES,
        "worked_minutes": worked_minutes,
        "adherence_pct": round(adherence_pct * 100, 2),
        "shrinkage_minutes": shrinkage_minutes,
        "occupancy_pct": round(occupancy_pct * 100, 2),
        "contacts_handled": contacts_handled,
        "average_handle_time_sec": aht_sec,
        "qa_score": round(qa_score, 1),
        "csat_score": round(csat_score, 1),
        "absences": absence,
        "late_login_minutes": late_login_minutes,
        "overtime_minutes": overtime_minutes,
        "service_level_pct": round(service_level_pct * 100, 2),
        "sla_met": sla_met,
    }


def main():
    print("Generating simulated BPO workforce data...")

    agent_profiles = {i: generate_agent_profile(i) for i in range(1, N_AGENTS + 1)}

    rows = []
    dates = [START_DATE + timedelta(days=d) for d in range(N_DAYS)]

    for campaign, cfg in CAMPAIGNS.items():
        for agent_id in cfg["agents"]:
            profile = agent_profiles[agent_id]
            for day in dates:
                rows.append(generate_daily_row(day, agent_id, campaign, cfg, profile))

    df = pd.DataFrame(rows)

    # Ensure correct dtypes
    df["date"] = pd.to_datetime(df["date"])
    df["sla_met"] = df["sla_met"].astype(bool)

    output_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "workforce_bpo_simulated_data.csv"
    )
    output_path = os.path.normpath(output_path)
    df.to_csv(output_path, index=False)

    print(f"Dataset saved to: {output_path}")
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Agents: {df['agent_id'].nunique()}")
    print(f"Campaigns: {df['campaign'].unique().tolist()}")
    print(f"Absence rate: {df['absences'].mean():.2%}")
    print("\nSample adherence by campaign:")
    print(
        df[df["absences"] == 0]
        .groupby("campaign")["adherence_pct"]
        .agg(["mean", "min", "max"])
        .round(2)
    )


if __name__ == "__main__":
    main()
