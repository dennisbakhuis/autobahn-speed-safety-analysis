# Highway Safety Metric — Definition & Design Space

> Working document for the Autobahn Speed Safety Analysis project.  
> Purpose: define a comparable, multi-dimensional safety metric that works across highway systems and countries.

---

## 1. The Core Problem

A raw accident count is meaningless without exposure. A fatality rate per km favours lightly-used roads. A rate per vehicle only rewards roads with few vehicles. Any metric that ignores infrastructure quality, enforcement, or traffic mix will confound what we're actually trying to measure.

The ideal metric must:
- Be **comparable across countries** with different reporting standards
- **Normalise for exposure** (traffic volume, road length, time)
- **Separate severity levels** (not lump property damage with fatalities)
- **Account for confounders** that are not the variable of interest (speed limit policy)

---

## 2. Perspectives & Quantity Families

### 2.1 Incident Outcomes (What Happened)

These are the dependent variables — what we ultimately want to minimise.

| Quantity | Symbol | Definition | Notes |
|---|---|---|---|
| Fatal accidents | `FA` | Crashes resulting in ≥1 death within 30 days | 30-day definition is EU standard (UN R54) |
| Fatalities | `D` | Number of deaths | Distinct from fatal accident count |
| Serious injuries | `SI` | Hospitalised >24h or MAIS3+ | Definition varies by country — major confounder |
| Light injuries | `LI` | Treated but not hospitalised | Highly underreported, use with caution |
| Property-damage-only | `PDO` | No injury reported | Severely underreported; exclude from primary metric |
| Near-misses | `NM` | Dangerous events without contact | Rarely collected; valuable but inconsistent |

**Severity index** (single composite):
```
SI_index = (D × w_fatal) + (SI × w_serious) + (LI × w_light)
```
Weights can follow MAIS-based disutility values (e.g. w_fatal=1.0, w_serious=0.1, w_light=0.01) or economic cost weights (VSL-based).

---

### 2.2 Exposure Normalisation (Per What?)

This is the most critical design choice. Different denominators answer different questions.

| Denominator | Abbreviation | Answers | Weakness |
|---|---|---|---|
| Road length (km) | per km | "How dangerous is this road segment?" | Ignores traffic volume |
| Vehicle-kilometres travelled | per VKT (100M vkm) | "How dangerous is driving here?" | VKT data quality varies by country |
| Vehicle-hours travelled | per VHT | "Time-at-risk exposure" | Favours slow/congested roads as safer |
| Registered vehicles | per 1000 veh | Population-level comparison | Confounds road use patterns |
| Population | per 100k pop | Policy/public health framing | Not road-segment comparable |

**Recommendation for this project:** Use both **per km** and **per 100M VKT** as primary metrics, and report both. They answer complementary questions. VKT is the international standard (WHO, EuroRAP, OECD/IRTAD use it).

---

### 2.3 Speed-Related Quantities

Speed is the central variable of interest in this project.

| Quantity | Symbol | Definition |
|---|---|---|
| Speed limit | `v_lim` | Posted limit (or "unlimited" / Richtgeschwindigkeit 130 advisory) |
| Mean operating speed | `v̄` | Mean speed from loop detectors or floating car data |
| 85th percentile speed | `v85` | Speed not exceeded by 85% of vehicles |
| Speed standard deviation | `σ_v` | Spread of speed distribution |
| Coefficient of variation | `CV_v = σ_v / v̄` | Relative speed dispersion; key for crash risk |
| Speed differential | `Δv` | Difference between fastest and slowest decile |
| Compliance rate | `C_lim` | Share of vehicles at or below speed limit |
| Mean excess speed | `v̄ - v_lim` | Average amount of limit exceedance |

**Power Model quantities** (from Nilsson 2004, Elvik 2013):
```
FA₂/FA₁ = (v₂/v₁)³        # fatal accidents
D₂/D₁   = (v₂/v₁)⁴        # fatalities (exponent ~4.6 at motorway speeds)
IA₂/IA₁ = (v₂/v₁)²        # injury accidents
```

Speed dispersion (`σ_v`) is independently predictive of crash risk (Aarts & van Schagen 2006) and must be included separately from mean speed.

---

### 2.4 Infrastructure Quality

These are confounders if not controlled for; they also determine the counterfactual "how safe should this road be?"

| Quantity | Symbol | Standard | Notes |
|---|---|---|---|
| International Roughness Index | IRI | World Bank | Surface condition |
| Lane width | `w_lane` | — | Narrow lanes → higher crash risk |
| Shoulder width & type | `w_shoulder` | — | Hard shoulder vs. soft vs. none |
| Median type | `M_type` | — | Concrete barrier, cable, grass, none |
| Number of lanes | `n_lanes` | — | Per direction |
| Alignment curvature | `κ` | rad/km | Straight vs. curved |
| Vertical grade | `g` | % | Gradient |
| Sight distance | `SD` | m | Stopping sight distance |
| Barrier quality | `B_score` | iRAP | iRAP star rating covers this |
| Junction/interchange density | `J_dens` | per km | Access management quality |
| Rest area / emergency bay density | `RA_dens` | per km | Emergency pulloff availability |
| Variable Speed Limit coverage | `VSL_frac` | [0,1] | Fraction of section with overhead VSL signs |
| Lighting | `L_type` | — | Full, partial, none |
| iRAP star rating | `iRAP*` | 1–5 stars | Infrastructure risk rating (composite) |

---

### 2.5 Traffic Composition

Who and what is on the road matters for both crash probability and severity.

| Quantity | Symbol | Definition |
|---|---|---|
| Annual Average Daily Traffic | AADT | Vehicles/day, both directions |
| Heavy goods vehicle share | `f_HGV` | Fraction of traffic that is truck/lorry |
| Motorcycle share | `f_moto` | Fraction motorcycles |
| Directional split | `DS` | Peak direction fraction |
| Traffic density | `k` | Vehicles/km (flow/speed) |
| Level of service | `LOS` | A–F (HCM) |
| Congestion frequency | `f_cong` | Hours/year at LOS E/F |
| Peak-to-off-peak ratio | `PPR` | Traffic variability |

HGV fraction is particularly important: mixed HGV/car traffic at high speed differential is a major severity amplifier.

---

### 2.6 Environmental & Contextual Factors

| Quantity | Symbol | Definition |
|---|---|---|
| Precipitation days/year | `P_days` | Wet surface exposure |
| Fog days/year | `F_days` | Low visibility events |
| Freeze-thaw cycles/year | `FT_cycles` | Ice risk |
| Snow days/year | `S_days` | Snow surface risk |
| Daylight fraction of traffic | `DL_frac` | Share of VKT in daylight hours |
| Tunnel fraction | `T_frac` | Share of route in tunnels |
| Wildlife crossing frequency | `WC_dens` | Game crossing risk |
| Urban vs. rural classification | `U_type` | EU urban/rural/intermediate |

Weather variables can be used to construct a **Weather Risk Index (WRI)** for normalisation.

---

### 2.7 Enforcement & Regulation

| Quantity | Symbol | Definition |
|---|---|---|
| Speed limit type | `v_lim_type` | Statutory / advisory / none |
| Camera density | `CAM_dens` | Fixed cameras per km |
| Mobile enforcement frequency | `ME_freq` | Patrol operations per year |
| Average fine for speeding | `fine_€` | Economic deterrent |
| DUI enforcement intensity | `DUI_score` | Checkpoint frequency, penalty severity |
| Post-crash investigation quality | `INV_score` | Data completeness |

The enforcement gap between Germany (no cameras on unlimited sections) and the Netherlands (widespread fixed camera network) is a key structural difference to quantify.

---

### 2.8 Emergency Response Capability

| Quantity | Symbol | Definition |
|---|---|---|
| Mean emergency response time | `ERT` | Minutes from crash to first responder |
| Distance to Level-1 trauma centre | `d_TC` | km |
| Helicopter availability | `HEMS` | Boolean or coverage fraction |
| Crash barrier performance | `CBP` | EN 1317 class |

ERT matters for fatality conversion: a survivable crash becomes fatal without rapid response. This should be included as a severity modifier, not a primary exposure metric.

---

## 3. Composite Metric Candidates

### 3.1 Fatality Rate (FR) — Primary

```
FR = (D / VKT) × 10⁸    [fatalities per 100M vehicle-km]
```

International standard used by OECD/IRTAD, WHO, EuroRAP. Most comparable across countries.

### 3.2 Serious Injury Rate (SIR)

```
SIR = (SI / VKT) × 10⁸    [serious injuries per 100M vehicle-km]
```

More statistically robust than FR (larger counts), but definition varies by country. Use MAIS3+ definition where available.

### 3.3 Risk Index (RI) — Severity-Weighted

```
RI = (D + 0.1 × SI + 0.01 × LI) / VKT × 10⁸
```

Weights can be calibrated to economic cost (VSL, MAIS-based) or disutility values. Requires a single weighting scheme applied consistently across all comparisons.

### 3.4 EuroRAP / iRAP Risk Rating

EuroRAP uses a risk mapping approach:
```
EuroRAP_Risk = (FA / VKT) × 10⁹    [fatal crashes per billion vkm]
```
Star ratings: <0.5 = 4★, 0.5–2 = 3★, 2–6 = 2★, >6 = 1★ (approximate).
This is the most internationally recognised existing standard — worth reporting for comparability.

### 3.5 Infrastructure-Adjusted Safety Score (IASS) — Experimental

A metric that separates the safety contribution of infrastructure from behaviour/regulation:
```
IASS = FR_observed / FR_predicted(iRAP*, v̄, AADT, f_HGV)
```
Where `FR_predicted` comes from a regression model trained on the full dataset. A score > 1 means the road is more dangerous than its infrastructure predicts; < 1 means it outperforms its infrastructure.

---

## 4. Comparability Challenges

### 4.1 Reporting Differences
- **Germany:** accident data from Destatis (Straßenverkehrsunfallstatistik); 30-day fatality definition
- **Netherlands:** BRON database (Bestand geRegistreerde Ongevallen in Nederland); 30-day definition since 2010
- **Serious injury definition:** MAIS3+ in NL; Germany uses "schwerverletzt" (hospitalised >24h) — not equivalent

→ **Recommendation:** use fatalities as primary metric (most consistent), serious injuries as secondary with explicit caveat on definition mismatch.

### 4.2 VKT Data Quality
- Germany: VKT from Bundesanstalt für Straßenwesen (BASt) traffic counts
- Netherlands: VKT from Rijkswaterstaat NDW loop detectors
- Granularity differs; section-level VKT may need interpolation

### 4.3 Road Classification Alignment
- German Autobahn (BAB) ↔ Dutch Autosnelweg (A-roads)
- Both are restricted-access, grade-separated motorways — most comparable road type internationally
- Exclude non-motorway Bundesstraßen / N-roads from primary comparison

### 4.4 Speed Limit Comparability
- NL: uniform 100 km/h (day) / 130 km/h (night/weekend) since 2020; was 120/130 before
- DE: mixed — ~70% unlimited, ~30% limited (various limits: 100, 120, 130 km/h)
- Key variable: must encode whether each section is unlimited or limited, and if limited, at what speed

---

## 5. Recommended Minimum Variable Set

For a primary analysis, these variables are necessary:

1. `FA` — fatal accident count per section per year
2. `D` — fatality count per section per year
3. `SI` — serious injury count per section per year
4. `VKT` — vehicle-kilometres travelled per section per year
5. `L_km` — section length (km)
6. `v_lim` — speed limit (numeric; use 999 or NaN for unlimited)
7. `v̄` — mean operating speed (from detectors or floating car data)
8. `σ_v` — speed standard deviation
9. `AADT` — annual average daily traffic
10. `f_HGV` — HGV fraction
11. `iRAP*` — infrastructure star rating (if available; otherwise `M_type` + `n_lanes` as proxy)
12. `VSL_frac` — fraction of section with variable speed limits
13. `country` — DE / NL (for reporting-system fixed effects)
14. `year` — for time-trend control

---

## 6. Open Questions

- [ ] Should the metric penalise speed *variance* independently of mean speed? (Literature suggests yes — Aarts 2006)
- [ ] How to handle unlimited sections: encode as `v_lim = observed_v85` or as a categorical dummy?
- [ ] iRAP star ratings: are these available at section level for Germany and the Netherlands?
- [ ] How to deal with changing speed limits on the same section across time (NL 2020 change)?
- [ ] Should emergency response time be included as a severity modifier?
- [ ] Is a single composite score useful, or should we always report FR and SIR separately?
- [ ] EuroRAP risk bands: should we adopt their thresholds for our rating, or define our own?

---

## 7. Existing Frameworks to Reference

| Framework | Owner | Primary Metric | Scope |
|---|---|---|---|
| EuroRAP Risk Mapping | EuroRAP | FA per 100M vkm | Europe |
| iRAP Star Rating | iRAP | Infrastructure-predicted risk | Global |
| OECD/IRTAD | OECD | D per 100M vkm | 40+ countries |
| WHO Global Status Report | WHO | D per 100k population | Global |
| Sustainable Safety (NL) | SWOV | Multiple | Netherlands |
| Power Model | Nilsson/Elvik | Speed-fatality elasticity | Global |

Our metric should be compatible with EuroRAP/IRTAD for international comparability, while adding the speed-distribution dimension that those frameworks typically omit.

---

*Last updated: 2026-03-18 · Status: draft*

---

## 8. Comparing Unlimited vs. ≤130 km/h: A Fair Metric

### 8.1 The Causal Question

The naive question — "do unlimited sections have more deaths?" — is answerable but not useful. A fair comparison must answer:

> **Holding road quality, traffic volume, and driver population equal, does removing the speed limit cause disproportionately more deaths?**

This is a causal inference problem. Unlimited and limited sections differ on many dimensions besides the speed policy. Without controlling for those, any raw comparison is confounded.

---

### 8.2 The Two Major Confounders

**Infrastructure selection bias → Underestimates risk of unlimited**  
Germany tends to place speed limits on *worse* sections: curves, construction zones, urban approaches, accident black spots. Unlimited sections are disproportionately the straight, wide, well-designed segments. If you compare raw fatality rates, unlimited sections may look *safer* — not because high speed is safe, but because they sit on better roads.

Direction: naive comparison **underestimates** the danger of removing limits.

**Traffic volume & composition → Ambiguous**  
Unlimited sections often have high AADT and high HGV fractions (freight corridors). High HGV fraction increases severity; high AADT can homogenise speeds (less dispersion) which reduces risk per vehicle. These effects partially cancel.

**Speed dispersion**  
At unlimited sections, mean speed is higher but speed dispersion may be *lower* during free-flow conditions (everyone going fast). During congestion, it spikes dangerously. The Sustainable Safety principle of speed homogeneity cuts both ways here.

---

### 8.3 Four Approaches to a Fair Comparison

#### Approach A — Regression-Adjusted Rate (Most Feasible)

Compute fatality rate (FR = deaths per 100M VKT) for every road section, then fit:

```
log(FR_i) = β₀ + β₁ · unlimited_i + β₂ · iRAP*_i + β₃ · log(AADT_i)
           + β₄ · f_HGV_i + β₅ · σ_v_i + β₆ · VSL_frac_i + ... + ε_i
```

The coefficient `β₁` on the unlimited dummy is the **adjusted risk premium** — how much more dangerous unlimited is, given comparable infrastructure and traffic. Exponentiate to get a risk ratio.

**Pros:** Uses all available data, handles continuous confounders.  
**Cons:** Assumes correct model specification; can't control for unobserved differences.

---

#### Approach B — Matched Pair Comparison (Cleanest Conceptually)

For each unlimited section, find a limited section (≤130 km/h) that is comparable on:
- Infrastructure quality (iRAP★ or proxy: lanes, median type, curvature)
- Traffic volume (AADT ± 20%)
- HGV fraction (± 5pp)
- Weather zone (similar precipitation/fog exposure)

Then compare FR within matched pairs. Technique: Coarsened Exact Matching (CEM) or Propensity Score Matching (PSM).

**Pros:** Transparent, no functional form assumption.  
**Cons:** Requires a large enough pool of comparable sections; Germany has limited limited-speed sections for matching.

---

#### Approach C — Power Model Counterfactual (Theory-Grounded)

Use the observed speed distribution on unlimited sections, then ask: *what would the fatality count be if everyone drove at ≤130 km/h?*

```
D_counterfactual = D_observed × (130 / v̄_observed)⁴·⁶
```

(Exponent 4.6 from Elvik 2013 for motorway fatalities at high initial speeds)

The **excess fatalities attributable to unlimited speeds**:

```
ΔD = D_observed - D_counterfactual

Excess Risk Fraction (ERF) = ΔD / D_observed
```

ERF = 0.30 means 30% of deaths on unlimited sections are attributable to the speed policy, beyond what would occur at 130 km/h.

**Pros:** Directly answers "what if we imposed a limit?"; uses peer-reviewed exponents from your existing references.  
**Cons:** Requires actual speed data (not just posted limits); assumes Power Model holds at high-speed regime.

---

#### Approach D — Natural Experiment / Difference-in-Differences (Gold Standard)

If any sections changed from unlimited → limited (or vice versa) during the study period:

```
Treatment Effect = ΔFR_treated - ΔFR_control
```

Where treated = sections that changed policy, control = sections that did not. Controls for all time-invariant section characteristics automatically.

**Pros:** Most credible causal identification; eliminates infrastructure confound entirely.  
**Cons:** Requires longitudinal section-level data and sections that actually changed policy. These exist but are rare on the Autobahn.

---

### 8.4 Recommended Metric: The Adjusted Risk Ratio (ARR)

Given available data, the most defensible primary metric is:

```
ARR = FR_unlimited_adjusted / FR_limited_adjusted
```

Where "adjusted" means controlling for infrastructure quality, traffic volume, HGV fraction, and speed dispersion via a Poisson or negative binomial regression (appropriate for count data with exposure offset).

**Interpretation:**
- ARR = 1.0 → unlimited sections are equally safe after controlling for confounders
- ARR = 1.5 → 50% higher fatality risk on unlimited sections, holding road quality equal
- ARR = 2.0 → unlimited sections are twice as deadly for comparable roads

Supplement with the **Excess Risk Fraction** (Approach C) as a second metric — it gives an absolute estimate of preventable deaths.

---

### 8.5 The Fairness Checklist

A comparison is only "fair" if it satisfies:

| Check | Why it Matters |
|---|---|
| Normalise by VKT, not km | Per-km favours low-traffic roads |
| Control for infrastructure quality | Unlimited sections sit on better roads |
| Control for HGV fraction | More trucks → more severe crashes |
| Use same severity definition | DE/NL serious injury definitions differ |
| Include speed *distribution*, not just mean | Dispersion is independently predictive |
| Separate FR from SIR | Survivability differs; don't conflate |
| Account for VSL coverage | Partial speed management on "unlimited" sections |
| Same time period | Control for secular safety improvements |

---

### 8.6 Summary Pipeline

```
Step 1: Compute FR = deaths / VKT × 10⁸ per section
Step 2: Fit regression controlling for infrastructure, traffic, HGV, speed dispersion
Step 3: Extract β_unlimited → Adjusted Risk Ratio (ARR)
Step 4: Compute Excess Risk Fraction via Power Model as cross-check
Step 5: (If data allows) DiD on sections that changed policy
Step 6: Report ARR ± CI, ERF, and raw FR for transparency
```

The finding is "irresponsibly more dangerous" if ARR is statistically significantly > 1 *after* controlling for all known advantages of unlimited sections. If unlimited sections are still more dangerous despite sitting on better roads, that is the cleanest possible finding.

---

### 8.7 Data Requirements

| Data Item | Germany Source | Netherlands Source |
|---|---|---|
| Fatalities per section | Destatis / BASt (Unfallatlas) | CBS / BRON |
| VKT per section | BASt traffic counts | RWS NDW loop detectors |
| Speed distribution | BASt loop detectors / TomTom probe data | NDW / MeMo |
| HGV fraction | BASt | NDW |
| Infrastructure quality | BASt road inventory | RWS wegkenmerken |
| Speed limit per section | BASt / OSM | WEGGEG / OSM |
| VSL coverage | Länder traffic authorities | RWS |

OpenStreetMap is a practical fallback for speed limits and road geometry where official data is unavailable at section level.
