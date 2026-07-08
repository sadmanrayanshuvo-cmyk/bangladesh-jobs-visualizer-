# Bangladesh Job Market Visualizer

End-to-end adaptation of Andrej Karpathy’s `karpathy/jobs` for Bangladesh.

- Uses BBS Labour Force Survey 2023, BGMEA, BMET and national pay scales.
- Maps ~66M workers into 46 occupations across agriculture, RMG, IT, banking,
  healthcare, migrant labour and services.
- LLM (Gemini via OpenRouter) scores each occupation 0–10 on **Digital AI Exposure**
  using Bangladesh-specific prompts.
- D3.js treemap (`index.html` + `data.json`) where:
  - Area = total employment for each occupation.
  - Color toggles between monthly wage (BDT), education tier, and AI exposure.

## How to run

1. Clone the repo:
   ```bash
   git clone https://github.com/sadmanrayanshuvo-cmyk/bangladesh-jobs-visualizer-.git
