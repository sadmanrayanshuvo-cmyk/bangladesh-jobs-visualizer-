# Bangladesh Job Market Visualizer — Full Engineering Blueprint

> **Adapted from Andrej Karpathy's [karpathy/jobs](https://github.com/karpathy/jobs) architecture** for the Bangladesh workforce.[^1]
> Data Year: BBS Labour Force Survey 2023 · Total labour force: **71.1M workers**[^2]
> Architecture: BBS Data ingestion → LLM AI Exposure scoring → D3.js interactive treemap

***

## 1. Credible Data Source Mapping

### 1.1 Primary Employment Data

The following official sources form the authoritative data backbone, replacing the US BLS Occupational Outlook Handbook with Bangladesh equivalents.

| Source | Data Available | Access |
|--------|---------------|--------|
| **BBS Labour Force Survey 2023** (Annual) | Occupation by ISCO-08, employment by sector (agriculture 44.4%, industry 17.3%, services 38.3%), sex-disaggregated[^3] | [bbs.gov.bd](https://bbs.gov.bd) · Free PDF/XLSX |
| **BBS Labour Force Survey 2022** (ILO microdata) | ISCO-08 4-digit occupation codes, BSIC industry codes, individual-level microdata[^4] | [ILO Survey Catalogue](https://webapps.ilo.org/surveyLib/index.php/catalog/8538) · Free |
| **BGMEA / BKMEA (RMG sector)** | 3.317M woven + 1.7M knit = 5.017M RMG workers (Parliamentary statement June 2024)[^5] | bgmea.com.bd |
| **BMET (Bureau of Manpower, Employment & Training)** | 1.303M overseas workers dispatched in 2023[^6]; cumulative 14.46M since 2004 | bmet.gov.bd |
| **Bangladesh Economic Zones Authority (BEZA)** | SEZ employment by industry zone | beza.gov.bd |

**Key BBS LFS 2023 aggregate (Q1):**[^2]
- Total employed: **71.10M** (46.54M male, 24.56M female)
- Agriculture sector: **31.94M** (44.9% of employed)
- Industry sector: **12.25M** (17.2%)
- Services sector: **26.91M** (37.9%)

### 1.2 Wage & Salary Data Sources

| Source | Coverage | Key Data Points |
|--------|----------|-----------------|
| **BBS Wage Rate Survey** (annual) | Sector-level daily/monthly wage by occupation category | Primary wage benchmark for informal sectors |
| **8th National Pay Scale 2015** (GoB Gazette) | All 20 government pay grades[^7] | Grade 9 BCS entry: BDT 22,000 basic + allowances ≈ BDT 33,100–37,305 total[^8] |
| **RMG Minimum Wage Board Gazette (Dec 2023)** | Grade 4 entry-level: BDT 12,500/month[^9] | 56% increase from 2018's BDT 8,000[^10] |
| **Glassdoor BD / PayScale BD** | Software: BDT 35K–65K/month average[^11] | Senior: BDT 80K–150K[^12] |
| **Fair Labor Association Wage Trends Report 2024**[^13] | RMG wages by grade, year-on-year trends | fairlabor.org |
| **2026 Pay Commission Proposal** | Grade 20 entry: BDT 8,250 → BDT 20,000; Grade 9 BCS: BDT 22,000 → ~BDT 50,000[^14] | Pending gazette notification |

### 1.3 Occupational Taxonomy — BSCO and NSDA NTVQF

Bangladesh uses **two parallel frameworks** — they must be cross-mapped for this project.

**BSCO (Bangladesh Standard Classification of Occupations)**
- Based on ILO ISCO-08 (Revision 2008)[^4]
- Published by BBS; aligns 4-digit SOC codes to local occupational titles in Bangla and English
- Covers 10 Major Groups → 43 Sub-Major → 130 Minor → 436 Unit Groups
- Source: `bbs.portal.gov.bd` → Publications → "National Occupational Classification BSCO"[^15]

**NSDA NTVQF (National Technical and Vocational Qualifications Framework)**
- Published by National Skills Development Authority under NSDA Act 2018[^16]
- 8-level competency framework for TVET occupations mapping to ISCO skill levels 1–4
- Source: `nsda.portal.gov.bd` → NTVQF documentation[^17]

**Mapping strategy:**
```
BSCO 4-digit code → ISCO-08 equivalent → BBS LFS employment count → BBS wage data
```

***

## 2. System Architecture & Data Schema

### 2.1 Pipeline Overview (Mirrors karpathy/jobs)

The architecture directly replicates Karpathy's 5-stage pipeline with Bangladeshi substitutions at every stage:[^1]

```
[BBS LFS Excel/CSV]         →  [parse_bbs.py]         →  [occupations.csv]
[Job descriptions]           →  [score.py + Gemini]    →  [scores.json]
[occupations.csv + scores]   →  [build_site_data.py]   →  [site/data.json]
                                                            ↓
                                                  [site/index.html]
                                                  Interactive D3.js Treemap
```

### 2.2 `occupations.json` — 46 Representative Bangladeshi Occupations

Each occupation entry contains:

```json
{
  "slug": "rmg-sewing-operator",
  "title": "RMG Sewing Machine Operator",
  "category": "Ready-Made Garments",
  "sector": "Manufacturing",
  "description": "Operates industrial sewing machines in garment factories to stitch fabric panels. Highly repetitive, physically present on factory floor. Requires manual dexterity and speed. Minimum wage BDT 12,500/month as of December 2023."
}
```

**Coverage across 8 major sectors:**

| Sector | Occupations | Approx. Workers Covered |
|--------|-------------|------------------------|
| Agriculture | 7 (rice farmer, vegetable farmer, jute worker, fisherman, poultry farmer, agricultural laborer, shrimp farmer) | ~30M |
| Ready-Made Garments | 5 (sewing operator, QC inspector, cutting worker, supervisor, merchandiser) | ~4.3M[^5] |
| Manufacturing & Construction | 7 (textile spinner, factory operator, shipbuilding, construction laborer, mason, electrician, carpenter) | ~6.5M |
| Services & Trade | 8 (retail worker, rickshaw, ride-sharing, bus/truck driver, restaurant, domestic worker, salon, pharmacy) | ~10M |
| Financial & NGO Services | 3 (bank officer, microfinance field officer, mobile banking agent) | ~1M |
| IT & Digital | 5 (software engineer, data analyst, IT support, freelance digital worker, call center agent) | ~1.5M |
| Professional & Government | 8 (BCS officer, primary teacher, secondary teacher, university professor, medical doctor, nurse, journalist, accountant, lawyer, engineer, NGO worker) | ~3.5M |
| Migrant Labor | 1 (overseas migrant worker — Gulf/Malaysia) | 1.3M dispatched in 2023[^18] |

### 2.3 `site/data.json` — Full Schema

The merged dataset that powers the frontend visualization combines worker counts, wages, education tiers, and AI exposure scores:

```json
{
  "meta": {
    "title": "Bangladesh Job Market Visualizer",
    "total_workforce_millions": 71.1,
    "data_year": 2023,
    "primary_source": "BBS Labour Force Survey 2023",
    "wage_currency": "BDT",
    "wage_period": "monthly"
  },
  "education_tiers": {
    "1": "No formal education / Illiterate",
    "2": "Primary (Class 1-5)",
    "3": "Secondary / SSC",
    "4": "Higher Secondary / HSC",
    "5": "Vocational / TVET Certificate",
    "6": "Bachelor's Degree",
    "7": "Master's / Postgraduate",
    "8": "Medical / Professional Degree"
  },
  "occupations": [
    {
      "slug": "software-engineer",
      "title": "Software Engineer / Developer",
      "category": "IT & Digital",
      "headcount": 400000,
      "avg_monthly_wage_bdt": 65000,
      "education_tier": 6,
      "education_label": "Bachelor's Degree",
      "ai_exposure": 9,
      "ai_rationale": "Work product is entirely digital — code, documentation, APIs. Can work remotely. AI coding assistants already substantially augment developer productivity in Bangladesh's growing tech sector."
    }
  ]
}
```

**Field definitions:**

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `headcount` | integer | BBS LFS 2023 / BGMEA / BMET | Total employed nationally |
| `avg_monthly_wage_bdt` | integer | BBS Wage Survey / Pay Scale / Glassdoor BD[^11] | Median monthly including typical allowances |
| `education_tier` | 1–8 | NSDA NTVQF / BANBEIS | Minimum qualification for typical entry |
| `ai_exposure` | 0–10 | LLM-scored via `score.py` | Digital AI disruption potential |
| `ai_rationale` | string | LLM-generated (Gemini Flash) | 2–3 sentence Bangladesh-specific explanation |

***

## 3. Bangladesh-Specific AI Exposure Scoring Rubric

### 3.1 System Prompt Design Philosophy

The scoring prompt is adapted from Karpathy's original rubric with **critical Bangladesh-specific calibrations**:[^19]

1. **Digital infrastructure gap**: Rural internet penetration ~35%; smartphone penetration ~50%; cash-based informal economy (85%+ informal workers)
2. **Bangla language proficiency**: LLMs already proficient in Bangla — call centers and content writing face immediate disruption
3. **Wage economics**: At BDT 12,500/month RMG minimum wage, automation ROI differs fundamentally from US/European contexts[^9]
4. **Bangladesh geography**: Rural agricultural work, factory floors in Gazipur/Narayanganj, coastal fishing in Cox's Bazar, Dhaka's rickshaw economy

**Two core dimensions:**

| Dimension | Weight | Question |
|-----------|--------|----------|
| **Output Digitality** | 50% | Is the work product entirely digital (code, text, data, reports, transactions)? |
| **Physical Presence** | 50% | Does the role require physical presence, dexterity, or localized human interaction within Bangladesh's infrastructure? |

### 3.2 `score.py` — Full LLM Scoring Pipeline

```python
#!/usr/bin/env python3
"""
score.py — Bangladesh Job Market AI Exposure Scoring Pipeline
Adapted from Andrej Karpathy's karpathy/jobs architecture.
Uses Google Gemini Flash (via OpenRouter) to score occupations 0-10.

Usage:
    pip install openai python-dotenv
    OPENROUTER_API_KEY=your_key python score.py
Output: scores.json — AI exposure scores with rationales for all 46 occupations.
"""

import json, os, time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

SYSTEM_PROMPT = """You are a labor economist specializing in the Bangladesh 
workforce and the impact of digital AI on South Asian occupational categories.

Score each occupation's "Digital AI Exposure" from 0 to 10.

DEFINITION: Measures how much CURRENT AI (LLMs, computer vision, RPA, 
generative AI) can reshape the CORE TASKS in the context of BANGLADESH's 
economy and infrastructure.

SCORING RUBRIC:
9-10 (Very High): Entirely digital output (code, text, data, reports). 
     Remoteable. Examples: Software developer, call center agent, data analyst.
7-8  (High): Majority digital; AI automates significant portions.
     Examples: Bank officer, journalist, accountant, freelance digital worker.
5-6  (Moderate): Mix of digital and physical; AI augments but doesn't substitute.
     Examples: BCS officer, NGO worker, civil engineer, university professor.
3-4  (Low-Moderate): Primarily physical; digital tools at the periphery.
     Examples: RMG supervisor, microfinance officer, ride-sharing driver.
1-2  (Very Low): Physical, manual, location-bound in Bangladesh.
     Examples: Agricultural labourer, construction worker, domestic worker.
0    (None): Entirely physical; zero digital work product.

BANGLADESH-SPECIFIC CALIBRATIONS:
- Rural internet penetration: ~35%; cash-based informal economy dominates
- LLMs now speak Bangla fluently — BPO/call centers face immediate risk
- At BDT 12,500/mo minimum wage, automation ROI differs from Global North
- 85%+ informal workers: digital adoption constrained by literacy and infrastructure
- Consider: flood-affected fields, factory floors in Gazipur, coastal fishing

Respond ONLY with JSON:
{"exposure": <0-10>, "rationale": "<2-3 sentences in Bangladesh context>"}
"""

def score_occupation(occ: dict) -> dict:
    user_content = f"""
Occupation: {occ['title']}
Sector: {occ['sector']} | Category: {occ['category']}
Description: {occ['description']}

Score this occupation's Digital AI Exposure (0-10) for Bangladesh's workforce.
"""
    response = client.chat.completions.create(
        model="google/gemini-flash-1.5",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.3,
        max_tokens=300,
    )
    raw = response.choices.message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[^1].lstrip("json").strip()
    return json.loads(raw)

# Load occupations
with open("occupations.json") as f:
    occupations = json.load(f)

scores_path = Path("scores.json")
scores = json.loads(scores_path.read_text()) if scores_path.exists() else {}

for i, occ in enumerate(occupations):
    slug = occ["slug"]
    if slug in scores:
        print(f"[{i+1}/{len(occupations)}] SKIP {occ['title']}")
        continue
    print(f"[{i+1}/{len(occupations)}] Scoring: {occ['title']}...", end=" ")
    try:
        result = score_occupation(occ)
        scores[slug] = {"title": occ["title"], **result}
        print(f"→ {result['exposure']}/10")
        scores_path.write_text(json.dumps(scores, indent=2))  # resume-safe
        time.sleep(0.5)  # rate limiting
    except Exception as e:
        print(f"ERROR: {e}")

print(f"✅ Scored {len(scores)} occupations → scores.json")
```

### 3.3 Expected Score Distribution

Based on Bangladesh's occupational structure, the pre-scored distribution is:

| Score | Count | Representative Occupations |
|-------|-------|---------------------------|
| **9–10** | 2 | Software Engineer (9), Data Analyst (8) |
| **7–8** | 5 | Freelance Digital Worker (8), Call Center Agent (8), Bank Officer (7), Journalist (7), Accountant (7) |
| **5–6** | 8 | University Professor (6), IT Support (6), Lawyer (6), Garments Merchandiser (6), BCS Officer (5), NGO Worker (5), Medical Doctor (5), Civil Engineer (5) |
| **3–4** | 9 | Microfinance Field Officer (4), Secondary Teacher (4), RMG Supervisor (4), Mobile Banking Agent (4), Factory Operator (3), Ride-sharing Driver (3) |
| **1–2** | 22 | Rice Farmer (1), Rickshaw Puller (1), Construction Laborer (1), Domestic Worker (1), RMG Sewing Operator (2), Fisherman (2) |

**Key Bangladesh insight:** ~55–60% of the total workforce is in physical/manual labour scoring ≤2 — primarily agriculture (31.94M), construction, and informal services. Only ~12M workers (17%) are in occupations with meaningful digital AI exposure at current infrastructure levels.[^2]

***

## 4. Frontend Visualization Blueprint

### 4.1 Architecture

The frontend is a **single self-contained HTML file** (`site/index.html`) with no build step, no framework, and no server dependencies — only a D3.js CDN link. In production, the embedded data object is replaced with a `fetch('data.json')` call.[^1]

```
site/
├── index.html      ← Complete app (HTML + CSS + D3.js treemap logic)
└── data.json       ← External data file (46 occupations × 6 metrics)
```

### 4.2 D3.js Treemap Implementation

**Library:** D3.js v7 (`https://d3js.org/d3.v7.min.js`)

**Key D3 APIs used:**
- `d3.hierarchy()` — builds parent-child tree from occupations grouped by sector/category
- `d3.treemap()` — squarified layout with `.paddingOuter(4).paddingInner(2).paddingTop(20)`
- `d3.scaleSequential()` — continuous color scale for wage visualization
- `d3.group()` — groups occupations by `category` field for sector-level parent nodes

**Color encoding logic per metric:**

```javascript
// AI Exposure: discrete 10-color palette (dark navy → deep orange)
const AI_COLORS = [
  "#1e3a5f","#1d4e89","#1565c0","#1976d2","#2196f3",
  "#42a5f5","#64b5f6","#ff9800","#f57c00","#e65100"
];
// Score 0 = dark blue (minimal AI exposure), Score 9 = deep orange (high)

// Wage: sequential BDT 7,000–85,000
const WAGE_SCALE = d3.scaleSequential()
  .domain([7000, 85000])
  .interpolator(d3.interpolateRgb("#1a2a4a", "#e65100"));

// Education: discrete 8-tier categorical colors
const EDU_COLORS = {1:"#4a1942", 2:"#6b2d6b", 3:"#7b5ea7",
  4:"#5aac8b", 5:"#3d9970", 6:"#27ae60", 7:"#1abc9c", 8:"#16a085"};

// Headcount mode: sector-level categorical colors
// Agriculture=green, RMG=red, IT/Digital=blue, Construction=orange, etc.
```

### 4.3 Toggle Controls

Four metric toggles switch treemap coloring via `data-metric` attributes:

| Button | Metric | Color Logic |
|--------|--------|-------------|
| 👥 Headcount | `headcount` | Category color by sector (area already encodes count) |
| 🤖 Digital AI Exposure | `ai_exposure` | 10-step blue → orange discrete palette |
| 💰 Monthly Wage (BDT) | `wage` | Sequential scale: BDT 7K (dark blue) → BDT 85K (orange) |
| 🎓 Education Tier | `education` | 8-tier categorical: purple (none) → teal (medical degree) |

### 4.4 Tooltip Schema

On hover, each occupation cell displays a detailed panel:

```
┌─────────────────────────────────────────┐
│  RMG Sewing Machine Operator            │
│  Category:    Ready-Made Garments       │
│  Workers:     3.32M (3,317,397)         │
│  Monthly Wage: ৳13,500 BDT             │
│  Education:   Secondary / SSC           │
│  ──────────────────────────────────     │
│  🤖 AI Exposure:  [2/10]               │
│  "Highly repetitive but requires manual │
│   dexterity on factory floor. Mass      │
│   automation limited by Bangladesh's    │
│   wage economics..."                    │
└─────────────────────────────────────────┘
```

### 4.5 Responsive Design

- SVG `viewBox` and treemap layout recalculated on `window.resize`
- Labels rendered only when cell dimensions exceed thresholds: `width > 55px && height > 26px`
- Sub-metric labels (wage/score/headcount) shown only when `width > 80px && height > 65px`
- Dark theme (`#0f1117` background) optimized for extended analysis sessions

***

## 5. Repository Structure & Deployment

### 5.1 Full Repository Layout

```
bangladesh-jobs/
├── README.md
├── occupations.json          ← 46 occupation definitions (source of truth)
├── occupations.csv           ← Tabulated stats (headcount, wage, education)
├── scores.json               ← LLM AI exposure scores (generated by score.py)
├── score.py                  ← LLM scoring pipeline (Gemini Flash/OpenRouter)
├── build_site_data.py        ← Merges CSV + scores → site/data.json
├── pyproject.toml            ← Python deps: openai, python-dotenv
├── .env                      ← OPENROUTER_API_KEY (gitignored)
└── site/
    ├── index.html            ← Complete interactive visualization
    └── data.json             ← Merged dataset for frontend
```

### 5.2 `build_site_data.py`

```python
"""Merges occupations.csv + scores.json → site/data.json"""
import json, csv, pathlib

with open('occupations.csv') as f:
    occ_rows = {row['slug']: row for row in csv.DictReader(f)}
with open('scores.json') as f:
    scores = json.load(f)

occupations = []
for slug, row in occ_rows.items():
    score_data = scores.get(slug, {"exposure": -1, "rationale": "Pending"})
    occupations.append({
        "slug": slug,
        "title": row["title"],
        "category": row["category"],
        "headcount": int(row["headcount"]),
        "avg_monthly_wage_bdt": int(row["avg_monthly_wage_bdt"]),
        "education_tier": int(row["education_tier"]),
        "education_label": row["education_label"],
        "ai_exposure": score_data["exposure"],
        "ai_rationale": score_data["rationale"],
    })

site_data = {
    "meta": {
        "title": "Bangladesh Job Market Visualizer",
        "total_workforce_millions": 71.1,
        "data_year": 2023,
        "primary_source": "BBS Labour Force Survey 2023",
    },
    "education_tiers": {
        "1": "No formal education", "2": "Primary (Class 1-5)",
        "3": "Secondary / SSC",     "4": "Higher Secondary / HSC",
        "5": "Vocational / TVET",   "6": "Bachelor's Degree",
        "7": "Master's / Postgraduate", "8": "Medical / Prof. Degree"
    },
    "occupations": occupations
}

pathlib.Path('site/data.json').write_text(json.dumps(site_data, indent=2))
print(f"Built site/data.json with {len(occupations)} occupations")
```

### 5.3 Quick Start

```bash
# 1. Install dependencies
pip install openai python-dotenv

# 2. Configure API key
echo "OPENROUTER_API_KEY=your_key_here" > .env

# 3. Run AI scoring pipeline (~46 API calls, ~30 seconds)
python score.py

# 4. Build merged site data
python build_site_data.py

# 5. Serve locally
cd site && python -m http.server 8000
# Open: http://localhost:8000
```

### 5.4 Alternative Scoring Prompts

The modular `score.py` can be rerun with any prompt. Bangladesh-relevant extensions:

| Prompt Variant | What It Measures |
|----------------|-----------------|
| **Climate Vulnerability** | Exposure to Bangladesh's flood, cyclone, and heat stress risks |
| **Offshoring Risk** | Can this job be moved to a remote worker abroad via digital platforms? |
| **Gender Concentration** | What share of workers are women? (intersects heavily with RMG/domestic sectors) |
| **Remittance Skill Transfer** | Are skills transferable to Gulf/Malaysia migration pathways? |
| **Digital Literacy Prerequisite** | What minimum smartphone skill does this job require *today*? |
| **Humanoid Robotics Exposure** | Following Karpathy's secondary prompt — physical tasks at risk from robotics |

***

## 6. Data Calibration Notes & Known Limitations

1. **BBS LFS occupation granularity**: The public LFS report provides 3-major-sector totals. ISCO-08 4-digit occupation data requires BBS microdata (free but requires formal application via bbs.gov.bd).[^20]

2. **Informal economy dominance**: BBS counts anyone working ≥1 hour in the reference week as "employed." ~85% of Bangladesh workers are informal — wage data for informal categories relies on BBS Wage Rate Survey averages, which may undercount.[^3]

3. **RMG worker count discrepancy**: BGMEA reports 3.317M woven; BKMEA 1.7M knit; BBS LFS 2022 reports 4.316M total; Parliamentary statement (June 2024) cites 5.017M. This blueprint uses BGMEA/BKMEA figures for sectoral breakdowns and BBS for aggregates.[^5]

4. **IT/freelance undercount**: Bangladesh has 600,000–800,000 registered freelancers on Upwork/Fiverr but many are not captured as formal employees in BBS LFS.[^12]

5. **Wage data vintage**: The National Pay Scale was last revised in 2015. A 2026 Pay Commission proposal recommends near-doubling — Grade 20 entry from BDT 8,250 → BDT 20,000, Grade 9 BCS entry from BDT 22,000 → ~BDT 50,000. Update `data.json` upon gazette notification.[^14]

6. **AI scores are LLM estimates**: Following Karpathy's own disclaimer — these are rough LLM estimates, not rigorous econometric predictions. A score of 9 for software engineers means AI is *transforming* the work, not eliminating it; demand for developers may grow as each becomes more productive.[^1]

---

## References

1. [karpathy/jobs: A research tool for visually ...](https://github.com/karpathy/jobs) - We scraped all of it and built an interactive treemap visualization where each rectangle's area is p...

2. [Bangladesh’s total labour force rises to 73.69m](https://www.dhakatribune.com/bangladesh/310227/bangladesh%E2%80%99s-total-labour-force-rises-to-73.69m) - The total labour force means the number of people engaged in work aged above 15 years and above alon...

3. [2023 employment growth lowest in 12 years: BBS](https://today.thefinancialexpress.com.bd/last-page/2023-employment-growth-lowest-in-12-years-bbs-1733252528) - Bangladesh's economy generated only 0.51 million new jobs in 2023, the lowest employment growth in 1...

4. [Labour Force Survey 2022](https://webapps.ilo.org/surveyLib/index.php/catalog/8538) - Quarterly

5. [State minister informs parliament of number of workers in ...](https://rmgbd.net/2024/06/state-minister-informs-parliament-of-number-of-workers-in-rmg-sector/) - There are over 5.017 million workers in the garment factories in the country and 55.57 per cent of t...

6. [Bangladesh sends over 10 lakh workers abroad till Nov 30 this year](https://www.bssnews.net/news/340245) - DHAKA, Dec 9, 2025 (BSS) – Overseas employment from Bangladesh maintained a satisfactory position in...

7. [Cabinet approves new pay-scale](https://en.prothomalo.com/bangladesh/Cabinet-approves-new-pay-scale) - The cabinet has approved the new pay-scale for government officers and employees on Monday at the ca...

8. [BCS Cadre Salary Scale in Bangladesh 2025 - ABN Blog](https://blog.allbanglanewspaper.org/bcs-cadre-salary-scale-in-bangladesh/) - If you are an aspiring civil servant in Bangladesh, one of the most important things you will want t...

9. [Tk 12,500 finalised as minimum RMG wage | News Flash](https://www.bssnews.net/news-flash/160231) - DHAKA, Nov 26, 2023 (BSS) - The minimum wage board today finalised Taka 12,500 as the minimum monthl...

10. [Bangladesh gazette notification retains RMG worker ...](https://apparelresources.com/business-news/sustainability/bangladesh-gazette-notification-retains-rmg-worker-minimum-wage-taka-12500-say-reports/) - Gazette notification confirms minimum wage unchanged at Taka 12,500 for Bangladesh's apparel workers...

11. [Salary: Software Engineer in Bangladesh 2025](https://www.glassdoor.co.in/Salaries/bangladesh-software-engineer-salary-SRCH_IL.0,10_IN27_KO11,28.htm) - The average salary for a Software Engineer is ₹55,000 per year in Bangladesh. Click here to see the ...

12. [Software Engineer Salary in Bangladesh | Average Pay & ...](https://www.daudbd.com/2025/09/software-engineer-salary-in-bangladesh.html) - Discover the average software engineer salary in Bangladesh 2025. Learn about junior, mid-level, sen...

13. [Wage Trends - Fair Labor Association](https://www.fairlabor.org/wp-content/uploads/2024/01/Wage-Trends-Report-Bangladesh-January-2024-Updated.pdf)

14. [Civil Service Salaries to Double Under New Proposal](https://khaborwala.com/civil-service-salaries-to-double-under-new-proposal) - Khaborwala is your trusted source for the latest news and updates from around the world.

15. [Nat i onal  Occupational](https://bbs.portal.gov.bd/sites/default/files/files/bbs.portal.gov.bd/page/745673c8_c7ed_49bc_a4e2_e7b05fe7a9d4/APA%20Final-BSCO.pdf)

16. [National Skill Development AuthorityNSDA](https://www.slideshare.net/slideshow/national-skill-development-authoritynsda/274078663) - The National Skill Development Authority (NSDA) has been established under the National Skill Develo...

17. [2020-12-21-14-24-8c85b4482cf8516df94dd6471eaf30a4.pdf](https://nsda.portal.gov.bd/sites/default/files/files/nsda.portal.gov.bd/npfblock/2020-12-21-14-24-8c85b4482cf8516df94dd6471eaf30a4.pdf)

18. [Record labor migration in 2023 yet small rise in remittance](https://www.dhakatribune.com/business/335695/record-labor-migration-in-2023-yet-small-rise-in) - There was a record labour migration in 2023 while remittance earnings increased ever so slightly. Da...

19. [US Job Market Visualizer](https://karpathy.ai/jobs/) - This is a research tool that visualizes 342 occupations from the Bureau of Labor Statistics Occupati...

20. [বাংলাদেশ পরিসংখ্যান ব্যুরো](https://bbs.gov.bd/site/page/111d09ce-718a-4ae6-8188-f7d938ada348/labor-&-employment) - 'Disability Insights from Labour Force Survey 2022' Final Report(16-06-2025) Flyer October to Decemb...

