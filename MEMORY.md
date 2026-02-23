# MEMORY — MedForm3D (summary)

Added: 2026-02-18

- Owner: Diego Jenzer (Basel, Europe/Zurich)
- Business: MedForm3D — Swiss 3D-printing service focused on medical/healthcare models (surgical planning, training models, patient-specific anatomy), plus FDM and hydrogel workflows.
- Key equipment: Anycubic M5s, M7, M7 Max, P1; Canon EOS R100; Wacom Intuos Pen S. Considering a small/medium 3D scanner.
- Materials: Anycubic Tough Ultra, ABS-like Pro2; Siraya Tenacious & Craft Clear; Resione Anti-impact & G217; 3Dresyns SSA1 (water-reactive hydrogel).
- Core priorities: develop SOPs for intake → print → post-process → QA → delivery; build content strategy (hard resin, FDM, hydrogel); material qualification and compliance posture for medical positioning.
- Tags: MEDICAL_MODELS, MATERIALS_RESIN, HYDROGEL_PRINTS, POST_PROCESS, CONTENT_MARKETING, EQUIPMENT, OPS_SYSTEMS

## Mission Control (autonomy + infra)
- Notion is canonical for Projects/Contacts/Ideas; Todoist is day‑to‑day tasks. Gmail+Calendar read allowed; email sending only with explicit request. Daily summary only on request (Telegram).
- **Agent setup (current): single assistant agent** (no separate ops/content agents). We use manual in-chat modes + /new for clean contexts; model switching is done manually per task.
- GitHub repo created: https://github.com/diegoje/Mission_Control (public). Secrets excluded via .gitignore.
- Git configured with SSH key stored in workspace .ssh; gh auth login completed.
- QMD installed and enabled as memory backend (memory.backend = "qmd"); gateway restarted successfully.

## Business Analysis & Strategic Positioning (Updated: 2026-02-23)
- **Merged Business Analysis created:** Combines market opportunity analysis with regulatory reality check
- **Overall assessment:** 6.5/10 — strong technical foundation, critical gaps in regulatory infrastructure
- **Strategic choice required:** Pick ONE focus for 2024 — CDMO for MedTech OR Surgical Planning Models (not both initially)
- **Key constraint:** Hydrogel implants = Class III devices; cannot sell commercially until CE pathway mapped
- **Immediate priority:** ISO 13485 QMS implementation (CHF 50k), Swissmedic registration
- **90-day sprint:** Medical Director recruitment, pilot customer acquisition, LinkedIn regulatory-focused campaign
- **Location:** https://www.notion.so/Business-Analysis-Merged-Final-3105d4551f56817280fee17a4e0a5e28

## Automated Systems (Active)
- **Daily news digest:** Cron job `morning-news` — 07:00 Europe/Berlin (global events, 3D printing, Brazil, Switzerland)
- **Weekly business review:** Cron job `business-plan-review` — Fridays 09:00 (analyzes learnings, suggests updates, creates Todoist review task)

## Competitor Intelligence
**Materialise (Feb 2025):** Launched PEEK CMF implants complementing titanium portfolio. 
- *Implication:* Hydrogel differentiation more critical; CMF surgical planning (not implants) remains underserved opportunity.

## Automated Systems (Active)
- **Daily news digest:** Cron job `morning-news` — 07:00 Europe/Berlin (global events, 3D printing, Brazil, Switzerland)
- **Weekly business review:** Cron job `business-plan-review` — Fridays 09:00 (analyzes learnings, suggests updates, creates Todoist review task)

## Receipt Processing Skill (NEW)
**Trigger phrases:** "process receipts", "process all receipts", or direct image upload
**Workflow:**
1. Extract data from receipt image (date, vendor, amount, currency, VAT, description, category)
2. Add to Business Expenses sheet (Google Sheets) with pipe-separated format
3. Move to processed folder based on year (2025 or 2026)
4. Send report to Telegram group -1003829111345
**Important:** Images only (JPG/PNG). No PDFs. No commas in descriptions (use dashes).
**Skill file:** `/data/.openclaw/workspace/skills/receipt-processing/SKILL.md`

## Working Protocols
**Information capture (new):** All URLs, videos, documents, receipts shared by Diego → fetch/analyze → summarize → save to memory (daily logs + curated MEMORY.md)

Source: memory/2026-02-18_mission_control_design.md + memory/2026-02-23.md
