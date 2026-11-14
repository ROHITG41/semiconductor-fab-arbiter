flowchart TD
    classDef client fill:#EFF6FF,stroke:#2563EB,stroke-width:2px,color:#1E3A8A;
    classDef deterministic fill:#ECFDF5,stroke:#059669,stroke-width:2px,color:#064E3B;
    classDef logic fill:#FAF5FF,stroke:#7C3AED,stroke-width:2px,color:#4C1D95;
    classDef output fill:#F8FAFC,stroke:#475569,stroke-width:2px,color:#0F172A;

    subgraph INGRESS ["1. SPECIFICATION & ECN INGRESS"]
        UI["Streamlit Cloud Command Center<br/><b>Tool Bay Telemetry, Baseline DBR & Raw OEM ECN Text</b>"]:::client
    end

    subgraph CPU_GATE ["2. DETERMINISTIC MCP CALCULATION SERVER"]
        direction TB
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
