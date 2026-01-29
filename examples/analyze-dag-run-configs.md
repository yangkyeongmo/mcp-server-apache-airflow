# Example: Analyzing Manual DAG Run Configurations

This example shows how the AI uses MCP tools to investigate DAG runs, handle partial information, and extract insights.

---

## User Prompt

> *"Get the manual DAG runs configuration details for the stage0_prep DAG"*

---

## AI Response

### Step 1: Initial Query

The AI first tries to get DAG runs with the provided name:

```
🔧 get_dag_runs
   dag_id: "stage0_prep"
   order_by: "-execution_date"
   limit: 100

→ Result: No DAG runs found
```

### Step 2: Search for Matching DAGs

The query returned no results, so the AI searches for DAGs matching the pattern:

```
🔧 fetch_dags
   dag_id_pattern: "stage0"
   limit: 50

→ Found: "arc_final_proposal_ingest_stage0_prep"
```

### Step 3: Retrieve Runs with Correct ID

Now with the correct DAG ID, it retrieves the runs:

```
🔧 get_dag_runs
   dag_id: "arc_final_proposal_ingest_stage0_prep"
   limit: 100
   order_by: "-execution_date"

→ Result: 120 manual runs found
```

---

## Final Summary

### Manual DAG Run Configuration for `arc_final_proposal_ingest_stage0_prep`

**Total Manual Runs**: 120

#### States Processed

| State | Runs |
|-------|------|
| VA (Virginia) | 21 |
| AZ (Arizona) | 12 |
| XY (Test) | 9 |
| LA (Louisiana) | 7 |
| AR (Arkansas) | 6 |
| OK (Oklahoma) | 5 |
| GU (Guam) | 3 |
| TX (Texas) | 3 |
| MN (Minnesota) | 2 |
| MS (Mississippi) | 1 |

#### Common Config Patterns

**clean_up_transformed_table**: `True` (~62%) / `False` (~38%)

**dp_rp_relationship_type**:
- `"1DP-1RP"` (One-to-One)
- `"provided-deployment_reporting.csv"` (CSV file)

**sa_agreement_type**:
- `"1Provider-1SA"` (One Provider, One Subgrant)
- `"provided-subgrant_agreements.csv"` (CSV file)

#### Example Configurations

```json
// Arizona
{
  "clean_up_transformed_table": true,
  "state": "AZ",
  "version_date": "2026-01-05",
  "gdrive_folder_id": "1TUnYWUlIiABZ4wFF0ms6gcuIHJgXN-RI",
  "sa_agreement_type": "1Provider-1SA",
  "dp_rp_relationship_type": "provided-deployment_reporting.csv"
}

// Virginia
{
  "clean_up_transformed_table": true,
  "state": "VA",
  "version_date": "2025-12-15",
  "gdrive_folder_id": "1LUGh4IEQpO2X9AfoauwlfM2ldzB1GdRJ"
}
```

**Run Status**: 118 successful, 2 failed
**Date Range**: 2025-11-27 to 2026-01-28
**Typical Duration**: 6-8 minutes per run

---

## Key Takeaway

The AI handled the partial DAG name gracefully, searched for matches, found the correct DAG, and summarized 120 runs into actionable insights — all from a single prompt.

---

## Tools Used

- `fetch_dags` - Search DAGs by pattern
- `get_dag_runs` - Retrieve run history with configs

## Related Examples

- [More examples...](./README.md)
