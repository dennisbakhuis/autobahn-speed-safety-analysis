Reasoning:
Dennis wants a focused overview of how to build a metric that fairly compares unlimited-speed Autobahn sections vs. ≤130 km/h highways. The key word is "fairly" — there are many confounders that could make unlimited sections look more or less dangerous than they actually are due to the speed policy itself.

Let me think through this carefully:

## The Core Causal Question
"Does removing the speed limit cause more deaths, holding everything else equal?"

This is a causal inference problem. The naive comparison (unlimited sections have higher fatality rates therefore unlimited is dangerous) is confounded by:
1. Selection bias in infrastructure: German unlimited sections tend to be on better infrastructure (straighter, wider, better barriers) — this could make them appear safer than they are

2. Traffic composition: Unlimited and limited sections differ in their mix of heavy vehicles and overall traffic volumes
3. Environmental factors: Geographic and weather conditions vary between regions — Alpine terrain versus flat plains create different baseline risks
4. Driver behavior: More experienced drivers may gravitate toward unlimited sections, and traffic patterns shift throughout the day in ways that could affect how speed policy impacts safety

## The Fair Comparison Problem

A proper comparison requires controlling for the road's inherent safety characteristics based on its physical design, normalizing by actual vehicle exposure rather than just distance, using consistent severity definitions across both road types, and accounting for differences in traffic composition.

## Approaches to a Fair Metric

I'm considering several methodological approaches. The simplest would be calculating fatality rates per vehicle-kilometer for each road type and using regression to isolate the effect of speed limits while controlling for infrastructure, traffic composition, and other confounders. Alternatively, I could match comparable unlimited and limited sections on observable characteristics and compare them directly, or use a power model to estimate what fatality rates would be on unlimited sections if they operated at 130 km/h instead, then compare that counterfactual to actual outcomes. The strongest approach would be analyzing sections that changed their speed policy over time, since that controls for fixed road characteristics.

For the final metric, I'm thinking of a ratio that compares observed fatality rates to what we'd expect given the road's infrastructure and traffic characteristics, using speed-limited sections as the reference class — this would show whether unlimited sections perform better or worse than their physical characteristics would predict.

## Key Methodological Challenges

The main issue is that unlimited sections tend to be built on better roads, so if I don't account for infrastructure quality, I'll overstate the danger of high speeds. The real driver of safety is actual driving speeds, not just the posted limit. There's also a potential homogeneity effect where unlimited sections have more consistent speeds and less mixed traffic, which could actually reduce crashes per kilometer. I need to be careful about differences in how Germany and the Netherlands report crashes, and ultimately I need to figure out what would actually happen if you imposed a 130 km/h limit on currently unlimited roads — that counterfactual is hard to pin down without time-series data from sections that have changed policies.

I think the clearest approach is to write a focused methodological document that walks through the causal question, identifies the key confounders, lays out candidate approaches like matched comparisons and regression adjustment, and specifies what data I'd need to make this work.


Saved to manuscript/METRIC_APPROACH.md. Here's the core logic:

───

The fundamental problem is that you can't naively compare raw fatality rates — unlimited sections sit on better roads (Germany puts limits on curves, black spots, construction zones). So a naive comparison would underestimate how dangerous unlimited speed is.

Four approaches, in order of credibility:

1. Regression-adjusted rate — fit a model controlling for infrastructure, traffic, HGV fraction, etc. The coefficient on "unlimited" is your adjusted risk premium. Most feasible.
2. Matched pair comparison — find limited sections with equivalent road quality and traffic, compare directly. Cleanest conceptually, requires enough comparable pairs.
3. Power Model counterfactual — use observed speeds + Elvik's exponent (4.6 for motorway fatalities) to compute what deaths would be at 130 km/h. Gives you an Excess Risk Fraction: "X% of deaths on unlimited sections are attributable to the speed policy."
4. Difference-in-differences — use sections that actually changed policy over time. Gold standard for causality, but rare.

The recommended metric is the Adjusted Risk Ratio (ARR):
ARR = FR_unlimited_adjusted / FR_limited_adjusted
The finding becomes "irresponsibly dangerous" if ARR > 1 after giving unlimited sections full credit for their infrastructure advantages. That's the most conservative and defensible framing — if they're still more deadly despite being better roads, the case is airtight.

The key insight: the fairness checklist (normalise by VKT, control for infrastructure, same severity definitions, include speed dispersion) is what separates a rigorous finding from a political talking point.
