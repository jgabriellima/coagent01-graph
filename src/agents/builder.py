from datetime import datetime
from jinja2 import Template
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableLambda


class AgentBuilder:
    def __init__(
        self,
        *,
        name: str,
        model,
        tools: list,
        agent_identity: str,
        responsibilities: list[str],
        state_schema=None,
        response_format=None,
        prompt_template_path: str,
        dynamic_block_template_path: str | None = None,
        constraints: list[str] | None = None,
        prompt_template: str | None = None,
        additional_pre_hooks: list[RunnableLambda] | None = None,
    ):
        self.name = name
        self.model = model
        self.tools = tools
        self.agent_identity = agent_identity
        self.responsibilities = responsibilities
        self.state_schema = state_schema
        self.response_format = response_format
        self.prompt_template_path = prompt_template_path
        self.dynamic_block_template_path = dynamic_block_template_path
        self.constraints = constraints
        self.prompt_template = prompt_template
        self.additional_pre_hooks = additional_pre_hooks or []

    def _extract_tool_infos(self) -> list[dict]:
        """Extract tool metadata into a uniform list for template rendering."""
        tool_infos = []
        for tool in self.tools:
            if hasattr(tool, "name") and hasattr(tool, "description"):
                name = getattr(tool, "name")
                description = getattr(tool, "description", "").strip()
            else:
                name = getattr(tool, "__name__", str(tool))
                description = getattr(tool, "__doc__", "").strip()
            tool_infos.append({"name": name, "description": description})
        return tool_infos

    def _render_prompt(self, state: dict) -> str:
        """Renders the full prompt using Jinja2 and the provided state."""
        if self.prompt_template:
            return self.prompt_template

        with open(self.prompt_template_path, "r") as f:
            self.prompt_template = Template(f.read())

        dynamic_block = ""
        if self.dynamic_block_template_path:
            with open(self.dynamic_block_template_path, "r") as f:
                dynamic_template = Template(f.read())
                dynamic_block = dynamic_template.render(**state)

        self.prompt_template = self.prompt_template.render(
            current_datetime=datetime.utcnow().isoformat(),
            agent_identity=self.agent_identity,
            responsibilities=self.responsibilities,
            constraints=self.constraints,
            tools=self._extract_tool_infos(),
            dynamic_block=dynamic_block,
        )

        print(f"prompt_template: {self.prompt_template}")
        return self.prompt_template

    def _compose_pre_hooks(self) -> RunnableLambda:
        """Composes multiple pre-hooks into a single RunnableLambda chain."""
        
        def composed_hook_fn(state: dict) -> dict:
            # Start with the original state
            current_state = state.copy()
            
            # Apply additional pre-hooks first (e.g., classify_query_hook)
            for hook in self.additional_pre_hooks:
                hook_result = hook.invoke(current_state)
                if isinstance(hook_result, dict):
                    current_state.update(hook_result)
                else:
                    # If hook returns a state object, convert to dict
                    current_state = hook_result if hasattr(hook_result, '__dict__') else current_state
            
            # Apply the prompt rendering hook last
            rendered_prompt = self._render_prompt(current_state)
            print(f"Calling composed pre_model_hook for agent: {self.name}")
            
            # Return the updated state with the llm_input_messages
            result = current_state.copy()
            result["llm_input_messages"] = [SystemMessage(content=rendered_prompt)] + current_state.get("messages", [])
            
            return result
        
        return RunnableLambda(composed_hook_fn)

    def _pre_model_hook(self) -> RunnableLambda:
        """Injects dynamically generated prompt as llm_input_messages."""

        def hook_fn(state: dict) -> dict:
            rendered_prompt = self._render_prompt(state)
            print("Calling pre_model_hook")
            return {
                "llm_input_messages": [SystemMessage(content=rendered_prompt)]
                + state.get("messages", [])
            }

        return RunnableLambda(hook_fn)

    def build(self) -> CompiledStateGraph:
        """Creates a fully configured ReAct agent with dynamic prompt injection via pre_model_hook."""
        bound_model = self.model.bind_tools(
            self.tools,
            parallel_tool_calls=False,
        )

        # Use composed hooks if additional hooks are provided, otherwise use the default
        pre_hook = self._compose_pre_hooks() if self.additional_pre_hooks else self._pre_model_hook()

        return create_react_agent(
            model=bound_model,
            tools=self.tools,
            pre_model_hook=pre_hook,
            name=self.name,
            state_schema=self.state_schema,
            response_format=self.response_format,
            checkpointer=MemorySaver(),
        )
