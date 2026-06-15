"""
Gemini agentic loop using the new google-genai SDK.
"""
from google import genai
from google.genai import types

from app.core.config import settings
from app.tools.agent_tools import TOOL_DISPATCH, TOOL_SCHEMA

SYSTEM_PROMPT = """You are an expert internal auditor AI assistant.
You have access to tools that let you read Excel sheets, search PDFs, and generate structured audit findings.
When the user asks about data, always use the tools to look it up rather than guessing.
Format audit findings using the generate_audit_finding tool.
Be precise, professional, and cite the specific data you find."""


def run_agent(
    user_message: str,
    history: list[dict],
    document_paths: list[str],
) -> str:
    """
    Run one turn of the audit agent.
    history: list of {"role": "user"|"model", "content": str}
    document_paths: list of file paths available to the agent
    """
    client = genai.Client(api_key=settings.gemini_api_key)

    # Inject document context
    context = ""
    if document_paths:
        context = (
            "Available documents (use these exact paths in tool calls):\n"
            + "\n".join(f"- {p}" for p in document_paths)
            + "\n\n"
        )

    augmented_message = context + user_message

    # Build chat history in genai format
    contents = []
    for msg in history:
        role = msg["role"]  # "user" or "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

    # Add current user message
    contents.append(types.Content(role="user", parts=[types.Part(text=augmented_message)]))

    tool = types.Tool(function_declarations=TOOL_SCHEMA["function_declarations"])
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[tool],
    )

    # Agentic loop
    max_iterations = 10
    for _ in range(max_iterations):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        parts = candidate.content.parts

        # Check for function calls
        function_calls = [p for p in parts if p.function_call is not None]
        if not function_calls:
            # Extract text response
            for part in parts:
                if part.text:
                    return part.text
            break

        # Append model response to contents
        contents.append(candidate.content)

        # Execute tools and collect results
        tool_response_parts = []
        for part in function_calls:
            fc = part.function_call
            fn_name = fc.name
            fn_args = dict(fc.args) if fc.args else {}
            try:
                result = TOOL_DISPATCH[fn_name](fn_args)
            except KeyError:
                result = f"Unknown tool: {fn_name}"
            except Exception as e:
                result = f"Error executing {fn_name}: {str(e)}"

            tool_response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fn_name,
                        response={"result": result},
                    )
                )
            )

        contents.append(types.Content(role="tool", parts=tool_response_parts))

    return "I was unable to generate a response. Please try again."
