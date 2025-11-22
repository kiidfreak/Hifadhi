# Hifadhi Multi-Agent Workflow Documentation

## Overview

The Hifadhi multi-agent system uses LangGraph to orchestrate conversation flow between specialized AI agents. Each agent focuses on a specific HR domain, and the Supervisor Agent intelligently routes queries to the appropriate specialist.

## Architecture Components

### 1. State Management

The workflow maintains a comprehensive `HifadhiState` that tracks:

- **Conversation History**: Full dialogue context
- **User Context**: IDs (candidate, job, application)
- **Routing Decisions**: Next agent, task assignments
- **Agent Outputs**: Messages and results
- **Clarification Flow**: Questions and responses
- **Escalation Flags**: Human intervention triggers

### 2. Agent Nodes

#### Supervisor Agent (Central Orchestrator)
- **Role**: Analyzes user intent and routes to specialists
- **Capabilities**: 
  - Intent detection
  - Context extraction
  - Clarification management
  - Iteration limiting
- **Tools**: `ask_user`

#### Candidate Screening Agent
- **Role**: Handles application tracking and candidate profiles
- **Capabilities**:
  - Application status lookup
  - Candidate profile retrieval
  - Interview scheduling
  - AI screening score interpretation
- **Tools**: `get_candidate_details`, `get_application_status`, `get_interview_schedule`

#### Onboarding Agent
- **Role**: Manages new hire onboarding process
- **Capabilities**:
  - Onboarding task tracking
  - Document collection
  - Timeline management
  - Training coordination
- **Tools**: `get_onboarding_tasks`, `get_candidate_details`

#### Compliance Agent
- **Role**: Ensures regulatory compliance
- **Capabilities**:
  - KRA PIN verification
  - NSSF/NHIF enrollment
  - Labor law compliance
  - Document expiry tracking
- **Tools**: `get_compliance_status`, `get_candidate_details`

#### Payroll Agent
- **Role**: Processes payments and manages payroll
- **Capabilities**:
  - M-Pesa payment processing (via PayLink)
  - Payment history tracking
  - Transaction status checking
  - Salary calculations
- **Tools**: `process_mpesa_payment`, `get_payroll_history`, `check_payment_status`

#### Analytics Agent
- **Role**: Provides hiring metrics and insights
- **Capabilities**:
  - Time-to-hire calculation
  - Pipeline analytics
  - Conversion rate tracking
  - Performance metrics
- **Tools**: `get_hiring_metrics`, `get_pipeline_analytics`

#### General Help Agent
- **Role**: Answers FAQs using RAG
- **Capabilities**:
  - Vector search over FAQ knowledge base
  - Context-aware responses
  - General HR guidance
- **Tools**: ChromaDB vector search

#### Human Escalation Agent
- **Role**: Gracefully hands off to human HR team
- **Capabilities**:
  - Escalation acknowledgment
  - Context preservation
  - Human handoff coordination

#### Final Answer Agent
- **Role**: Polishes responses before ending
- **Capabilities**:
  - Response summarization
  - Professional formatting
  - Closing statement generation

### 3. Routing Logic

The workflow uses conditional edges to determine routing:

```python
def decide_next_agent(state):
    # Priority 1: Clarification loop
    if state.get("needs_clarification"):
        return "supervisor_agent"
    
    # Priority 2: End conversation
    if state.get("end_conversation"):
        return "end"
    
    # Priority 3: Human escalation
    if state.get("requires_human_escalation"):
        return "human_escalation_agent"
    
    # Priority 4: Route to specialist
    return state.get("next_agent", "general_help_agent")
```

### 4. Conversation Flow

```
User Query
    ↓
Supervisor Agent (Iteration 1)
    ↓
[Clarification needed?]
    ↓ No
Specialist Agent (e.g., Payroll)
    ↓
Supervisor Agent (Iteration 2)
    ↓
[Task complete?]
    ↓ Yes
Final Answer Agent
    ↓
END
```

### 5. Edge Types

#### Conditional Edges
- **From Supervisor**: Routes to any specialist based on intent
- **Clarification Loop**: Returns to supervisor when clarification provided

#### Static Edges
- **Specialist → Supervisor**: All specialists return to supervisor
- **Final Answer → END**: Terminal edge
- **Human Escalation → END**: Terminal edge

### 6. Safety Mechanisms

#### Iteration Limiting
- Maximum 5 supervisor iterations
- Auto-escalates to human if limit reached

#### State Validation
- Checks for required information before routing
- Extracts IDs from conversation history
- Validates agent names

#### Error Handling
- Fallback routing for invalid decisions
- Exception catching in all agents
- Graceful degradation to general help

## Example Conversation Flows

### Example 1: Payment Processing

```
User: "Process salary payment for candidate CAND00001"
    ↓
Supervisor: Routes to payroll_agent
    ↓
Payroll Agent: Requests M-Pesa details
    ↓
Supervisor: Uses ask_user tool
    ↓
User: Provides phone number
    ↓
Supervisor: Routes back to payroll_agent
    ↓
Payroll Agent: Processes payment via PayLink
    ↓
Supervisor: Task complete → Final Answer
    ↓
Final Answer: "Payment of KES 50,000 sent successfully"
    ↓
END
```

### Example 2: Complex Multi-Agent Query

```
User: "What's the status of my onboarding and when will I get paid?"
    ↓
Supervisor: Asks for candidate ID
    ↓
User: "CAND00123"
    ↓
Supervisor: Routes to onboarding_agent
    ↓
Onboarding Agent: Returns task status
    ↓
Supervisor: Routes to payroll_agent
    ↓
Payroll Agent: Returns payment schedule
    ↓
Supervisor: Both questions answered → Final Answer
    ↓
Final Answer: Combines both responses
    ↓
END
```

### Example 3: Escalation

```
User: "I need to discuss a complex contract issue"
    ↓
Supervisor: Iteration 1 - asks clarifying questions
    ↓
User: Provides details
    ↓
Supervisor: Iteration 2 - routes to compliance_agent
    ↓
Compliance Agent: Cannot resolve
    ↓
Supervisor: Iteration 3 - complexity detected
    ↓
Supervisor: Routes to human_escalation_agent
    ↓
Human Escalation: "HR specialist will contact you"
    ↓
END
```

## Performance Considerations

### Optimization Strategies

1. **State Minimization**: Only include necessary data in state
2. **Tool Call Efficiency**: Batch database queries when possible
3. **Prompt Optimization**: Keep prompts concise but specific
4. **Caching**: Cache frequently accessed data (FAQs, job postings)

### Monitoring Metrics

- Average conversation length (iterations)
- Agent utilization rates
- Escalation frequency
- Response times per agent
- Tool call success rates

## Deployment Considerations

### Scaling

- **Horizontal**: Multiple instances with shared database
- **Vertical**: Increase LLM token limits
- **Agent-level**: Deploy resource-intensive agents separately

### Fault Tolerance

- Retry logic for tool calls
- Fallback responses for LLM failures
- State persistence for crash recovery
- Circuit breakers for external APIs

## Testing Strategy

### Unit Tests
- Individual agent logic
- Tool function accuracy
- State update correctness

### Integration Tests
- Multi-agent workflows
- Edge case routing
- Error propagation

### End-to-End Tests
- Complete conversation flows
- Performance benchmarks
- Load testing

## Future Enhancements

1. **Agent Memory**: Persistent memory across sessions
2. **Parallel Agent Execution**: Multiple agents working simultaneously
3. **Dynamic Agent Registration**: Hot-swap agents without restart
4. **Advanced Analytics**: ML-based intent prediction
5. **Multi-Language Support**: Localization framework

---

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
