---
name: reset-stuck-maestro
description: Resets stuck provisioning by cleaning up BPM and Maestro transaction states.
---

# CONTEXT
This skill resolves "request already in process" errors by updating status flags in Oracle.

# DATA SOURCE
The script `./scripts/reset.sh query <phonenumber> <environment>` runs a Python script that queries the database and prints each row as a Python tuple.

# TUPLE STRUCTURE
Each row is a tuple with **20 elements** (0-indexed). The SQL query defines the columns as:

| Index | Column Name | Description |
|-------|-------------|-------------|
| 0 | ticket_id | BPM event log ticket ID (may contain phone number - always use this column) |
| 1 | event_id | Internal BPM event ID (IGNORE) |
| 2 | event | BPM process name |
| 3 | event_status | Status of the event |
| 4 | event_start | Start timestamp |
| 5 | event_end | End timestamp |
| 6 | log_msg1 | Log message 1 |
| 7 | log_msg2 | Log message 2 |
| 8 | log_msg3 | Log message 3 |
| 9 | bpm_process_id | BPM process ID |
| 10 | bpm_parent_id | Parent process ID |
| 11 | manual_task | Manual task flag |
| 12 | manual_task_id | Manual task ID |
| 13 | manual_task_reason | Reason for manual task |
| 14 | server_host_name | Server hostname |
| 15 | trans_id | Maestro transaction ID (REQUIRED) |
| 16 | source | External system source |
| 17 | member_phone | Member phone number |
| 18 | trans_status | Transaction status |
| 19 | environment | Environment name |

**Note:** All rows have exactly 20 elements. For rows where the LEFT JOIN to maestro_transactions yields no match, `trans_id` (index 15) will be `None`.

# WORKFLOW

### 1. Data Acquisition
- Run `./scripts/reset.sh query <phonenumber> <environment>`
- Capture the printed tuples.

### 2. Analysis & Extraction (CRITICAL)
- Display the raw output for verification.
- **Extract TARGET_TICKET_IDS:** Collect unique values from **column 0** (index 0) of each tuple.
- **Extract TARGET_TRANS_IDS:** Collect unique, non-None values from **column 15** (index 15) of each tuple.
- Show both lists to the user for confirmation before proceeding.

### 3. BPM Cleanup Phase
- Pre-condition: Have TARGET_TICKET_IDS.
- Show: "I will run: `./scripts/reset.sh bpm-cleanup <TARGET_TICKET_IDS> <environment>`"
- Upon "yes", execute and capture "rows updated" count.

### 4. Maestro Cleanup Phase
- Pre-condition: Have TARGET_TRANS_IDS.
- Show: "I will run: `./scripts/reset.sh maestro-cleanup <TARGET_TRANS_IDS> <environment>`"
- Upon "yes", execute and capture "rows updated" count.

### 5. Final Summary
Provide a summary table.