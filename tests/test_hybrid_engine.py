"""Automated Pytest Suite for Solar + BESS Dispatch Optimizer."""

import numpy as np
import pytest
from src.hybrid_engine import HybridDispatchEngine


def test_grid_export_limit_compliance():
  engine = HybridDispatchEngine(
      grid_export_limit_mw=10.0,
      battery_power_mw=5.0,
      battery_capacity_mwh=10.0,
      round_trip_efficiency=0.90,
  )
  solar = [0.0, 0.0, 5.0, 15.0, 18.0, 12.0, 2.0, 0.0]
  prices = [40.0, 30.0, 20.0, -10.0, -5.0, 60.0, 120.0, 90.0]

  res = engine.optimize_dispatch(solar, prices)
  # Total export to grid must never exceed 10.0 MW limit
  assert np.all(res["total_grid_export"] <= 10.0 + 1e-5)


def test_battery_storage_prevents_clipping_loss():
  engine = HybridDispatchEngine(
      grid_export_limit_mw=10.0,
      battery_power_mw=5.0,
      battery_capacity_mwh=10.0,
  )
  solar = [0.0, 0.0, 0.0, 14.0, 14.0, 0.0, 0.0, 0.0]
  prices = [50.0, 50.0, 50.0, 10.0, 10.0, 90.0, 90.0, 50.0]

  res = engine.optimize_dispatch(solar, prices)
  # Battery should charge during midday peak and discharge during evening peak
  assert np.sum(res["p_solar_bess"]) > 0.0
  assert np.sum(res["p_bess_discharge"]) > 0.0
  assert res["total_revenue_eur"] > 0.0
