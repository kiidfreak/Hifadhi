# Hifadhi Multi-Agent Workflow Diagram


```mermaid
graph TD
    Start([User Query]) --> Supervisor[Supervisor Agent]
    
    Supervisor -->|Route based on intent| Screening[Candidate Screening Agent]
    Supervisor --> Onboarding[Onboarding Agent]
    Supervisor --> Compliance[Compliance Agent]
    Supervisor --> Payroll[Payroll Agent]
    Supervisor --> Analytics[Analytics Agent]
    Supervisor --> GeneralHelp[General Help Agent]
    Supervisor -->|Complex case| Escalation[Human Escalation Agent]
    Supervisor -->|Task complete| FinalAnswer[Final Answer Agent]
    
    Screening --> Supervisor
    Onboarding --> Supervisor
    Compliance --> Supervisor
    Payroll --> Supervisor
    Analytics --> Supervisor
    GeneralHelp --> Supervisor
    
    FinalAnswer --> End([Conversation End])
    Escalation --> End
    
    Supervisor -->|Needs clarification| Supervisor
    
    style Supervisor fill:#667eea,stroke:#764ba2,stroke-width:3px,color:#fff
    style Screening fill:#10B981,stroke:#059669,stroke-width:2px,color:#fff
    style Onboarding fill:#3B82F6,stroke:#2563EB,stroke-width:2px,color:#fff
    style Compliance fill:#8B5CF6,stroke:#7C3AED,stroke-width:2px,color:#fff
    style Payroll fill:#F59E0B,stroke:#D97706,stroke-width:2px,color:#fff
    style Analytics fill:#EC4899,stroke:#DB2777,stroke-width:2px,color:#fff
    style GeneralHelp fill:#6366F1,stroke:#4F46E5,stroke-width:2px,color:#fff
    style Escalation fill:#EF4444,stroke:#DC2626,stroke-width:2px,color:#fff
    style FinalAnswer fill:#14B8A6,stroke:#0D9488,stroke-width:2px,color:#fff
    style Start fill:#1F2937,stroke:#111827,stroke-width:2px,color:#fff
    style End fill:#1F2937,stroke:#111827,stroke-width:2px,color:#fff
```


## Workflow Description

This diagram represents the complete conversation flow in the Hifadhi multi-agent system.

### Flow Explanation:

1. **User Query** enters the system through the Supervisor Agent
2. **Supervisor Agent** analyzes intent and routes to appropriate specialist
3. **Specialist Agents** execute their tasks and return to Supervisor
4. **Supervisor** continues routing until task is complete
5. **Final Answer Agent** polishes the response before ending
6. **Human Escalation** occurs for complex cases

### Agent Responsibilities:

- **Candidate Screening Agent**: Application status, profiles, interviews
- **Onboarding Agent**: Task tracking, document collection
- **Compliance Agent**: KRA/NSSF/NHIF verification
- **Payroll Agent**: M-Pesa payments, salary processing
- **Analytics Agent**: Hiring metrics and insights
- **General Help Agent**: FAQ responses using RAG
