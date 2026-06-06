# Dashboard Requirements — Workforce Analytics BPO
**Version:** 1.0  
**Tool:** Power BI Desktop (primary) / Excel (alternative)  
**Data source:** `data/workforce_bpo_simulated_data.csv`

---

## How to Open in Power BI

1. Download and install [Power BI Desktop](https://powerbi.microsoft.com/desktop/) (free).
2. Open Power BI Desktop → **Get Data** → **Text/CSV**.
3. Navigate to `data/workforce_bpo_simulated_data.csv` and click **Load**.
4. In the **Transform Data** editor, verify column types:
   - `date` → Date
   - `adherence_pct`, `occupancy_pct`, `service_level_pct` → Decimal Number
   - `contacts_handled`, `worked_minutes`, `shrinkage_minutes` → Whole Number
   - `qa_score`, `csat_score` → Decimal Number
   - `sla_met` → True/False (Boolean)
5. Click **Close & Apply**.

---

## How to Open in Excel

1. Open Excel → **Data** tab → **Get Data** → **From File** → **From Text/CSV**.
2. Select `data/workforce_bpo_simulated_data.csv`.
3. Click **Transform Data** → verify `date` column is parsed as Date.
4. Click **Close & Load**.
5. Use **PivotTables** for the analyses below.

---

## Recommended Dashboard Pages

### Page 1 — Operations Overview (KPI Summary)
| KPI Card | Metric | Target |
|---|---|---|
| Overall Adherence | avg(adherence_pct) where absences=0 | ≥ 90% |
| Shrinkage Rate | avg(shrinkage_minutes / scheduled_minutes) | ≤ 15% |
| SLA Compliance | % of days sla_met = True | ≥ 80% |
| Absence Rate | count(absences=1) / total records | ≤ 5% |
| Avg CSAT | avg(csat_score) where absences=0 | ≥ 80 |
| Avg QA Score | avg(qa_score) where absences=0 | ≥ 85 |

**Visuals:**
- Line chart: adherence_pct trend by week, sliced by campaign
- Bar chart: total contacts_handled by campaign
- Gauge: SLA compliance vs. 80% target

### Page 2 — Adherence & Shrinkage Deep Dive
**Visuals:**
- Heatmap: agent_id vs. week, color = adherence_pct
- Clustered bar: shrinkage_minutes by campaign and shift
- Table: bottom 15 agents by avg adherence (flag at-risk)
- Trend: late_login_minutes by week

**Filters/Slicers:** Campaign | Shift | Date range

### Page 3 — Agent Performance
**Visuals:**
- Scatter plot: avg_adherence_pct (x) vs. avg_qa_score (y), bubble size = contacts_handled
- Bar chart: top 10 agents by productivity score
- Table: agent-level KPI summary (sortable)
- KPI: % agents meeting all targets simultaneously

**Filters/Slicers:** Campaign | Performance tier (top/mid/at-risk)

### Page 4 — SLA & Volume Analysis
**Visuals:**
- Area chart: contacts_handled by date and campaign
- Line chart: service_level_pct by week and campaign
- Bar: sla_met rate by campaign
- Scatter: occupancy_pct vs. average_handle_time_sec (correlation view)

### Page 5 — CSAT & Quality
**Visuals:**
- Line: csat_score and qa_score trends by week
- Scatter: qa_score (x) vs. csat_score (y) by campaign
- Bar: avg csat by shift (identify shift quality gaps)
- Distribution histogram: qa_score

---

## Power BI DAX Measures to Create

```dax
-- Adherence (active agents only)
Avg Adherence % = 
CALCULATE(
    AVERAGE(workforce_bpo_simulated_data[adherence_pct]),
    workforce_bpo_simulated_data[absences] = 0
)

-- Shrinkage Rate
Shrinkage Rate % = 
DIVIDE(
    SUM(workforce_bpo_simulated_data[shrinkage_minutes]),
    SUM(workforce_bpo_simulated_data[scheduled_minutes])
) * 100

-- SLA Compliance
SLA Compliance % = 
CALCULATE(
    COUNTROWS(workforce_bpo_simulated_data),
    workforce_bpo_simulated_data[sla_met] = TRUE()
) / COUNTROWS(workforce_bpo_simulated_data) * 100

-- Absence Rate
Absence Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(workforce_bpo_simulated_data), 
              workforce_bpo_simulated_data[absences] = 1),
    COUNTROWS(workforce_bpo_simulated_data)
) * 100

-- Productivity Score (composite)
Productivity Score = 
CALCULATE(
    AVERAGE(workforce_bpo_simulated_data[contacts_handled]) * 0.35 +
    AVERAGE(workforce_bpo_simulated_data[adherence_pct]) * 0.25 +
    AVERAGE(workforce_bpo_simulated_data[qa_score]) * 0.20 +
    AVERAGE(workforce_bpo_simulated_data[csat_score]) * 0.20,
    workforce_bpo_simulated_data[absences] = 0
)
```

---

## Excel PivotTable Recipes

### Adherence by Week and Campaign
- Rows: week (derived from date)
- Columns: campaign
- Values: average(adherence_pct) — filter absences = 0

### Top Agents by Productivity
- Rows: agent_id, campaign
- Values: average(contacts_handled), average(adherence_pct), average(qa_score)
- Sort: contacts_handled descending, top 10

### Shrinkage Summary
- Rows: campaign, shift
- Values: average(shrinkage_minutes / scheduled_minutes) formatted as %
