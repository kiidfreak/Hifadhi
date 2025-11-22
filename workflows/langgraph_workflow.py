"""
Main LangGraph workflow for Hifadhi multi-agent system
Defines the complete conversation graph with all agents and routing logic
"""

import logging
from langgraph.graph import StateGraph, END
from utils.state_management import HifadhiState
from workflows.routing_logic import decide_next_agent, should_continue_conversation

# Import all agents
from agents.supervisor_agent import supervisor_agent
from agents.candidate_screening_agent import candidate_screening_agent
from agents.onboarding_agent import onboarding_agent
from agents.compliance_agent import compliance_agent
from agents.payroll_agent import payroll_agent
from agents.analytics_agent import analytics_agent
from agents.general_help_agent import general_help_agent
from agents.human_escalation_agent import human_escalation_agent
from agents.final_answer_agent import final_answer_agent

logger = logging.getLogger(__name__)


# ============================================
# BUILD THE WORKFLOW GRAPH
# ============================================

def create_hifadhi_workflow():
    """
    Create the complete Hifadhi multi-agent workflow graph
    
    Returns:
        Compiled LangGraph workflow
    """
    
    # Initialize the graph with HifadhiState
    workflow = StateGraph(HifadhiState)
    
    logger.info("🏗️ Building Hifadhi workflow graph...")
    
    # ============================================
    # ADD ALL AGENT NODES
    # ============================================
    
    workflow.add_node("supervisor_agent", supervisor_agent)
    workflow.add_node("candidate_screening_agent", candidate_screening_agent)
    workflow.add_node("onboarding_agent", onboarding_agent)
    workflow.add_node("compliance_agent", compliance_agent)
    workflow.add_node("payroll_agent", payroll_agent)
    workflow.add_node("analytics_agent", analytics_agent)
    workflow.add_node("general_help_agent", general_help_agent)
    workflow.add_node("human_escalation_agent", human_escalation_agent)
    workflow.add_node("final_answer_agent", final_answer_agent)
    
    logger.info("✅ Added 9 agent nodes to graph")
    
    # ============================================
    # SET ENTRY POINT
    # ============================================
    
    workflow.set_entry_point("supervisor_agent")
    logger.info("✅ Entry point set to supervisor_agent")
    
    # ============================================
    # ADD CONDITIONAL EDGES FROM SUPERVISOR
    # ============================================
    
    # The supervisor can route to any specialist agent, or trigger end/escalation
    workflow.add_conditional_edges(
        "supervisor_agent",
        decide_next_agent,
        {
            "supervisor_agent": "supervisor_agent",  # Loop back for clarifications
            "candidate_screening_agent": "candidate_screening_agent",
            "onboarding_agent": "onboarding_agent",
            "compliance_agent": "compliance_agent",
            "payroll_agent": "payroll_agent",
            "analytics_agent": "analytics_agent",
            "general_help_agent": "general_help_agent",
            "human_escalation_agent": "human_escalation_agent",
            "end": "final_answer_agent"  # Route to final answer before END
        }
    )
    
    logger.info("✅ Added conditional edges from supervisor")
    
    # ============================================
    # ADD EDGES FROM SPECIALIST AGENTS BACK TO SUPERVISOR
    # ============================================
    
    # After each specialist completes, return to supervisor for next decision
    specialist_agents = [
        "candidate_screening_agent",
        "onboarding_agent",
        "compliance_agent",
        "payroll_agent",
        "analytics_agent",
        "general_help_agent"
    ]
    
    for agent in specialist_agents:
        workflow.add_edge(agent, "supervisor_agent")
    
    logger.info(f"✅ Added return edges from {len(specialist_agents)} specialists to supervisor")
    
    # ============================================
    # ADD TERMINAL EDGES
    # ============================================
    
    # Final answer agent → END
    workflow.add_edge("final_answer_agent", END)
    
    # Human escalation agent → END (conversation terminates)
    workflow.add_edge("human_escalation_agent", END)
    
    logger.info("✅ Added terminal edges to END")
    
    # ============================================
    # COMPILE THE WORKFLOW
    # ============================================
    
    compiled_app = workflow.compile()
    
    logger.info("🎉 Hifadhi workflow compiled successfully!")
    
    return compiled_app


# ============================================
# CREATE THE APP INSTANCE
# ============================================

app = create_hifadhi_workflow()


# ============================================
# HELPER FUNCTIONS
# ============================================

def visualize_graph(save_path: str = "docs/hifadhi_workflow.png"):
    """
    Generate visual representation of the workflow graph
    
    Args:
        save_path: Path to save the PNG image
    """
    try:
        from IPython.display import Image, display
        
        graph_image = app.get_graph().draw_mermaid_png()
        
        # Save to file
        with open(save_path, "wb") as f:
            f.write(graph_image)
        
        print(f"✅ Workflow graph saved to {save_path}")
        
        # Display if in notebook
        try:
            display(Image(graph_image))
        except:
            pass
        
        return graph_image
    
    except Exception as e:
        logger.error(f"Failed to visualize graph: {e}")
        print(f"❌ Graph visualization failed: {e}")
        return None


def get_workflow_statistics():
    """
    Get statistics about the workflow graph
    
    Returns:
        Dictionary with graph statistics
    """
    graph = app.get_graph()
    
    stats = {
        "total_nodes": len(graph.nodes),
        "node_names": list(graph.nodes.keys()),
        "entry_point": "supervisor_agent",
        "terminal_nodes": ["final_answer_agent", "human_escalation_agent"],
        "specialist_agents": [
            "candidate_screening_agent",
            "onboarding_agent",
            "compliance_agent",
            "payroll_agent",
            "analytics_agent",
            "general_help_agent"
        ],
        "max_iterations": 5
    }
    
    return stats


def print_workflow_info():
    """Print human-readable workflow information"""
    stats = get_workflow_statistics()
    
    print("\n" + "="*70)
    print("HIFADHI MULTI-AGENT WORKFLOW")
    print("="*70)
    print(f"\n📊 Total Nodes: {stats['total_nodes']}")
    print(f"🚀 Entry Point: {stats['entry_point']}")
    print(f"🏁 Terminal Nodes: {', '.join(stats['terminal_nodes'])}")
    print(f"🔄 Max Supervisor Iterations: {stats['max_iterations']}")
    
    print(f"\n🤖 Specialist Agents ({len(stats['specialist_agents'])}):")
    for i, agent in enumerate(stats['specialist_agents'], 1):
        print(f"  {i}. {agent}")
    
    print("\n📋 Workflow Flow:")
    print("  User Query → Supervisor → Specialist Agent → Supervisor → ... → Final Answer → END")
    print("="*70 + "\n")


# ============================================
# TESTING UTILITIES
# ============================================

def test_workflow_routing(test_queries: list):
    """
    Test workflow with multiple queries
    
    Args:
        test_queries: List of test queries to run
    """
    from utils.state_management import create_initial_state
    
    print("\n" + "="*70)
    print("WORKFLOW ROUTING TEST")
    print("="*70 + "\n")
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}/{len(test_queries)}] Query: {query}")
        print("-" * 70)
        
        try:
            initial_state = create_initial_state(query)
            final_state = app.invoke(initial_state)
            
            result = {
                "query": query,
                "agents_invoked": _extract_agents_from_history(
                    final_state.get("conversation_history", "")
                ),
                "iterations": final_state.get("n_iteration", 0),
                "final_answer": final_state.get("final_answer", "No answer")[:100] + "...",
                "escalated": final_state.get("requires_human_escalation", False),
                "success": True
            }
            
            print(f"✅ Completed in {result['iterations']} iterations")
            print(f"📍 Agents used: {', '.join(result['agents_invoked'])}")
            
        except Exception as e:
            result = {
                "query": query,
                "success": False,
                "error": str(e)
            }
            print(f"❌ Error: {e}")
        
        results.append(result)
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r.get("success"))
    print(f"Successful: {successful}/{len(results)}")
    
    return results


def _extract_agents_from_history(history: str) -> list:
    """Extract list of agents invoked from conversation history"""
    agents = []
    for line in history.split("\n"):
        if "Agent:" in line:
            agent_name = line.split("Agent:")[0].strip().replace(" ", "_").lower() + "_agent"
            if agent_name not in agents:
                agents.append(agent_name)
    return agents


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    # Print workflow info
    print_workflow_info()
    
    # Visualize graph
    visualize_graph()
    
    # Run test queries
    test_queries = [
        "What is the status of application APP00001?",
        "Process payment of KES 50000 to candidate CAND00001 via M-Pesa",
        "What documents are needed for onboarding?",
        "Show me hiring metrics for last 30 days",
        "I want to speak to a human"
    ]
    
    test_workflow_routing(test_queries)
