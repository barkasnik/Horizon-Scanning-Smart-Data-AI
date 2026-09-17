# Smart Data & AI Horizon Scanner — Version 5

A visual, automated horizon-scanning tool for **UK Smart Data and AI policy intelligence**.

The radar discovers relevant public material, ranks it, analyses the most important items using a Government / Smart Data lens, and publishes a public-safe dashboard with weekly and monthly views.

## Dashboard

The root `index.html` is the GitHub Pages dashboard. It reads the generated JSON briefings from `output/` and displays:

- ranked news and policy developments
- urgency, impact, consequences, policy advancement, opportunity and monitoring scores
- strategic significance, implementation risk, novelty and evidence-strength scores
- humanised bottom-line analysis
- UK Government / Smart Data PESTLE
- UK Smart Data programme SWOT
- policy implications, tensions and follow-up questions
- controlled hashtags including `#PolicyGap`, `#Opportunity`, `#Threat`, `#Monitor`, `#AIxSmartData`, `#Interoperability`, `#Consent`, `#DigitalIdentity`, `#EconomicSecurity` and others
- direct links to the original articles

## Modes

**Weekly:** 7-day horizon, weighted toward urgency, immediate impact, consequences, monitoring and implementation risk.

**Monthly:** 30-day horizon, weighted toward strategic significance, cumulative impact, policy advancement, persistent gaps, opportunities and threats.

## Source stance

GOV.UK Smart Data material is a principal policy anchor. Government and regulator primary sources receive strong source weighting. Raidiam and Marie Walker are monitored because their material is often relevant to Smart Data infrastructure and AI, but the tool neither aligns with nor opposes Raidiam. Commercial arguments are identified as source perspective rather than treated as neutral fact.

## Zero-cost default

- Discovery: Google News RSS + direct monitored indexes
- Extraction: open-source Python tooling
- Analysis: Ollama + `qwen2.5:1.5b-instruct`
- Hosting: GitHub Pages
- Scheduling: GitHub Actions

No paid search or LLM API is required by default. Optional paid backends remain possible.

## Public-safe design

Public JSON contains provenance, links, scores and original radar analysis. It deliberately excludes scraped article bodies and discovery snippets.

## Installation

**Read [`START-HERE.md`](START-HERE.md) first.** It contains click-by-click instructions, especially important because the folder structure must be retained.

## Repository structure

```text
.github/workflows/radar.yml        scheduled/manual workflow
config/interest_profile.yml        topics, search phrases and editorial principles
config/sources.yml                 monitored sources and source/person boosts
src/smart_data_radar/              Python intelligence engine
tests/                             automated tests
output/                            generated weekly/monthly public briefings
index.html                         visual GitHub Pages dashboard
START-HERE.md                      non-technical setup guide
```

## Licence

MIT. Source articles remain the property of their publishers; the tool links to them rather than republishing their full text.
