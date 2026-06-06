# Executive Summary — Workforce Analytics Dashboard
**Period:** March 8, 2026 – June 5, 2026 (90 days)  
**Scope:** 80 agents | 3 campaigns | ~7,200 daily records  
**Author:** Juan Carlos Mejía Soto  
**Data:** Simulated — for portfolio demonstration only

---

## Problem Statement

Contact centers lose revenue and incur SLA penalties when workforce data exists but no one has translated it into decisions. This analysis simulates the exact scenario: 90 days of raw operational logs across three BPO campaigns, analyzed the same way a WFM Director would review them — with a focus on what is broken, what is at risk, and what to do next.

---

## Dataset Overview

| Metric | Value |
|---|---|
| Total records | 7,200 |
| Date range | 2026-03-08 → 2026-06-05 |
| Agents | 80 (AGT-001 to AGT-080) |
| Campaigns | Tech Support · Billing & Collections · Customer Retention |
| Shifts | Morning · Afternoon · Night (rotating) |

---

## KPI Summary

| KPI | Target | Observed | Status |
|---|---|---|---|
| Schedule Adherence | ≥ 90% | ~88.5% | ⚠ Below target |
| Shrinkage | ≤ 15% | ~15.6% | ⚠ Above budget |
| Average Handle Time | Varies | 360–540 sec | ✓ Within range |
| SLA Compliance (daily) | ≥ 80% of days | ~78% | ⚠ At risk |
| QA Score | ≥ 85 | ~83.5 | ⚠ Near threshold |
| CSAT Score | ≥ 80 | ~78.0 | ⚠ Below target |
| Absence Rate | ≤ 5% | ~4.3% | ✓ On track |

---

## Key Findings

### Adherence — 88.5% vs. 90% target
- Average adherence across all campaigns is **88.5%**, falling short of the 90% benchmark by 1.5 points.
- Approximately **15 agents (19% of workforce)** average below 85% adherence — classified as at-risk for immediate coaching.
- Adherence dips cluster on **Mondays** and in the **Night shift**, exposing peak-hour SLA risk.
- **Week-over-week trend is flat** — no organic improvement without targeted intervention.

### Shrinkage — Exceeds budget across all campaigns
- All three campaigns exceed the 15% shrinkage target: Tech Support (15.9%), Billing & Collections (15.7%), Customer Retention (15.2%).
- Root causes split between **late logins** (tracked via `late_login_minutes`) and **unplanned offline events** embedded in `shrinkage_minutes`.
- Absence rate is on track at 4.3%, but Monday morning spikes suggest structural scheduling gaps.

### SLA Compliance — Tech Support at critical risk
- **Tech Support** hits only ~74% of daily SLA targets vs. the 80% goal — the worst performer.
- The SLA failure is **compound**: lower adherence (fewer agents working) + higher AHT (420+ sec) = insufficient throughput.
- **Billing & Collections** is the only campaign consistently above target (~82% SLA compliance).
- **Customer Retention** sits in a borderline zone at ~79%, susceptible to any Monday absence spike.

### Agent Productivity — High dispersion between top and bottom quartile
- Top 10 agents score 76–80 on composite productivity (adherence × QA × CSAT × contacts).
- **Top-quartile agents handle 35% more contacts per day** than bottom-quartile peers — a gap large enough to justify structural peer coaching.
- High-QA agents (>88) tend to cluster in Customer Retention, suggesting better onboarding or supervision practices.

### Occupancy → AHT → CSAT Cascade
- Days with **occupancy >88%** show an average **+8% AHT increase** (agents rush, make errors, repeat contacts).
- The same high-occupancy days show **−3.5 CSAT points** — directly measurable customer experience degradation.
- This validates the industry-standard 88% occupancy ceiling as a real operational constraint, not an arbitrary guideline.

---

## Risk Register

| Risk | Severity | Probability | Immediate Owner |
|---|---|---|---|
| Tech Support SLA breach this quarter | High | High | WFM Lead + Tech Support Ops Manager |
| 15 agents below 85% adherence → morale/attrition | High | Medium | Supervisors (per agent) |
| Shrinkage budget overrun (all campaigns) | Medium | High | WFM Analyst |
| CSAT below 80 driving contract penalty | High | Medium | Quality + Operations VP |
| Monday staffing gap recurring | Medium | High | Scheduling team |

---

## Recommendations

### Immediate (Week 1–2)
1. **Adherence coaching sprint:** Flag the 15 at-risk agents (see `reports/exports/agent_risk_summary.csv`). Schedule 1:1s with supervisors. Implement intraday adherence alerts in WFM tools.
2. **Tech Support headcount review:** 74% SLA compliance indicates insufficient FTE coverage. Evaluate a +5% buffer during peak weeks, or renegotiate the SLA threshold for complex contact types.
3. **Occupancy cap enforcement:** Route Tech Support contacts at a max 85% occupancy ceiling during the immediate stabilization period. Re-evaluate after adherence improves.

### Short-term (Month 1)
4. **Shrinkage root-cause audit:** Break down shrinkage by type (late logins vs. break overruns vs. system issues) for each campaign. Billing & Collections and Tech Support are the priority.
5. **Monday buffer staffing:** Pre-schedule a 5–8% voluntary standby pool for Monday morning shifts across all campaigns.
6. **Peer mentoring:** Pair top-quartile agents (high QA + high CSAT) with at-risk agents. Target: 8–12% adherence improvement in 30 days per published BPO coaching benchmarks.

### Strategic (Quarter 2+)
7. **Predictive absence model:** Build a lightweight ML model using day-of-week, campaign, and rolling absence patterns to predict high-risk days 72 hours in advance.
8. **Automated daily reporting:** Schedule this pipeline to run nightly, push CSV exports to an S3 bucket, and refresh a Power BI dataset automatically.
9. **Skills-based routing review:** High AHT in Tech Support may indicate routing mismatches. Review agent skill tags and ensure complex contacts are distributed to high-QA agents.

---

## Improvement Actions Tracker

| Action | Owner | Timeline | Success Metric |
|---|---|---|---|
| 1:1 coaching for 15 at-risk agents | Supervisors | Week 1–2 | Adherence >85% for all flagged agents by Day 30 |
| Tech Support FTE review | WFM Lead | Week 2 | SLA compliance >78% by end of Month 1 |
| Occupancy cap at 85% (Tech Support) | Real-Time Analyst | Immediate | Avg AHT reduction of ≥5% within 2 weeks |
| Shrinkage root-cause audit | WFM Analyst | Week 3 | Identify top 2 shrinkage drivers per campaign |
| Monday standby pool setup | Scheduling | Week 2–3 | Monday SLA compliance parity with Tuesday–Friday |
| Peer mentoring program launch | Ops Manager | Month 1 | 10%+ adherence lift in bottom-quartile group |

---

## Methodology Note

All data is **synthetically generated** using Python (NumPy + Pandas). Realistic correlations between metrics (adherence ↔ contacts handled, AHT ↔ CSAT, occupancy ↔ quality) were encoded in the data generation script to mirror patterns observed in real BPO operations.

This project is intended to demonstrate workforce analytics competency. **No proprietary data from any employer was used.**

---

## Artifacts

| Artifact | Location |
|---|---|
| Main dataset | `data/workforce_bpo_simulated_data.csv` |
| Chart — Adherence trend | `assets/charts/weekly_adherence_trend.png` |
| Chart — Shrinkage by campaign | `assets/charts/shrinkage_by_campaign.png` |
| Chart — SLA performance | `assets/charts/sla_performance_by_campaign.png` |
| Chart — Top 10 agents | `assets/charts/top_10_agents_productivity.png` |
| Chart — Occupancy vs CSAT | `assets/charts/occupancy_vs_csat.png` |
| Chart — Adherence risk agents | `assets/charts/adherence_risk_agents.png` |
| Power BI export — weekly adherence | `reports/exports/weekly_adherence.csv` |
| Power BI export — campaign summary | `reports/exports/campaign_summary.csv` |
| Power BI export — agent risk | `reports/exports/agent_risk_summary.csv` |
| Power BI export — top agents | `reports/exports/top_agents.csv` |
