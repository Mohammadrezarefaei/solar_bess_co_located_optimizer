# ☀️🔋 Co-located Solar PV + BESS Dispatch Optimizer

[![CI Pipeline](https://img.shields.io/badge/CI%20Pipeline-passing-brightgreen?logo=github&style=flat-square)](https://github.com/Mohammadrezarefaei/solar-plus-storage-dispatch-optimizer/actions)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://solar-plus-storage-dispatch-optimizer-mrearm8fvjnryhdygkxp6y.streamlit.app/)

A mathematical optimization framework for maximizing commercial revenues in **co-located Solar PV and Battery Energy Storage Systems (BESS)** under strict **Grid Interconnection Capacity Constraints** in the European electricity wholesale market.

---

## 🚀 Live Interactive Demo
👉 **[Access the Live Streamlit Web App](https://solar-plus-storage-dispatch-optimizer-mrearm8fvjnryhdygkxp6y.streamlit.app/)**

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

## 🔍 Key Findings & Commercial Value Drivers

* **Grid Curtailment Mitigation:** The battery actively absorbs midday generation that would otherwise be curtailed by substation thermal limits or liquidated into negative price regimes.
* **Energy Time-Shifting:** Stored energy is evacuated during evening net-load ramps (€120–145/MWh), unlocking substantial revenue uplift over standalone solar assets.
* **Linear Programming Precision:** Formulated and solved via the **HiGHS Solver** (`scipy.optimize.linprog`) for deterministic, globally optimal daily dispatch schedules.

---

## 🛠️ Software Architecture & Automated Testing
* **CI/CD Pipeline:** Fully automated testing via **GitHub Actions** with **all unit tests passing** (`pytest` suite validating grid export limits, C-rate compliance, state-of-charge continuity, and round-trip efficiency losses).
* **Modular Core Engine:** Implemented in `src/hybrid_engine.py`.
* **Tech Stack:** Python 3.11, SciPy (Linear Programming), NumPy, Pandas, Matplotlib, Streamlit, Pytest.
