---
name: reset-stuck-maestro
description: Resets stuck provisioning by cleaning up BPM and Maestro transaction states.
---

# CONTEXT
This skill resolves "request already in process" errors by updating status flags in Oracle.

# COLUMN MAPPING (0-indexed)
- 0: ticket_id (BPM Log - REQUIRED for bpm-cleanup)
- 1: event_id (Internal - IGNORE)
- 15: trans_id (Maestro Trans - REQUIRED for maestro-cleanup)

# WORKFLOW

### 1. Data Acquisition
- **Constraint**: If 10-digit <phonenumber> is missing, prompt user.
- **Action**: Run `./reset.sh query <phonenumber>`

### 2. Analysis & Extraction (CRITICAL)
- Display results in a Markdown table.
- **Mandatory Variable Extraction**: Identify and list values explicitly before proceeding:
    - `TARGET_TICKET_IDS`: Unique values from Column 0.
    - `TARGET_TRANS_IDS`: Unique non-None values from Column 15.
- **Warning**: Do NOT use Column 1 for any cleanup action.

### 3. BPM Cleanup Phase
- **Pre-condition**: Must have `TARGET_TICKET_IDS`.
- **User Confirmation**: Show: "I will run: `./reset.sh bpm-cleanup <ids>`"
- **Action**: Upon "yes", execute and capture "rows updated" count.

### 4. Maestro Cleanup Phase
- **Pre-condition**: Must have `TARGET_TRANS_IDS`.
- **User Confirmation**: Show: "I will run: `./reset.sh maestro-cleanup <ids>`"
- **Action**: Upon "yes", execute and capture "rows updated" count.

### 5. Final Summary
- Provide a summary table:
| Phase | IDs Processed | Rows Updated |
| :--- | :--- | :--- |
| BPM | ... | ... |
| Maestro | ... | ... |
