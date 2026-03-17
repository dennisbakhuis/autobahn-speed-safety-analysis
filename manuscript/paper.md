# Speed Without Limits: A Data-Driven Analysis of Fatality Rates on Unlimited-Speed German Autobahn Sections Compared to Speed-Limited Motorways and Dutch Motorways

**Dennis Bakhuis**  
2026

---

## Abstract

Germany is the only country in the European Union that permits unlimited driving speeds on a substantial share of its motorway network. This paper investigates whether unlimited-speed sections of the German Autobahn (Bundesautobahn) are disproportionately dangerous relative to speed-limited sections of the same network and relative to Dutch motorways (autosnelwegen), which are subject to speed limits of 100–130 km/h. Using accident microdata from the German Unfallatlas (2016–2024), the Dutch BRON dataset (2010–2024), and long-term aggregate statistics from Destatis (1979–2021), we compute fatality severity indices (fatalities per 1,000 accidents) and rate ratios for each group. We find that accidents on unlimited-speed Autobahn sections are, on average, 42% more likely to be fatal than accidents on speed-limited sections of the same network (16.0 vs. 11.3 per 1,000 accidents; 2016–2024 mean). Both German categories show a fatality severity 5–7 times higher than Dutch motorways (2.3 per 1,000 accidents). The rate ratio of unlimited to limited sections exceeded 2.0 in 2020 and remained above 1.0 in every year of the study period. These findings are consistent with the Power Model of speed and safety (Nilsson, 2004; Elvik, 2013) and provide strong empirical support for introducing a general speed limit on German motorways.

---

## 1. Introduction

The German Autobahn is one of the world's most recognisable motorway networks, in part because approximately 70% of its total length carries no permanent speed limit (Bauernschuster & Traxler, 2021). Drivers on unrestricted sections may legally travel at any speed their vehicle can sustain. This policy is unique among Western democracies and stands in contrast to the rest of the European Union, where motorway speed limits of 110–130 km/h are universal.

The safety implications of this policy have been debated for decades. Proponents of the status quo argue that German drivers are experienced, Autobahn infrastructure is of high quality, and that unrestricted sections are self-selecting for low-traffic, high-visibility conditions. Opponents cite the Power Model of speed and safety (Nilsson, 2004), which predicts that fatalities scale with approximately the fourth power of speed — meaning a vehicle travelling at 180 km/h is, under the model, roughly 23 times as likely to cause a fatality as one travelling at 90 km/h.

This paper contributes empirical evidence to this debate using large-scale accident microdata from Germany and the Netherlands. We address three research questions:

1. Do unlimited-speed Autobahn sections have a higher fatality severity index than speed-limited Autobahn sections?
2. How does German motorway fatality severity compare to Dutch motorways?
3. Has the safety gap between unlimited and limited sections been stable or changing over time (2016–2024)?

---

## 2. Related Work

### 2.1 The Power Model of Speed and Safety

The theoretical backbone of speed-safety research is the Power Model, originally formulated by Nilsson (2004) and subsequently updated by Elvik (2013) and Elvik et al. (2019). The model relates a change in mean traffic speed to a proportional change in crash outcomes:

- **Injury accidents:** A₂/A₁ = (v₂/v₁)²
- **Fatal accidents:** F₂/F₁ = (v₂/v₁)³
- **Fatalities:** D₂/D₁ = (v₂/v₁)⁴

Elvik (2013) re-estimated the exponents using 115 studies and found that the exponent for fatal accidents on motorways/freeways is approximately 4.1 (95% CI: 2.9–5.3), suggesting the original Nilsson exponents may be conservative at high initial speeds. Elvik et al. (2019) confirmed these findings using post-2000 data, ruling out the hypothesis that modern vehicle safety technology has decoupled the speed–fatality relationship.

### 2.2 Empirical Evidence on German Autobahn Safety

Manner & Wünsch-Ziegler (2013) analysed accident severity on the North Rhine-Westphalia Autobahn (2009–2011) using multinomial logit models and found that intelligent traffic control systems — effectively variable speed limits — significantly reduced accident severity, providing direct evidence that speed restriction on the Autobahn improves outcomes. Bertini et al. (2006) and Weikl et al. (2013) both report that German variable speed limit systems have reduced crash rates by up to 20% on the sections where they are deployed.

Bauernschuster & Traxler (2021) reviewed the macroeconomic and safety evidence for a 130 km/h general limit, concluding that the Power Model and international studies jointly predict a significant reduction in fatalities, with additional benefits in CO₂ emissions and fuel consumption. Bauernschuster & Rekers (2022) further demonstrated that German drivers reduce their speed measurably in response to increased enforcement (Blitzmarathon operations), confirming that many currently drive above safe speeds when enforcement is absent.

### 2.3 Speed and Crash Risk: General Evidence

Aarts & van Schagen (2006) reviewed the international literature and found that the speed–crash relationship is unambiguous in direction: no study found that higher speeds reduce crash rates. The effect is present at both the individual vehicle level (exponential function) and the road section level (power function). Johansson (1996) demonstrated, using time series count data models, that a speed limit reduction on Swedish motorways decreased casualty counts — a direct natural experiment analogy to the Autobahn case.

Vadeby & Forsman (2018) exploited Sweden's 2008–2009 nationwide speed limit reform as a natural experiment, finding that motorway speed limit increases to 120 km/h led to a significant increase in seriously injured victims (~15 per year), while reductions saved an estimated 17 lives per year across the affected network. Doecke et al. (2018) provided crash-type-specific empirical thresholds from Australian data, finding that speeds above 100 km/h only meet Safe System criteria where collision types other than rear-end are exceedingly rare — a condition met on standard motorways but not on sections where lateral and head-on collisions occur at very high speeds.

### 2.4 Dutch Road Safety as a Benchmark

The Netherlands consistently ranks among the safest road environments in the world. Hermans et al. (2009), using data envelopment analysis across 21 European countries, identified the Netherlands as a benchmark performer. Wegman et al. (2008) attribute this to the country's Sustainable Safety programme, of which **speed homogeneity** is an explicit core principle: mixing vehicles at widely different speeds is inherently dangerous. Goldenbeld & van Schagen (2005) demonstrated that sustained speed enforcement in the Netherlands produces lasting reductions in mean speed and a 21% reduction in injury accidents — in contrast to one-day enforcement campaigns, which produce only temporary effects (Bauernschuster & Rekers, 2022).

---

## 3. Data and Methods

### 3.1 German Accident Data

**Unfallatlas (2016–2024):** The German Unfallatlas is a geo-referenced microdata set of all police-recorded personal-injury road accidents in Germany, published annually by the Federal Statistical Office (Destatis) and state statistical offices. Each record includes GPS coordinates, accident year, and severity category (fatal / severe injury / slight injury). We use data for 2016–2024, covering nine years of observation.

**Destatis aggregate series (1979–2021):** Long-term aggregate counts of personal-injury accidents and fatal accidents on the Autobahn network, used for historical trend analysis.

### 3.2 Netherlands Accident Data

**BRON (2010–2024):** The Basic Road Accidents Registration (Bestand geRegistreerde Ongevallen in Nederland) dataset, maintained by the Dutch National Police and Rijkswaterstaat (RWS), contains police-recorded accidents on the national road network. The variable `MAXSNELHD` (posted speed limit) directly identifies motorway accidents without requiring a spatial join. We classify as motorways all records with `MAXSNELHD ∈ {100, 120, 130}` and `BEBKOM = 'BU'` (outside built-up area).

**Important data quality note:** The BRON dataset underwent a significant expansion in recording scope around 2013–2014, greatly increasing the number of minor and property-damage accidents captured. This artefact produces an apparent dramatic drop in the severity index before 2015 that does not reflect a genuine safety improvement of that magnitude. For cross-country comparisons, we focus on the **2016–2024 overlap period** for Germany and the **post-2015 stable period** for the Netherlands.

### 3.3 Motorway Classification for Germany

We downloaded the complete German motorway network from OpenStreetMap (OSM) using OSMnx and extracted the `maxspeed` tag for each segment. Sections are classified as **unlimited** if the `maxspeed` tag is absent, set to `DE:motorway`, `DE`, `none`, or `signals`. Sections with explicit numeric speed limits (100, 120, 130 km/h) are classified as **speed-limited**. Accidents are assigned to the nearest motorway segment within a 50-metre buffer via spatial join (EPSG:25832).

### 3.4 Primary Metric

Our primary outcome measure is the **fatality severity index**: the number of fatal accidents per 1,000 total accidents (including fatal, severe injury, and slight injury) in each group. This metric normalises for differences in traffic volume reporting and network length between the groups and countries, and is directly comparable across years.

---

## 4. Results

### 4.1 Long-Term German Autobahn Trend (1979–2021)

Fatal accidents on the Autobahn network peaked at approximately 1,250 in 1990–1991, coinciding with German reunification and rapid network expansion. They declined steeply to approximately 300–400 by 2010 — a reduction of ~70% — and have remained roughly stable since, with approximately 300 fatal accidents in 2021. This long-run improvement reflects vehicle safety improvements, trauma care advances, and gradual expansion of speed-limited sections, but the rate of improvement has clearly plateaued since ~2010 (Figure 1).

### 4.2 Severity Index by Road Type: Germany 2016–2024

Figure 2 presents the annual fatality severity index for three road categories: unlimited Autobahn, speed-limited Autobahn, and non-motorway roads. In every year from 2016 to 2024, the three-tier hierarchy holds: unlimited Autobahn > speed-limited Autobahn ≥ non-motorway.

Key observations:
- **Unlimited Autobahn** severity ranged from 13 to 21 per 1,000 accidents, with the highest value recorded in 2020 (21), likely reflecting changed traffic composition during COVID-19 restrictions (reduced commercial traffic, increased high-speed recreational driving on empty roads).
- **Speed-limited Autobahn** severity ranged from 8.7 to 14.3 per 1,000 accidents, with a clear downward trend reaching 9.2 by 2024.
- **Non-motorway** roads showed the flattest trend, declining gradually from ~10 to ~9 per 1,000 accidents.
- The gap between unlimited and speed-limited sections was smallest in 2018 (ratio: 1.12) and largest in 2020 (ratio: 2.10).

### 4.3 Period-Average Severity Index (2016–2024)

Averaging across the full study period (Figure 5):

| Group | Fatalities per 1,000 accidents | Ratio vs NL motorways |
|---|---|---|
| DE: Unlimited Autobahn | **16.04** | 7.1× |
| DE: Speed-limited Autobahn | **11.28** | 5.0× |
| NL: Motorways | **2.27** | — |

Unlimited Autobahn sections show a fatality severity index **42% higher** than speed-limited sections (16.04 vs. 11.28). Both German categories substantially exceed Dutch motorways.

### 4.4 Rate Ratio: Unlimited vs. Speed-Limited Autobahn (2016–2024)

Figure 6 shows the year-by-year rate ratio of unlimited to speed-limited Autobahn fatality severity. The ratio was **above 1.0 in every single year**, confirming that the elevated risk of unlimited sections is not an artefact of a single exceptional year:

| Year | Ratio |
|---|---|
| 2016 | 1.22 |
| 2017 | 1.50 |
| 2018 | 1.12 |
| 2019 | 1.30 |
| 2020 | 2.10 |
| 2021 | 1.32 |
| 2022 | 1.41 |
| 2023 | 1.60 |
| 2024 | 1.41 |
| **Mean** | **~1.42** |

### 4.5 Netherlands Motorway Comparison (2016–2024)

Dutch motorway fatality severity stabilised at approximately 2–3 per 1,000 accidents from 2016 onwards (Figure 3, Figure 4). The DE vs. NL comparison reveals:

- Unlimited Autobahn sections have a fatality severity approximately **6–10× higher** than Dutch motorways in the 2016–2024 period.
- Speed-limited Autobahn sections have a fatality severity approximately **3–6× higher** than Dutch motorways.
- Even the safer German category (speed-limited) is nearly **five times** as fatal per accident as a Dutch motorway.

The magnitude of this gap is striking. Both countries use similar vehicle fleets and have comparable trauma care systems. The most plausible explanations are (a) the dramatically higher operating speeds on both categories of German motorway relative to the Netherlands, and (b) the Netherlands' Sustainable Safety programme, which includes consistent speed enforcement, infrastructure designed to prevent high-energy collisions, and a 130 km/h motorway limit that was further reduced to 100 km/h (daytime) in 2020 for environmental reasons.

---

## 5. Discussion

### 5.1 Consistency with the Power Model

Our empirical findings are directionally consistent with the Power Model. The Power Model predicts that if unlimited Autobahn sections have a mean operating speed roughly 20–30 km/h higher than speed-limited sections (a reasonable assumption given observed speed distributions), fatality rates should be 40–100% higher. Our observed mean ratio of ~1.42 (42% higher) is at the lower end of this prediction, suggesting either that our speed differential assumption is conservative, or that drivers on unlimited sections are partially self-selecting for lower-risk conditions (better weather, less congestion). Either way, the direction of the effect is unambiguous and the magnitude is policy-relevant.

### 5.2 The Netherlands Gap

The five-to-sevenfold difference in fatality severity between German and Dutch motorways is difficult to explain solely by speed policy. Potential confounders include:

- **Recording differences:** If Germany records a higher proportion of minor accidents (thereby inflating the denominator), the German severity index would be artificially deflated. The true gap could be larger or smaller depending on the recording threshold.
- **Traffic mix:** Dutch motorways carry a higher share of commercial vehicles and less high-speed passenger traffic; heavy goods vehicles tend to be involved in crashes at lower relative speeds.
- **Road design:** Dutch motorways are designed under the Sustainable Safety framework, which explicitly minimises the probability of high-energy crashes through median barriers, clear zones, and forgiving run-off areas.
- **Speed enforcement:** Dutch motorways have consistent section control (trajectory speed enforcement) on many sections; German Autobahn unlimited sections have essentially no speed enforcement by definition.

Despite these confounders, the scale of the gap strongly suggests that operating speed is a primary contributor. Even if we conservatively attribute half the gap to confounders, a remaining 2.5–3.5× safety disadvantage for German motorways is practically significant.

### 5.3 Limitations

- **No vehicle-kilometres-travelled (VKT) normalisation:** Our metric is fatalities per accident, not fatalities per vehicle-km. Sections with different traffic volumes or travel speeds may have different denominators. A VKT-normalised rate would be a stronger measure of exposure-adjusted risk; however, section-level VKT is not available in the Unfallatlas.
- **OSM tag completeness:** The `maxspeed` tag in OSM is user-contributed and may be incomplete or outdated for some sections. Our unlimited classification may include some sections that have recently received a limit and vice versa.
- **BRON recording change:** The expansion of Dutch accident recording around 2013–2014 creates a discontinuity that prevents reliable pre/post comparisons; we address this by focusing on the post-2015 period.
- **Causal identification:** This is an observational study. We cannot rule out selection effects (e.g., unlimited sections being on routes with different driver populations or traffic compositions). A natural experiment — such as a policy-induced speed limit introduction on specific sections — would allow stronger causal inference.

---

## 6. Conclusion

Unlimited-speed sections of the German Autobahn show a consistently and substantially higher fatality severity index than speed-limited sections of the same network. Over the 2016–2024 study period, accidents on unlimited sections were on average 42% more likely to be fatal than accidents on speed-limited sections, with the ratio above 1.0 in every single year. Both German categories show fatality severity 5–7 times higher than Dutch motorways.

These findings are consistent with the Power Model of speed and safety and with evidence from Swedish, Australian, and Dutch natural experiments. Taken together, the evidence base provides strong support for the introduction of a general speed limit on German motorways. Based on prior estimates and the Power Model, a limit of 130 km/h on currently unlimited sections would be expected to reduce fatalities on those sections by 20–40%, equivalent to saving tens of lives per year.

The Netherlands provides proof of concept: a comparable motorway network, operating under consistent speed limits and a Sustainable Safety philosophy, achieves fatality rates that are an order of magnitude lower. Germany's exceptional status as the last major economy to permit unrestricted motorway speeds is not associated with exceptional safety outcomes — quite the opposite.

---

## Figures

- **Figure 1** — German Autobahn: long-term personal-injury and fatal accident trends (Destatis, 1979–2021). `output/figures/fig01_destatis_longterm.png`
- **Figure 2** — Severity index by road type, Germany, 2016–2024 (Unfallatlas). `output/figures/fig02_de_severity_by_roadtype.png`
- **Figure 3** — Netherlands motorway accident trends (BRON, 2010–2024). `output/figures/fig03_nl_motorway_trends.png`
- **Figure 4** — Severity index comparison: DE unlimited, DE limited, NL motorways (2016–2024). `output/figures/fig04_de_vs_nl_severity_index.png`
- **Figure 5** — Period-mean severity index bar chart by group (2016–2024). `output/figures/fig05_summary_bar.png`
- **Figure 6** — Rate ratio (unlimited ÷ limited Autobahn), fatality severity by year (2016–2024). `output/figures/fig06_rate_ratio_unlimited_vs_limited.png`

---

## References

Aarts, L., & van Schagen, I. (2006). Driving speed and the risk of road crashes: A review. *Accident Analysis & Prevention, 38*(2), 215–224. https://doi.org/10.1016/j.aap.2005.07.004

Aarts, L., & Houwing, S. (2015). Benchmarking road safety performance by grouping local territories: A study in the Netherlands. *Transportation Research Part A, 74*, 174–185. https://doi.org/10.1016/j.tra.2015.02.008

Bauernschuster, S., & Traxler, C. (2021). Tempolimit 130 auf Autobahnen: Eine evidenzbasierte Diskussion der Auswirkungen. *Perspektiven der Wirtschaftspolitik, 22*(2), 86–102. https://doi.org/10.1515/pwp-2021-0023

Bauernschuster, S., & Rekers, J. (2022). Speed limit enforcement and road safety. *Journal of Public Economics, 209*, 104663. https://doi.org/10.1016/j.jpubeco.2022.104663

Bertini, R. L., Boice, S., & Bogenberger, K. (2006). Dynamics of variable speed limit system surrounding bottleneck on German autobahn. *Transportation Research Record, 1978*, 149–159. https://doi.org/10.3141/1978-20

Doecke, S., Kloeden, C., Dutschke, J., & Baldock, M. (2018). Safe speed limits for a safe system: The relationship between speed limit and fatal crash rate for different crash types. *Traffic Injury Prevention, 19*(4), 404–408. https://doi.org/10.1080/15389588.2017.1422601

Elvik, R. (2010). A restatement of the case for speed limits. *Transport Policy, 17*(3), 196–204. https://doi.org/10.1016/j.tranpol.2009.12.006

Elvik, R. (2013). A re-parameterisation of the Power Model of the relationship between the speed of traffic and the number of accidents and accident victims. *Accident Analysis & Prevention, 50*, 854–860. https://doi.org/10.1016/j.aap.2012.07.012

Elvik, R., Vadeby, A., Hels, T., & van Schagen, I. (2019). Updated estimates of the relationship between speed and road safety at the aggregate and individual levels. *Accident Analysis & Prevention, 123*, 114–122. https://doi.org/10.1016/j.aap.2018.11.014

Goldenbeld, C., & van Schagen, I. (2005). The effects of speed enforcement with mobile radar on speed and accidents. *Accident Analysis & Prevention, 37*(6), 1135–1144. https://doi.org/10.1016/j.aap.2005.06.011

Hermans, E., Brijs, T., Wets, G., & Vanhoof, K. (2009). Benchmarking road safety: Lessons to learn from a data envelopment analysis. *Accident Analysis & Prevention, 41*(1), 174–182. https://doi.org/10.1016/j.aap.2008.10.010

Johansson, P. (1996). Speed limitation and motorway casualties: A time series count data regression approach. *Accident Analysis & Prevention, 28*(1), 73–87. https://doi.org/10.1016/0001-4575(95)00043-7

Manner, H., & Wünsch-Ziegler, L. (2013). Analyzing the severity of accidents on the German Autobahn. *Accident Analysis & Prevention, 57*, 40–48. https://doi.org/10.1016/j.aap.2013.03.022

Nilsson, G. (2004). *Traffic Safety Dimensions and the Power Model to Describe the Effect of Speed on Safety.* Bulletin 221, Lund Institute of Technology.

Vadeby, A., & Forsman, Å. (2018). Traffic safety effects of new speed limits in Sweden. *Accident Analysis & Prevention, 114*, 34–39. https://doi.org/10.1016/j.aap.2017.02.003

Wegman, F., Aarts, L., & Bax, C. (2008). Advancing sustainable safety: National road safety outlook for The Netherlands for 2005–2020. *Safety Science, 46*(2), 323–343. https://doi.org/10.1016/j.ssci.2007.06.013

Weikl, S., Bogenberger, K., & Bertini, R. L. (2013). Traffic management effects of variable speed limit system on a German autobahn: Empirical assessment before and after system implementation. *Transportation Research Record, 2380*, 48–60. https://doi.org/10.3141/2380-06
