# Autonomous Semiconductor Change Intelligence & Hook-Up Arbiter

[![Open in Streamlit](https://streamlit.io)](https://streamlit.app)
![Python 3.12](https://shields.io)
![Audit Standard](https://shields.io)
![Cognitive LLM](https://shields.io)
![Architecture](https://shields.io)

> **Dataset & Confidentiality Note:** This application is an independent engineering architecture demonstration validated on representative, anonymized project datasets.

---

### Executive Problem Statement
On &#36;3B–&#36;28B semiconductor fab projects, Phase 3/4 cleanroom fit-out, tool move-in, and testing & commissioning (T&C) face an acute operational bottleneck. Continuous revisions to OEM process tool manuals collide with fixed base-build sub-fab headers and overlapping contractor schedules. Every single day of delay to 'First Wafer' output costs semiconductor owners between &#36;1M and &#36;5M+ in deferred revenue, while manual tracking across spreadsheets fails to catch coupled hydraulic and exhaust shortfalls.

### Operational Value
- **Prevents Cleanroom Tear-Out & Schedule Slip:** Immediately recalculates coupled sub-fab fluid and exhaust physics when an OEM issues a late specification change—flagging lateral pipe or duct upsizing directives before cleanroom welding begins.
- **Protects CapEx Against Inflated Claims:** Runs deterministic schedule concurrency math under SCL Delay Protocols and FIDIC Sub-Clause 8.4 rules to isolate liability across Base-Build MEP, Tool-Install Contractors, and Tool OEMs, certifying only strictly justified Extension of Time (EoT) days.
- **Shields Wafer Yield & Life Safety:** Enforces SEMI S2, SEMI F47, ISO 14644-1, and VC-E/VC-G micro-vibration limits prior to Gas-Turn-On (GTO) clearance.

---

### System Architecture

```mermaid
flowchart TD
    classDef client fill:#EFF6FF,stroke:#2563EB,stroke-width:2px,color:#1E3A8A;
    classDef deterministic fill:#ECFDF5,stroke:#059669,stroke-width:2px,color:#064E3B;
    classDef logic fill:#FAF5FF,stroke:#7C3AED,stroke-width:2px,color:#4C1D95;
    classDef output fill:#F8FAFC,stroke:#475569,stroke-width:2px,color:#0F172A;

    subgraph INGRESS ["1. SPECIFICATION & ECN INGRESS"]
        UI["Streamlit Cloud Command Center<br/><b>Tool Bay Telemetry, Baseline DBR & Raw OEM ECN Text</b>"]:::client
    end

    subgraph CPU_GATE ["2. DETERMINISTIC MCP CALCULATION SERVER"]
        GRAPH["<b>Multiphysics Computation (CPU)</b><br/>Audits Darcy-Weisbach PCW Friction, SEMI S6 Exhaust & VC-E Vibration"]:::deterministic
        METRICS["<b>Hook-Up Readiness Index (HRI 0-100)</b><br/>Computes Coupled Header Headroom & Safety Gates"]:::deterministic
        CONTRACT["<b>Pydantic v2 Structured Payload</b><br/>Immutable Point-of-Use (POU) Data Contracts"]:::deterministic
        GRAPH --> METRICS --> CONTRACT
    end

    subgraph COGNITIVE ["3. COGNITIVE MULTI-AGENT ARBITRATION"]
        LLM["<b>LangChain + Google Gemini (gemini-3.8-flash)</b><br/>Multi-Agent Debate: Yield Sentinel, CapEx Auditor & T&C Arbiter<br/>Enforces FIDIC Contract Governance & SCL Protocols"]:::logic
    end

    subgraph DELIVERABLE ["4. AUDIT-GRADE DOSSIER OUTPUT"]
        MEMO["<b>Pre-Hookup Readiness & NCR PDF Dossier</b><br/>Signed Engineering Determination & Trade Remediation Directives"]:::output
    end

    UI --> GRAPH
    CONTRACT -->|Verified Telemetry & Attribution| LLM
    LLM --> MEMO
```

---

### Technology Stack
- **Runtime & UI:** Python 3.12, Streamlit Community Cloud
- **Orchestration & LLM:** LangChain, Google Gemini (`gemini-3.8-flash`)
- **Deterministic Analytics:** Pandas, Pydantic v2, ReportLab PDF Engine

---

### Author & Architect
**Rohit Kumar, PMP, CEng (India), CEA, FSEr (TÜV)**  
*Mission-Critical Infrastructure & Systems Engineering Specialist | Forensic Project Controls & Contract Governance*  

[LinkedIn](https://www.linkedin.com/in/rohitg41/) | [Live Application](https://streamlit.app)

---

### Enterprise Advisory & Custom Architecture
Available for technical consulting, custom agentic workflow development, and private enterprise deployments.

- **Connect:** [LinkedIn](https://www.linkedin.com/in/rohitg41/)
- **Email:** grohit41@gmail.com

---

### Intellectual Property & Licensing
Copyright © 2026 Rohit Kumar. All Rights Reserved.

This repository and its source code are published solely for technical portfolio evaluation and architectural demonstration. Unauthorized copying, redistribution, or commercial deployment is prohibited without prior written consent.
