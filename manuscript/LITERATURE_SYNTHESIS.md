# Literature Synthesis — What Each Paper Gives Us

> Maps all 16 reference papers to concrete inputs for the safety metric, ARR analysis, and Power Model counterfactual.  
> Organised by contribution type, not by paper.

---

## 1. The Power Model — Core Quantitative Engine

These papers provide the mathematical backbone for the Excess Risk Fraction (ERF) calculation.

### Nilsson (2004) — *The foundational source*
**What we get:**
- The three canonical Power Model equations, validated on Swedish motorway experiments:
  ```
  FA₂/FA₁ = (v₂/v₁)³      # fatal accident ratio
  D₂/D₁   = (v₂/v₁)⁴      # fatality ratio
  IA₂/IA₁ = (v₂/v₁)²      # injury accident ratio
  ```
- Validated cross-sectionally and longitudinally — this is not a theoretical model, it's empirically derived.

**Direct use:** Apply to unlimited sections to compute counterfactual deaths at 130 km/h. Use exponent 4 as the conservative baseline.

---

### Elvik (2013) — *Upgraded exponents, especially at high speed*
**What we get:**
- Re-parameterised exponents from 115 studies, 526 estimates. Most important finding: **exponents are higher at high initial speeds**, meaning Nilsson's fixed exponents *underestimate* the effect on motorways.
- Motorway/rural road exponents:
  ```
  Fatal accidents:  3.0  (95% CI: 2.9–5.3, best estimate ~4.1)
  Fatalities:       4.6
  Serious injuries: 2.6
  Injury accidents: 1.6
  ```
- The 4.6 exponent for fatalities is the most defensible number to use for Autobahn counterfactuals.

**Direct use:** Use exponent **4.6** (not 4) for fatality counterfactual on unlimited sections. This is the peer-reviewed upgrade to Nilsson and should be our default. Nilsson's 4.0 becomes the conservative lower bound.

---

### Elvik et al. (2019) — *Modern validation*
**What we get:**
- Confirms the Power Model holds with post-2000 data across multiple countries.
- Modern vehicle safety technology has **not** weakened the speed–fatality relationship.
- Same relationship at individual driver level and aggregate traffic level.

**Direct use:** Rebuts the "modern cars are safer so speed matters less" counterargument. Include as a robustness citation when defending the ERF calculation.

---

### Aarts & van Schagen (2006) — *Speed dispersion is a separate predictor*
**What we get:**
- At the individual vehicle level: crash risk is exponential when a vehicle's speed deviates from mean flow speed.
- At the road section level: Power Model applies to mean speed.
- Speed dispersion (σ_v) is **independently predictive** of crash rate, separate from mean speed.
- Relationship is steeper on minor roads but significant on motorways too.

**Direct use:**
1. Justifies including `σ_v` as a separate term in the regression model (Approach A), not just `v̄`.
2. Means unlimited sections need their full speed distribution modelled — not just the mean.
3. The "unlimited sections have low dispersion" argument (sometimes used to defend them) is only true during free-flow; σ_v spikes during congestion.

---

## 2. Empirical Evidence on Speed Limits & Safety Outcomes

These papers give us observable effect sizes to calibrate against and cite as corroboration.

### Vadeby & Forsman (2018) — *Natural experiment, Sweden*
**What we get:**
- Sweden's 2008–2009 speed limit changes across ~20,500 km of rural roads. Both increases and decreases.
- **90→80 km/h reductions:** 14 fewer fatalities/year; no significant change in serious injuries.
- **Increases to 120 km/h on motorways:** ~15 more serious injuries/year.
- **110→100 km/h reductions:** ~16 fewer serious injuries/year.
- A 10 km/h limit change → 2–3 km/h actual mean speed change (compliance is imperfect).

**Direct use:**
1. Real-world calibration: observed effect sizes are broadly consistent with Power Model predictions — validates our ERF methodology.
2. The 10 km/h limit → 2–3 km/h speed change ratio is important: when modelling counterfactual at 130 km/h, don't assume everyone suddenly drives at 130 — model a realistic compliance-adjusted speed reduction.
3. Directly comparable to our DiD approach (Approach D) — use as a template for the natural experiment design.

---

### Johansson (1996) — *Swedish motorway speed limit reduction*
**What we get:**
- Time series count data regression (Poisson + negative binomial) showing speed limit reduction decreased crash counts on Swedish motorways.
- Methodological note: models allowing for serial correlation performed best.

**Direct use:**
1. Confirms count data regression (negative binomial) is the right model family for our Approach A — validates the statistical model choice.
2. Serial correlation in annual section-level counts must be accounted for. Use panel regression with section fixed effects or cluster-robust standard errors.

---

### Doecke et al. (2018) — *Safe speed thresholds by crash type*
**What we get:**
- Empirically derived "safe" speed limits per crash type (defined as ≤1-in-100 fatal crash probability):
  - Rear-end crashes: 110 km/h or more is safe
  - Head-on crashes: 50 km/h
  - Fixed-object crashes: 60 km/h
  - Rollover: 80 km/h
- **Key implication:** speeds >110 km/h are only "safe" where head-on, rollover, and fixed-object crashes are exceedingly rare — i.e., high-standard, divided, barrier-protected motorways.

**Direct use:**
1. Provides crash-type-specific speed thresholds: Autobahn sections that are barrier-protected and divided may be justifiably faster than non-divided roads, but not unlimited.
2. Use to justify why crash type composition matters in the regression — not just total FR.
3. If crash type breakdown is available in Destatis data, stratify the analysis by crash type.

---

## 3. Benchmarking & Cross-Country Comparability

### Aarts & Houwing (2015) — *Fair benchmarking methodology*
**What we get:**
- Urbanisation is the dominant structural factor explaining inter-municipality safety differences in the Netherlands.
- Fair benchmarking requires grouping comparable units — raw cross-country comparisons are misleading without structural controls.
- Methodology: cluster comparable units before comparing rates.

**Direct use:**
1. Directly supports our Approach B (matched pair comparison) — the paper formalises the conceptual basis for matching.
2. When comparing DE unlimited vs. NL limited: must control for urbanisation context and road network structure, not just raw rates.
3. Provides a benchmark: even within one country (NL), sub-national variation is substantial — warns against over-aggregating.

---

### Hermans et al. (2009) — *DEA benchmarking across 21 European countries*
**What we get:**
- Data Envelopment Analysis across 21 EU countries on 6 safety domains (alcohol, speed, protective systems, vehicle, infrastructure, trauma management).
- Sweden, UK, Netherlands are top performers.
- **Speed** is the most critical and actionable domain.
- Country-specific recommendations: countries with poor speed-domain performance should prioritise enforcement and limit-setting.

**Direct use:**
1. Validates Netherlands as a meaningful comparator for Germany — both are EU countries with comparable data systems.
2. The 6 domains map well to our variable families in SAFETY_METRIC.md.
3. DEA could be used as an alternative composite metric if we want to avoid single-number reduction.

---

### Wegman et al. (2008) — *Dutch Sustainable Safety programme*
**What we get:**
- Five principles of Sustainable Safety, with **homogeneity of mass, speed, and direction** as a core pillar.
- Speed homogeneity explicitly identified as a safety principle: mixing high- and low-speed vehicles is inherently dangerous.
- NL's low fatality rate is a direct result of sustained speed management — inverse of German unlimited policy.
- Road crash costs in NL 2003: €12.3 billion (2.6% of GNP).

**Direct use:**
1. Speed homogeneity principle provides theoretical justification for including `σ_v` (speed dispersion) in the metric — not just mean speed.
2. Economic cost framing: use to express ERF in monetary terms (preventable deaths × VSL).
3. Institutional context: explains *why* NL is a valid comparator — it is the result of a deliberate and documented safety programme, not random variation.

---

## 4. Enforcement Effects

### Bauernschuster & Rekers (2022) — *Blitzmarathon natural experiment*
**What we get:**
- One-day mass enforcement operations (Blitzmarathon) reduced accidents by **7.5%** and slight injuries by **8.5%** on operation days.
- Effect **vanishes immediately** after the operation ends — purely deterrence-driven, no lasting behavioural change.
- Information campaigns alone do not change behaviour.

**Direct use:**
1. Confirms that German Autobahn drivers *do* reduce speed when detection probability rises — they are speed-limit-responsive, not speed-limit-immune.
2. The effect size (7.5% fewer accidents in one day) calibrates the potential gain from permanent enforcement.
3. Methodologically: provides a clean DiD effect size to compare against our ARR — if our ARR is much larger than 7.5%, enforcement alone doesn't explain the difference.
4. Warns against using camera density alone as an enforcement proxy — it's about perceived detection probability, not just camera count.

---

### Goldenbeld & van Schagen (2005) — *Sustained Dutch enforcement*
**What we get:**
- 5-year sustained speed enforcement on Dutch rural roads: 21% reduction in injury accidents and serious casualties.
- Effects sustained and grew over time — opposite of the one-day Blitzmarathon.
- Spillover effects to non-enforced roads.

**Direct use:**
1. Contrast with Bauernschuster: sustained enforcement (NL model) produces lasting 21% safety gains; one-day operations (DE model) produce temporary 7.5% gains. This is a quantified enforcement gap.
2. When computing the ARR (DE unlimited vs. NL limited), part of the difference is attributable to enforcement intensity — not purely to the speed limit itself. Must include enforcement proxy in the regression.
3. The 21% figure provides an upper bound on the "enforcement effect" that could confound our comparison.

---

## 5. Variable Speed Limits on the Autobahn

### Bertini et al. (2006) — *A9 VSL system*
**What we get:**
- VSL systems on German Autobahn have decreased crash rates by **up to 20%** (cited from prior literature, confirmed in new data).
- A9 near Munich: VSL successfully reduced speeds before bottleneck; traffic continued flowing during congestion.

**Direct use:**
1. Justifies `VSL_frac` as a control variable in the regression — sections with VSL coverage are partially speed-managed even if nominally "unlimited".
2. The 20% effect size means that unlimited sections *with* VSL are materially safer than unlimited sections *without* VSL. Confounding if not controlled.
3. Operationalise: code each section as `VSL_frac ∈ [0, 1]` (fraction of section km covered by overhead signs), not as a binary.

---

### Weikl et al. (2013) — *A99 before/after VSL*
**What we get:**
- True before/after comparison (rare) of VSL installation on A99 near Munich.
- VSL produced more homogeneous lane-use and balanced flow across lanes.
- **Safety gain comes at a small capacity cost** — VSL slows the fastest drivers.
- Confirms: crash rates decrease up to 20% with VSL.

**Direct use:**
1. Corroborates Bertini — 20% is a robust estimate for the VSL effect.
2. The before/after design is the same methodology as our Approach D (DiD). Use this paper as a methodological template.
3. Lane homogeneity insight: VSL improves safety partly through speed dispersion reduction, not only through mean speed reduction. Supports including `σ_v` as a separate term.

---

### Manner & Wünsch-Ziegler (2013) — *Accident severity on NRW Autobahn*
**What we get:**
- Multinomial logit on NRW Autobahn data 2009–2011.
- Intelligent traffic control (VSL + dynamic signs) significantly **reduces accident severity**.
- Severity is higher: roadside object collisions, poor visibility, pedestrians/motorcycles.
- Severity is lower: daytime, interchanges, construction sites.

**Direct use:**
1. Validates the severity-reduction mechanism of VSL — relevant to the SIR component of our metric.
2. Covariates for the severity model: time of day, visibility, crash partner type. These should be in the regression if crash-level data is available.
3. **Actionable:** if section-level VSL coverage data can be obtained for NRW specifically, Manner's dataset geography overlaps.

---

## 6. Speed Limit Policy Context

### Bauernschuster & Traxler (2021) — *Evidence base for Tempolimit 130*
**What we get:**
- ~70% of German Autobahn has no speed limit — an international outlier.
- Available evidence points to net benefits from a 130 km/h limit.
- Data quality is poor and causal evidence is scarce (their critique — which our project addresses).
- >50% of Germans support a general limit in surveys.

**Direct use:**
1. **Explicitly positions our project** — they flag that causal evidence is scarce. Our ARR analysis with confounders controlled is the kind of evidence they are calling for.
2. Confirms the ~70% unlimited fraction — useful for computing the share of German BAB km that is unlimited (denominator for aggregate ERF).
3. CO₂ and travel time effects are out of scope for us but worth acknowledging in limitations.

---

### Elvik (2010) — *The case for speed limits*
**What we get:**
- Three theoretical reasons speed limits are necessary: externalities, misperception of risk, coordination failure.
- Drivers systematically underestimate crash risk at high speeds.
- Speed limits reduce both mean and variance of speed — dual benefit.
- Explicitly discusses the Autobahn as the last major remnant of unregulated speed.

**Direct use:**
1. Provides the theoretical frame for *why* we expect ARR > 1 — not just empirical expectation but a theoretically grounded prediction.
2. The "speed limits reduce σ_v as well as v̄" point reinforces why speed dispersion must be modelled separately.
3. Use in the introduction/motivation section of the paper.

---

## 7. Summary Table: Paper → Metric Component

| Paper | Contributes to |
|---|---|
| Nilsson (2004) | ERF calculation — baseline Power Model exponents (4.0 fatalities) |
| Elvik (2013) | ERF calculation — upgraded exponents (4.6 fatalities); higher at high speeds |
| Elvik et al. (2019) | ERF robustness — Power Model validated with modern data |
| Aarts & van Schagen (2006) | Justifies σ_v as independent term; individual vs. aggregate speed risk |
| Vadeby & Forsman (2018) | Calibration of observed effect sizes; DiD template; compliance adjustment |
| Johansson (1996) | Statistical model choice (neg. binomial); serial correlation |
| Doecke et al. (2018) | Crash-type stratification; safe speed thresholds by crash type |
| Aarts & Houwing (2015) | Matched pair methodology; warns against naive cross-group comparisons |
| Hermans et al. (2009) | Validates DE/NL comparability; DEA as alternative composite |
| Wegman et al. (2008) | Theoretical basis for σ_v (homogeneity principle); NL as reference system |
| Bauernschuster & Rekers (2022) | Enforcement gap quantification; 7.5% effect size; drivers are responsive |
| Goldenbeld & van Schagen (2005) | Sustained enforcement 21% gain; enforcement as confounder in ARR |
| Bertini et al. (2006) | VSL_frac as control variable; 20% VSL effect |
| Weikl et al. (2013) | VSL before/after template; VSL reduces σ_v not only v̄ |
| Manner & Wünsch-Ziegler (2013) | Severity model covariates; VSL reduces severity |
| Bauernschuster & Traxler (2021) | Project motivation; 70% unlimited fraction; calls for causal evidence |
| Elvik (2010) | Theoretical framing; σ_v reduction as dual benefit of limits |

---

## 8. Gaps — What the Literature Does Not Give Us

| Gap | Implication |
|---|---|
| No paper provides section-level VKT for unlimited vs. limited DE sections | We must derive from BASt traffic counts |
| No paper directly computes ARR with full confounder control for DE/NL | This is our novel contribution |
| Speed distribution data (σ_v) at section level not in any paper | Must obtain from BASt loop detectors or probe data |
| iRAP star ratings not available in existing papers for our sections | May need to proxy via road geometry variables |
| Crash type breakdown for unlimited vs. limited sections not available | Would strengthen Doecke application |
| Compliance rate (how fast people actually drive on unlimited sections) | Critical for counterfactual — needs floating car or detector data |

---

*Last updated: 2026-03-18 · Status: draft*
