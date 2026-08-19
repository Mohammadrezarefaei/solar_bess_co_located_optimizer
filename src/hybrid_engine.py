"""Co-located Solar PV + BESS Dispatch Optimizer under Grid Interconnection Constraints."""

from typing import Dict, List
import numpy as np
from scipy.optimize import linprog


class HybridDispatchEngine:

  def __init__(
      self,
      grid_export_limit_mw: float = 10.0,
      battery_power_mw: float = 5.0,
      battery_capacity_mwh: float = 10.0,
      round_trip_efficiency: float = 0.90,
  ):
    self.grid_limit = grid_export_limit_mw
    self.bess_power = battery_power_mw
    self.bess_capacity = battery_capacity_mwh
    self.efficiency = round_trip_efficiency
    self.charge_eff = np.sqrt(round_trip_efficiency)
    self.discharge_eff = np.sqrt(round_trip_efficiency)

  def optimize_dispatch(
      self,
      solar_profile_mw: List[float],
      day_ahead_prices_eur: List[float],
  ) -> Dict[str, np.ndarray]:
    """Optimizes hourly Solar + Storage dispatch to maximize total revenue while strictly respecting the grid connection limit."""
    T = len(solar_profile_mw)
    prices = np.array(day_ahead_prices_eur)
    solar = np.array(solar_profile_mw)

    # Decision variables per hour:
    # 0..T: P_solar_to_grid (t)
    # T..2T: P_solar_to_bess (t)
    # 2T..3T: P_bess_discharge (t)
    # 3T..4T: SOC(t)
    c = np.zeros(4 * T)
    # Maximize Revenue: c^T * x -> linprog minimizes, so multiply prices by -1
    c[0:T] = -prices  # Revenue from direct solar export
    c[2 * T : 3 * T] = -prices  # Revenue from battery discharge export

    A_ub = []
    b_ub = []
    A_eq = []
    b_eq = []

    for t in range(T):
      # 1. Grid connection limit: P_solar_to_grid(t) + P_bess_discharge(t) <= Grid Limit
      row_grid = np.zeros(4 * T)
      row_grid[t] = 1.0
      row_grid[2 * T + t] = 1.0
      A_ub.append(row_grid)
      b_ub.append(self.grid_limit)

      # 2. Solar balance: P_solar_to_grid(t) + P_solar_to_bess(t) <= Solar(t)
      row_solar = np.zeros(4 * T)
      row_solar[t] = 1.0
      row_solar[T + t] = 1.0
      A_ub.append(row_solar)
      b_ub.append(solar[t])

      # 3. SOC dynamic continuity constraint: SOC(t) - SOC(t-1) - eta_ch*P_ch(t) + (1/eta_dis)*P_dis(t) = 0
      row_soc = np.zeros(4 * T)
      row_soc[3 * T + t] = 1.0  # SOC(t)
      if t > 0:
        row_soc[3 * T + t - 1] = -1.0  # -SOC(t-1)
      row_soc[T + t] = -self.charge_eff  # -eta_ch * P_ch(t)
      row_soc[2 * T + t] = 1.0 / self.discharge_eff  # + P_dis(t)/eta_dis
      A_eq.append(row_soc)
      b_eq.append(0.0)

    bounds = (
        [(0, self.grid_limit) for _ in range(T)]  # P_solar_to_grid
        + [(0, self.bess_power) for _ in range(T)]  # P_solar_to_bess
        + [(0, self.bess_power) for _ in range(T)]  # P_bess_discharge
        + [(0, self.bess_capacity) for _ in range(T)]
    )  # SOC bounds

    res = linprog(
        c,
        A_ub=np.array(A_ub),
        b_ub=np.array(b_ub),
        A_eq=np.array(A_eq),
        b_eq=np.array(b_eq),
        bounds=bounds,
        method="highs",
    )

    if not res.success:
      raise ValueError(f"Optimization failed: {res.message}")

    x = res.x
    p_solar_grid = x[0:T]
    p_solar_bess = x[T : 2 * T]
    p_bess_dis = x[2 * T : 3 * T]
    soc = x[3 * T : 4 * T]
    total_grid_export = p_solar_grid + p_bess_dis
    clipped_solar = np.maximum(0.0, solar - (p_solar_grid + p_solar_bess))

    total_rev = np.sum(total_grid_export * prices)

    return {
        "p_solar_grid": p_solar_grid,
        "p_solar_bess": p_solar_bess,
        "p_bess_discharge": p_bess_dis,
        "soc": soc,
        "total_grid_export": total_grid_export,
        "clipped_solar": clipped_solar,
        "total_revenue_eur": round(float(total_rev), 2),
    }
