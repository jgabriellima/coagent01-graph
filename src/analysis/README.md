# Workflow Analysis Utility

**Technical blueprint generator for multi-agent workflows.**

## Overview

The Workflow Analysis utility extracts real agent configurations from `create_react_agent` workflows and generates structured technical blueprints using GPT-4o. Perfect for documentation, system analysis, and development insights.

## Key Features

- **Real Agent Extraction**: Extracts actual tools, prompts, and configurations from React agents
- **LLM-Powered Analysis**: Uses GPT-4o with structured output for intelligent role inference
- **Technical Blueprint**: Generates concise, structured documentation
- **Handoff Detection**: Automatically identifies agent handoff relationships
- **Tool Classification**: Distinguishes between regular tools and handoff tools

## Quick Start

```python
from sample_agent.analysis import analyze_workflow
from sample_agent.agents.swarm.graph import create_multi_agent_system_swarm_mode

# Create workflow
workflow = create_multi_agent_system_swarm_mode()

# Generate blueprint
blueprint = analyze_workflow(workflow)

# Access structured data
print(f"Workflow type: {blueprint.workflow_type}")
print(f"Agents: {blueprint.agent_count}")

for agent_name, agent_bp in blueprint.agents.items():
    print(f"{agent_name}: {agent_bp.role}")
    print(f"  Tools: {len(agent_bp.tools)}")
    print(f"  Handoffs: {agent_bp.handoffs}")
```

## Blueprint Structure

### WorkflowBlueprint
- `workflow_type`: Type of workflow system
- `description`: Workflow description
- `agents`: Dictionary of agent blueprints
- `agent_count`: Number of agents
- `total_tools`: Total number of tools

### AgentBlueprint
- `role`: Agent role/function
- `role_description`: Detailed role description
- `tools`: List of available tools
- `handoffs`: List of agent names for handoffs

### ToolInfo
- `name`: Tool name
- `description`: Tool description
- `is_handoff`: Whether tool is for agent handoff

## Configuration

```python
from sample_agent.analysis import WorkflowAnalysisConfig

config = WorkflowAnalysisConfig(
    save_to_file=True,
    output_file=Path("workflow_blueprint.json")
)
```

## Example Output

```
🔧 WORKFLOW BLUEPRINT
================================================================================

📊 OVERVIEW:
   • Type: Multi-agent coordination system
   • Description: Specialized workflow with role-based agent coordination
   • Agents: 3
   • Total tools: 8

🤖 AGENTS:

   Main_Agent:
      • Role: Workflow Coordinator
      • Description: Primary coordination agent for task routing and management
      • Tools (3):
        🔧 ask_user: Human interaction tool for clarifications
        🔄 alice_handoff_tool: Handoff to Alice for mathematical tasks
        🔄 bob_handoff_tool: Handoff to Bob for weather queries
      • Handoffs: Alice, Bob

   Alice:
      • Role: Mathematics Specialist
      • Description: Specialized agent for mathematical calculations and analysis
      • Tools (2):
        🔧 calculate_math: Mathematical computation tool
        🔄 main_agent_handoff_tool: Return to main coordination
      • Handoffs: Main_Agent

   Bob:
      • Role: Weather Information Provider
      • Description: Specialized agent for weather data and forecasting
      • Tools (3):
        🔧 get_weather: Weather data retrieval tool
        🔧 ask_user: Human interaction for location clarification
        🔄 main_agent_handoff_tool: Return to main coordination
      • Handoffs: Main_Agent
```

## Requirements

- **GPT-4o**: Required for blueprint generation (no fallbacks)
- **Python 3.8+**
- **LangGraph**: For workflow analysis
- **Pydantic**: For structured output models

## Error Handling

The analyzer requires GPT-4o and will raise `RuntimeError` if unavailable:

```python
try:
    analyzer = WorkflowAnalyzer()
    blueprint = analyzer.analyze_workflow(workflow)
except RuntimeError as e:
    print(f"GPT-4o required: {e}")
```

## Integration

### Synthetic Data Generation

```python
# Generate blueprint
blueprint = analyze_workflow(workflow)

# Use in synthetic data generation
synthesizer_config = {
    "project": f"blueprint-{blueprint.workflow_type.lower().replace(' ', '-')}",
    "agents": blueprint.agent_count,
    "tools": blueprint.total_tools
}
```

### Documentation Generation

```python
# Generate and save blueprint
config = WorkflowAnalysisConfig(
    save_to_file=True,
    output_file=Path("system_documentation.json")
)

blueprint = analyze_workflow(workflow, config)
```

## Architecture

The analyzer works in three phases:

1. **Agent Extraction**: Extracts real agent data from workflow nodes
2. **LLM Analysis**: Uses GPT-4o to analyze agent roles and capabilities
3. **Blueprint Generation**: Creates structured technical documentation

All analysis is performed via LLM with structured output - no static pattern matching or fallbacks.

## Best Practices

1. **GPT-4o Availability**: Ensure GPT-4o is configured before using
2. **Structured Output**: Leverage Pydantic models for type safety
3. **Error Handling**: Handle GPT-4o failures gracefully
4. **Documentation**: Use blueprints for system documentation
5. **Integration**: Integrate with existing development workflows 