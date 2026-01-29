# Examples

Real-world examples of using the Airflow MCP server with AI coding assistants.

## Available Examples

| Example | Description | Tools Used |
|---------|-------------|------------|
| [Analyze DAG Run Configs](analyze-dag-run-configs.md) | Extract configuration patterns from 120+ manual DAG runs | `fetch_dags`, `get_dag_runs` |

---

## Adding New Examples

When you have a useful MCP interaction, add it here:

1. Create a new `.md` file in this folder
2. Include:
   - **User prompt** - What you asked
   - **AI steps** - Tool calls and reasoning
   - **Final output** - The useful result
   - **Key takeaway** - Why this is valuable
3. Update this README with a link

---

## Example Template

```markdown
# Example: [Title]

Brief description of what this example demonstrates.

---

## User Prompt

> *"Your actual prompt here"*

---

## AI Response

### Step 1: [What the AI did first]

\`\`\`
🔧 tool_name
   param: value

→ Result: ...
\`\`\`

[Continue with more steps...]

---

## Final Summary

[The useful output]

---

## Key Takeaway

[Why this matters]

---

## Tools Used

- `tool_name` - What it does
```
