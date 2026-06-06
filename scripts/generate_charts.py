"""
generate_charts.py
Reads workforce_bpo_simulated_data.csv and generates 6 professional PNG charts
plus 4 summary CSVs ready for Power BI import.

Usage: python scripts/generate_charts.py
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, 'data', 'workforce_bpo_simulated_data.csv')
CHARTS_DIR = os.path.join(BASE_DIR, 'assets', 'charts')
EXPORTS_DIR = os.path.join(BASE_DIR, 'reports', 'exports')

os.makedirs(CHARTS_DIR,  exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

# ── Color palette (campaign → hex) ─────────────────────────────────────────────
COLORS = {
    'Tech Support':          '#2196F3',
    'Billing & Collections': '#FF9800',
    'Customer Retention':    '#4CAF50',
}
ALERT  = '#E53935'
PURPLE = '#673AB7'
GREY   = '#9E9E9E'

plt.rcParams.update({
    'figure.facecolor':  '#FAFAFA',
    'axes.facecolor':    '#FAFAFA',
    'axes.edgecolor':    '#CCCCCC',
    'axes.labelcolor':   '#333333',
    'axes.titlesize':    13,
    'axes.labelsize':    11,
    'xtick.labelsize':   9,
    'ytick.labelsize':   9,
    'legend.fontsize':   9,
    'grid.color':        '#E0E0E0',
    'grid.linestyle':    '--',
    'grid.alpha':        0.7,
    'font.family':       'DejaVu Sans',
})

# ── Load & prepare data ────────────────────────────────────────────────────────
print(f"[1/9] Loading {DATA_PATH} ...")
df = pd.read_csv(DATA_PATH, parse_dates=['date'])
df['week_num']   = df['date'].dt.isocalendar().week.astype(int)
df['week_label'] = 'W' + df['week_num'].astype(str)

campaigns = ['Tech Support', 'Billing & Collections', 'Customer Retention']
weeks     = sorted(df['week_label'].unique(), key=lambda w: int(w[1:]))

# Active rows only (exclude full-absence records for metric charts)
df_active = df[df['absences'] == 0].dropna(subset=['adherence_pct']).copy()

# ──────────────────────────────────────────────────────────────────────────────
# CHART 1 — Weekly Adherence Trend
# ──────────────────────────────────────────────────────────────────────────────
print("[2/9] weekly_adherence_trend.png ...")

adh = (df_active
       .groupby(['week_label', 'campaign'])['adherence_pct']
       .mean()
       .reset_index()
       .rename(columns={'adherence_pct': 'avg_adherence_pct'}))
adh_pivot = (adh.pivot(index='week_label', columns='campaign', values='avg_adherence_pct')
               .reindex(weeks))

fig, ax = plt.subplots(figsize=(12, 5))
for camp in campaigns:
    if camp in adh_pivot.columns:
        ax.plot(range(len(weeks)), adh_pivot[camp].values,
                marker='o', markersize=4, linewidth=2,
                label=camp, color=COLORS[camp])

ax.axhline(90, color=ALERT, linestyle='--', linewidth=1.5, label='Target: 90%')
ax.set_title('Weekly Schedule Adherence by Campaign', fontweight='bold', pad=12)
ax.set_xlabel('ISO Week')
ax.set_ylabel('Avg Adherence (%)')
ax.set_ylim(82, 97)
ax.set_xticks(range(len(weeks)))
ax.set_xticklabels(weeks, rotation=45, ha='right', fontsize=8)
ax.legend(loc='lower right')
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'weekly_adherence_trend.png'), dpi=150)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# CHART 2 — Shrinkage & Absence Rate by Campaign
# ──────────────────────────────────────────────────────────────────────────────
print("[3/9] shrinkage_by_campaign.png ...")

shr = df.groupby('campaign').agg(
    total_scheduled_min=('scheduled_minutes',   'sum'),
    total_shrinkage_min=('shrinkage_minutes',    'sum'),
    total_absences=     ('absences',             'sum'),
    total_records=      ('agent_id',             'count'),
).reset_index()
shr['shrinkage_pct']    = shr['total_shrinkage_min'] / shr['total_scheduled_min'] * 100
shr['absence_rate_pct'] = shr['total_absences'] / shr['total_records'] * 100

x     = np.arange(len(shr))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 5))
bars1 = ax.bar(x - width / 2, shr['shrinkage_pct'], width,
               color=[COLORS[c] for c in shr['campaign']], alpha=0.85,
               label='Shrinkage %')
bars2 = ax.bar(x + width / 2, shr['absence_rate_pct'], width,
               color=GREY, alpha=0.75, label='Absence Rate %')

ax.axhline(15, color=ALERT,   linestyle='--', linewidth=1.5, label='Shrinkage Target ≤15%')
ax.axhline(5,  color=PURPLE,  linestyle=':',  linewidth=1.5, label='Absence Target ≤5%')

for bar in list(bars1) + list(bars2):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
            f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=8)

ax.set_title('Shrinkage & Absence Rate by Campaign', fontweight='bold', pad=12)
ax.set_xlabel('Campaign')
ax.set_ylabel('Rate (%)')
ax.set_xticks(x)
ax.set_xticklabels(shr['campaign'], rotation=8)
ax.set_ylim(0, 22)
ax.legend()
ax.grid(True, axis='y')
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'shrinkage_by_campaign.png'), dpi=150)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# CHART 3 — SLA Performance by Campaign
# ──────────────────────────────────────────────────────────────────────────────
print("[4/9] sla_performance_by_campaign.png ...")

sla = (df.groupby(['week_label', 'campaign'])['service_level_pct']
         .mean()
         .reset_index()
         .rename(columns={'service_level_pct': 'avg_sla_pct'}))
sla_pivot = (sla.pivot(index='week_label', columns='campaign', values='avg_sla_pct')
               .reindex(weeks))

fig, ax = plt.subplots(figsize=(12, 5))
for camp in campaigns:
    if camp in sla_pivot.columns:
        vals = sla_pivot[camp].values
        ax.plot(range(len(weeks)), vals, marker='s', markersize=4,
                linewidth=2, label=camp, color=COLORS[camp])

ax.axhline(80, color=ALERT, linestyle='--', linewidth=1.5, label='SLA Target: 80%')
ax.axhspan(0, 80, alpha=0.04, color=ALERT)

ax.set_title('Weekly SLA Performance by Campaign', fontweight='bold', pad=12)
ax.set_xlabel('ISO Week')
ax.set_ylabel('Avg Service Level (%)')
ax.set_ylim(45, 100)
ax.set_xticks(range(len(weeks)))
ax.set_xticklabels(weeks, rotation=45, ha='right', fontsize=8)
ax.legend(loc='upper right')
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'sla_performance_by_campaign.png'), dpi=150)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# CHART 4 — Top 10 Agents Productivity
# ──────────────────────────────────────────────────────────────────────────────
print("[5/9] top_10_agents_productivity.png ...")

agent_stats = (df_active
               .groupby(['agent_id', 'campaign'])
               .agg(
                   avg_contacts= ('contacts_handled',      'mean'),
                   avg_adherence=('adherence_pct',         'mean'),
                   avg_qa=       ('qa_score',              'mean'),
                   avg_csat=     ('csat_score',            'mean'),
                   days_worked=  ('date',                  'count'),
               )
               .reset_index()
               .dropna(subset=['avg_qa', 'avg_csat']))

max_contacts = agent_stats['avg_contacts'].max()
agent_stats['productivity_score'] = (
    agent_stats['avg_adherence'] * 0.30 +
    agent_stats['avg_qa']        * 0.25 +
    agent_stats['avg_csat']      * 0.25 +
    (agent_stats['avg_contacts'] / max_contacts * 100) * 0.20
)

top10 = agent_stats.nlargest(10, 'productivity_score').reset_index(drop=True)

fig, ax = plt.subplots(figsize=(10, 6))
bar_colors = [COLORS[c] for c in top10['campaign']]
bars = ax.barh(top10['agent_id'], top10['productivity_score'],
               color=bar_colors, alpha=0.85, edgecolor='white')

for bar, row in zip(bars, top10.itertuples()):
    ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height() / 2,
            f'{row.productivity_score:.1f}',
            va='center', fontsize=8, fontweight='bold')

ax.set_title('Top 10 Agents — Composite Productivity Score', fontweight='bold', pad=12)
ax.set_xlabel('Productivity Score (0–100)')
ax.set_ylabel('Agent ID')
ax.invert_yaxis()
ax.set_xlim(0, top10['productivity_score'].max() + 7)
ax.grid(True, axis='x')

legend_handles = [mpatches.Patch(color=COLORS[c], label=c)
                  for c in campaigns if c in top10['campaign'].values]
ax.legend(handles=legend_handles, loc='lower right')
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'top_10_agents_productivity.png'), dpi=150)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# CHART 5 — Occupancy % vs. CSAT Score
# ──────────────────────────────────────────────────────────────────────────────
print("[6/9] occupancy_vs_csat.png ...")

occ = (df_active[df_active['occupancy_pct'] > 0]
       .dropna(subset=['csat_score'])
       .copy())
occ_sample = occ.sample(n=min(1500, len(occ)), random_state=42)

fig, ax = plt.subplots(figsize=(10, 6))
for camp in campaigns:
    mask = occ_sample['campaign'] == camp
    ax.scatter(occ_sample.loc[mask, 'occupancy_pct'],
               occ_sample.loc[mask, 'csat_score'],
               color=COLORS[camp], alpha=0.40, s=16, label=camp)

ax.axvline(88, color=ALERT,  linestyle='--', linewidth=1.5, label='Occupancy Cap: 88%')
ax.axhline(80, color='#333', linestyle=':',  linewidth=1.2, label='CSAT Target: 80')

valid = occ_sample.dropna(subset=['occupancy_pct', 'csat_score'])
z = np.polyfit(valid['occupancy_pct'], valid['csat_score'], 1)
p = np.poly1d(z)
x_line = np.linspace(valid['occupancy_pct'].min(), valid['occupancy_pct'].max(), 100)
ax.plot(x_line, p(x_line), color='#212121', linewidth=1.5, alpha=0.6, label='Trend line')

ax.set_title('Occupancy % vs. CSAT Score by Campaign', fontweight='bold', pad=12)
ax.set_xlabel('Occupancy (%)')
ax.set_ylabel('CSAT Score')
ax.legend(loc='upper right', fontsize=8)
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'occupancy_vs_csat.png'), dpi=150)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# CHART 6 — Adherence Risk Agents
# ──────────────────────────────────────────────────────────────────────────────
print("[7/9] adherence_risk_agents.png ...")

risk_all = (df_active
            .groupby(['agent_id', 'campaign'])['adherence_pct']
            .mean()
            .reset_index()
            .rename(columns={'adherence_pct': 'avg_adherence'}))
risk = risk_all[risk_all['avg_adherence'] < 85].nsmallest(15, 'avg_adherence').reset_index(drop=True)

fig, ax = plt.subplots(figsize=(10, 6))
bar_colors = [COLORS[c] for c in risk['campaign']]
bars = ax.barh(risk['agent_id'], risk['avg_adherence'],
               color=bar_colors, alpha=0.85, edgecolor='white')

ax.axvline(85, color=ALERT,    linestyle='--', linewidth=1.5, label='Risk Threshold: 85%')
ax.axvline(90, color='#4CAF50', linestyle=':',  linewidth=1.2, label='Target: 90%')

for bar in bars:
    ax.text(bar.get_width() - 0.6, bar.get_y() + bar.get_height() / 2,
            f'{bar.get_width():.1f}%',
            va='center', ha='right', fontsize=8, color='white', fontweight='bold')

ax.set_title('Agents Below Adherence Threshold (<85%) — Intervention Required',
             fontweight='bold', pad=12)
ax.set_xlabel('Avg Adherence (%)')
ax.set_ylabel('Agent ID')
ax.invert_yaxis()
ax.set_xlim(60, 93)
ax.grid(True, axis='x')

legend_handles = [mpatches.Patch(color=COLORS[c], label=c)
                  for c in campaigns if c in risk['campaign'].values]
legend_handles += [
    mpatches.Patch(color=ALERT,     label='Risk Threshold 85%'),
    mpatches.Patch(color='#4CAF50', label='Target 90%'),
]
ax.legend(handles=legend_handles, loc='lower right', fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'adherence_risk_agents.png'), dpi=150)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# EXPORT CSVs — Power BI ready
# ──────────────────────────────────────────────────────────────────────────────
print("[8/9] Exporting Power BI CSVs ...")

# 1. Weekly adherence
adh.to_csv(os.path.join(EXPORTS_DIR, 'weekly_adherence.csv'), index=False)

# 2. Campaign summary
camp_raw = df.groupby('campaign').agg(
    total_agents=        ('agent_id',             'nunique'),
    total_records=       ('date',                 'count'),
    avg_adherence_pct=   ('adherence_pct',        'mean'),
    avg_occupancy_pct=   ('occupancy_pct',        'mean'),
    avg_aht_sec=         ('average_handle_time_sec', 'mean'),
    avg_qa_score=        ('qa_score',             'mean'),
    avg_csat_score=      ('csat_score',           'mean'),
    avg_sla_pct=         ('service_level_pct',    'mean'),
    total_absences=      ('absences',             'sum'),
    total_shrinkage_min= ('shrinkage_minutes',    'sum'),
    total_scheduled_min= ('scheduled_minutes',    'sum'),
    sla_met_count=       ('sla_met',              'sum'),
).reset_index()
camp_raw['shrinkage_pct']  = camp_raw['total_shrinkage_min'] / camp_raw['total_scheduled_min'] * 100
camp_raw['sla_met_rate']   = camp_raw['sla_met_count'] / camp_raw['total_records'] * 100
camp_raw.round(2).to_csv(os.path.join(EXPORTS_DIR, 'campaign_summary.csv'), index=False)

# 3. Agent risk summary
risk_detail = (df_active
               .groupby(['agent_id', 'campaign'])
               .agg(
                   avg_adherence=    ('adherence_pct', 'mean'),
                   days_worked=      ('date',          'count'),
                   days_below_85=    ('adherence_pct', lambda x: (x < 85).sum()),
                   total_absences=   ('absences',      'sum'),
                   avg_csat=         ('csat_score',    'mean'),
                   avg_qa=           ('qa_score',      'mean'),
               )
               .reset_index())
risk_detail['pct_days_below_85'] = (
    risk_detail['days_below_85'] / risk_detail['days_worked'] * 100
).round(1)
risk_detail['risk_flag'] = risk_detail['avg_adherence'] < 85
risk_detail.round(2).to_csv(os.path.join(EXPORTS_DIR, 'agent_risk_summary.csv'), index=False)

# 4. Top agents
top10[['agent_id', 'campaign', 'productivity_score',
       'avg_contacts', 'avg_adherence', 'avg_qa', 'avg_csat',
       'days_worked']].round(2).to_csv(os.path.join(EXPORTS_DIR, 'top_agents.csv'), index=False)

print("[9/9] Done.")
print()
print("  Charts  →", CHARTS_DIR)
print("    weekly_adherence_trend.png")
print("    shrinkage_by_campaign.png")
print("    sla_performance_by_campaign.png")
print("    top_10_agents_productivity.png")
print("    occupancy_vs_csat.png")
print("    adherence_risk_agents.png")
print()
print("  Exports →", EXPORTS_DIR)
print("    weekly_adherence.csv")
print("    campaign_summary.csv")
print("    agent_risk_summary.csv")
print("    top_agents.csv")
