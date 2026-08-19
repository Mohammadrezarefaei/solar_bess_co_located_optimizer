"""Streamlit App: Co-located Solar PV + BESS Dispatch Optimizer."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import streamlit as st

st.set_page_config(
    page_title="Co-located Solar + BESS Dispatch Optimizer",
    page_icon="☀️",
    layout="wide",
)

st.title("☀️🔋 Co-located Solar + BESS Dispatch Optimizer")
st.markdown(
    "Linear Programming (**HiGHS Solver**) for joint optimization of Solar PV"
    " generation and Battery Storage under **Grid Export Capacity"
    " Bottlenecks**."
)

st.sidebar.header("⚙️ System Technical Ratings")
solar_peak_mw = st.sidebar.slider("Solar PV Plant Peak (MWp)", 5.0, 40.0, 20.0, 1.0)
grid_cap_mw = st.sidebar.slider(
    "Grid Interconnection Limit (MW)", 3.0, 25.0, 10.0, 1.0
)
bess_power_mw = st.sidebar.slider("BESS Inverter Power (MW)", 1.0, 15.0, 5.0, 0.5)
bess_cap_mwh = st.sidebar.slider("BESS Energy Capacity (MWh)", 2.0, 40.0, 10.0, 1.0)
bess_rte = st.sidebar.slider("Round-Trip Efficiency (%)", 75, 96, 90, 1) / 100.0

# 24-Hour Synthetic Benchmark Profiles
hours = np.arange(24)
solar_profile = np.clip(
    solar_peak_mw * np.sin(np.pi * (hours - 5) / 14), 0, None
)
solar_profile = np.where((hours >= 6) & (hours <= 19), solar_profile, 0.0)

# Typical German Day-Ahead Price Profile with midday solar dip and evening peak
day_ahead_prices = [
    55,
    48,
    45,
    42,
    46,
    58,
    75,
    88,
    65,
    40,
    15,
    -5,
    -12,
    8,
    30,
    60,
    95,
    135,
    145,
    120,
    90,
    75,
    65,
    58,
]

# High-performance dispatch optimization engine
T = 24
prices = np.array(day_ahead_prices)
c = np.zeros(4 * T)
c[0:T] = -prices
c[2 * T : 3 * T] = -prices

A_ub, b_ub, A_eq, b_eq = [], [], [], []
eta_ch = np.sqrt(bess_rte)
eta_dis = np.sqrt(bess_rte)

for t in range(T):
  # Grid limit constraint
  row_grid = np.zeros(4 * T)
  row_grid[t] = 1.0
  row_grid[2 * T + t] = 1.0
  A_ub.append(row_grid)
  b_ub.append(grid_cap_mw)

  # Solar allocation constraint
  row_solar = np.zeros(4 * T)
  row_solar[t] = 1.0
  row_solar[T + t] = 1.0
  A_ub.append(row_solar)
  b_ub.append(solar_profile[t])

  # Battery SOC balance
  row_soc = np.zeros(4 * T)
  row_soc[3 * T + t] = 1.0
  if t > 0:
    row_soc[3 * T + t - 1] = -1.0
  row_soc[T + t] = -eta_ch
  row_soc[2 * T + t] = 1.0 / eta_dis
  A_eq.append(row_soc)
  b_eq.append(0.0)

bounds = (
    [(0, grid_cap_mw) for _ in range(T)]
    + [(0, bess_power_mw) for _ in range(T)]
    + [(0, bess_power_mw) for _ in range(T)]
    + [(0, bess_cap_mwh) for _ in range(T)]
)

res = linprog(
    c,
    A_ub=np.array(A_ub),
    b_ub=np.array(b_ub),
    A_eq=np.array(A_eq),
    b_eq=np.array(b_eq),
    bounds=bounds,
    method="highs",
)

p_solar_grid = res.x[0:T]
p_solar_bess = res.x[T : 2 * T]
p_bess_dis = res.x[2 * T : 3 * T]
soc = res.x[3 * T : 4 * T]
total_export = p_solar_grid + p_bess_dis
clipped = np.maximum(0.0, solar_profile - (p_solar_grid + p_solar_bess))

# Baseline Standalone Solar (without battery, clipped at grid cap)
standalone_export = np.minimum(solar_profile, grid_cap_mw)
standalone_rev = np.sum(standalone_export * prices)
optimized_rev = np.sum(total_export * prices)
revenue_uplift = optimized_rev - standalone_rev

col1, col2 = st.columns([2, 1])

with col1:
  st.subheader("📊 24-Hour Optimal Co-located Dispatch Schedule")
  fig, ax1 = plt.subplots(figsize=(10, 5))

  ax1.plot(
      hours,
      solar_profile,
      label="Raw Solar PV Generation",
      color="#F59E0B",
      linestyle="--",
      linewidth=1.8,
  )
  ax1.fill_between(
      hours,
      0,
      p_solar_grid,
      label="Direct Solar Export to Grid",
      color="#10B981",
      alpha=0.6,
  )
  ax1.fill_between(
      hours,
      p_solar_grid,
      p_solar_grid + p_solar_bess,
      label="Solar Charged into BESS",
      color="#3B82F6",
      alpha=0.6,
  )
  ax1.fill_between(
      hours,
      total_export - p_bess_dis,
      total_export,
      label="BESS Discharged to Grid",
      color="#8B5CF6",
      alpha=0.6,
  )
  ax1.axhline(
      grid_cap_mw,
      color="#EF4444",
      linestyle=":",
      linewidth=2.2,
      label=f"Grid Limit ({grid_cap_mw} MW)",
  )

  ax1.set_xlabel("Hour of Day", fontweight="bold")
  ax1.set_ylabel("Power [MW]", fontweight="bold")
  ax1.set_xticks(hours)
  ax1.grid(alpha=0.3)
  ax1.legend(loc="upper left", frameon=True, fontsize=8)

  st.pyplot(fig)

with col2:
  st.subheader("💶 Commercial Value & Arbitrage Uplift")
  st.metric(
      label="Optimized Daily Revenue (Solar + BESS)",
      value=f"€{optimized_rev:,.2f}",
  )
  st.metric(
      label="Standalone Solar Revenue (Clipped)",
      value=f"€{standalone_rev:,.2f}",
  )
  st.metric(
      label="Daily Battery Revenue Uplift",
      value=f"+€{revenue_uplift:,.2f}",
      delta=f"+{(revenue_uplift/standalone_rev)*100:.1f}% Boost"
      if standalone_rev > 0
      else "N/A",
  )
  st.metric(
      label="Solar Energy Shifted via Storage",
      value=f"{np.sum(p_solar_bess):,.1f} MWh/day",
  )

st.markdown("---")
st.caption(
    "Solves the peak-hour grid curtailment bottleneck by energy time-shifting"
    " into premium evening hours."
)
