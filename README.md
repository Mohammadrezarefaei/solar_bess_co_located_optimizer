# ☀️🔋 Co-located Solar PV + BESS Dispatch Optimizer

[![Optimizer CI](https://github.com/Mohammadrezarefaei/solar-plus-storage-dispatch-optimizer/actions/workflows/ci.yml/badge.svg)](https://github.com/Mohammadrezarefaei/solar-plus-storage-dispatch-optimizer/actions)

A mathematical optimization framework for maximizing commercial revenues in **co-located Solar PV and Battery Energy Storage Systems (BESS)** under strict **Grid Interconnection Capacity Constraints** in the European electricity wholesale market.

---

## 📌 Problem Formulation & Market Mechanics

Renewable asset developers frequently face grid capacity bottlenecks where the nameplate peak generation exceeds local substation export ratings ($P_{\text{Solar}} > P_{\text{Grid Limit}}$). During peak midday hours, high solar feed-in coincides with cannibalized or negative wholesale prices:
* **Objective Function:**
  $$\max \sum_{t=1}^{T} \left( P_{\text{Solar}\to\text{Grid}}(t) + P_{\text{BESS}\to\text{Grid}}(t) \right) \cdot \lambda_{\text{DA}}(t)$$
* **Grid Export Capacity Boundary:**
  $$P_{\text{Solar}\to\text{Grid}}(t) + P_{\text{BESS}\to\text{Grid}}(t) \le C_{\text{Grid Limit}} \quad \forall t$$
* **Storage Energy Balance & Round-Trip Efficiency:**
  $$\text{SOC}(t) = \text{SOC}(t-1) + \eta_{\text{charge}} P_{\text{Charge}}(t) - \frac{1}{\eta_{\text{discharge}}} P_{\text{Discharge}}(t)$$

---

## 🔍 Key Findings & Value Drivers

* **Curtailment Mitigation:** The battery absorbs excess generation that would otherwise be curtailed by grid boundaries or liquidated into negative price spreads.
* **Energy Time-Shifting:** Stored energy is evacuated during high-demand evening net-load ramps (€120–145/MWh), unlocking substantial revenue uplift over standalone solar assets.
* **Solver Implementation:** Formulated via Linear Programming using the **HiGHS Solver** for deterministic and globally optimal dispatch solutions.

---

## 🛠️ Software Architecture & Automated Testing
* **CI/CD Pipeline:** Fully automated testing via **GitHub Actions** (`pytest` suite validating grid export limits, C-rate compliance, and round-trip efficiency losses).
* **Modular Core Engine:** Located in `src/hybrid_engine.py`.
* **Tech Stack:** Python 3.11, SciPy (Linear Programming), NumPy, Pandas, Matplotlib, Pytest.
