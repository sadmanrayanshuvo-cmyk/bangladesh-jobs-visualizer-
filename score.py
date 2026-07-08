#!/usr/bin/env python3
"""
score.py — Bangladesh Job Market AI Exposure Scoring Pipeline
Adapted from Andrej Karpathy's karpathy/jobs architecture for the Bangladesh workforce.
Uses Google Gemini Flash (via OpenRouter) to score 46 occupations on Digital AI Exposure (0-10).

Usage:
    pip install openai python-dotenv
    OPENROUTER_API_KEY=your_key_here python score.py

Output: scores.json — AI exposure scores with rationales for all occupations.
"""

import json
import os
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

# ─────────────────────────────────────────────────────────────────
# SYSTEM PROMPT — Bangladesh-Specific AI Exposure Rubric
# ─────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a labor economist specializing in the Bangladesh workforce and the impact of digital AI on South Asian occupational categories.

Your task: Score each occupation's "Digital AI Exposure" from 0 to 10.

## Definition
"Digital AI Exposure" measures how much CURRENT AI (large language models, computer vision, robotic process automation, generative AI tools) can reshape the CORE TASKS of this occupation IN THE CONTEXT OF BANGLADESH'S ECONOMY AND INFRASTRUCTURE.

This is NOT a prediction of job loss. A score of 9 for software engineers means AI is transforming HOW they work, not that they disappear.

## Scoring Rubric

**Score 9-10 (Very High Exposure)**
- Work product is ENTIRELY digital (code, text, data, reports, spreadsheets)
- Core tasks include: writing, translating, coding, data entry, analysis, customer service via chat
- Can be performed remotely via internet
- Examples: Software developer, call center agent, data analyst, content writer, accountant

**Score 7-8 (High Exposure)**
- Majority of work output is digital but some physical presence required
- AI can automate significant portions of the role (document processing, scheduling, analysis)
- Examples: Bank officer, journalist, lawyer, university professor, BPO agent

**Score 5-6 (Moderate Exposure)**
- Mix of digital work and physical presence
- AI can augment but not substitute core tasks
- Some digital tools already in use
- Examples: BCS official, NGO worker, civil engineer, IT support

**Score 3-4 (Low-Moderate Exposure)**
- Primarily physical but some digital components exist
- AI tools at the periphery (scheduling apps, quality inspection AI)
- Examples: RMG supervisor, microfinance officer, pharmacist, ride-sharing driver

**Score 1-2 (Very Low Exposure)**
- Core work is PHYSICAL, MANUAL, and LOCATION-BOUND in Bangladesh
- Requires physical dexterity, human presence, or operates in environments without reliable digital infrastructure
- Bangladesh-specific: rural areas, informal economy, manual trades
- Examples: Agricultural labourer, rickshaw puller, domestic worker, garment sewing operator, fisherman

**Score 0 (No Exposure)**
- Entirely physical manual labour with zero digital work product
- AI cannot meaningfully interact with the work in Bangladesh's current context

## Bangladesh-Specific Calibration
- Consider Bangladesh's ACTUAL digital infrastructure: patchy rural internet, smartphone penetration ~50%, cash-based informal economy
- Do NOT assume US/European levels of automation. A call center agent in Dhaka faces disruption differently than one in California — but LLMs speaking Bangla are already advanced.
- Weight physical presence in Bangladesh's geography: rural agriculture, factory floors, coastal fishing, Dhaka traffic
- Consider the informal economy: 85%+ of Bangladesh workers are informal, limiting digital adoption

## Output Format
Respond with ONLY a JSON object in this exact format, no other text:
{"exposure": <0-10>, "rationale": "<2-3 sentences explaining the score in Bangladesh's economic context>"}
"""

# ─────────────────────────────────────────────────────────────────
# Load occupations
# ─────────────────────────────────────────────────────────────────
with open("occupations.json") as f:
    occupations = json.load(f)

scores_path = Path("scores.json")
if scores_path.exists():
    with open(scores_path) as f:
        scores = json.load(f)
else:
    scores = {}

# ─────────────────────────────────────────────────────────────────
# Scoring loop
# ─────────────────────────────────────────────────────────────────
def score_occupation(occ: dict) -> dict:
    """Send one occupation to LLM and return {exposure, rationale}."""
    user_content = f"""
Occupation: {occ['title']}
Sector: {occ['sector']}
Category: {occ['category']}

Job Description (Bangladesh context):
{occ['description']}

Score this occupation's Digital AI Exposure (0-10) for the Bangladesh workforce.
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
    raw = response.choices[0].message.content.strip()
    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

def main():
    total = len(occupations)
    for i, occ in enumerate(occupations):
        slug = occ["slug"]
        if slug in scores:
            print(f"[{i+1}/{total}] SKIP {occ['title']} (already scored)")
            continue

        print(f"[{i+1}/{total}] Scoring: {occ['title']}...", end=" ", flush=True)
        try:
            result = score_occupation(occ)
            scores[slug] = {
                "title": occ["title"],
                "exposure": result["exposure"],
                "rationale": result["rationale"]
            }
            print(f"Score: {result['exposure']}/10")

            # Save after each occupation (resume-safe)
            with open(scores_path, "w") as f:
                json.dump(scores, f, indent=2)

            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"ERROR: {e}")
            scores[slug] = {"title": occ["title"], "exposure": -1, "rationale": f"Error: {e}"}

    print(f"\n✅ Done. Scored {len(scores)} occupations → scores.json")

    # Print summary statistics
    valid = [s["exposure"] for s in scores.values() if s["exposure"] >= 0]
    print(f"Average AI Exposure: {sum(valid)/len(valid):.2f}/10")
    high_exp = [(s["title"], s["exposure"]) for s in scores.values() if s["exposure"] >= 7]
    low_exp = [(s["title"], s["exposure"]) for s in scores.values() if s["exposure"] <= 2]
    print(f"\nHigh Exposure (7+): {len(high_exp)} occupations")
    for t, e in sorted(high_exp, key=lambda x: -x[1])[:5]:
        print(f"  {e}/10 — {t}")
    print(f"\nLow Exposure (≤2): {len(low_exp)} occupations")
    for t, e in sorted(low_exp, key=lambda x: x[1])[:5]:
        print(f"  {e}/10 — {t}")

if __name__ == "__main__":
    main()
