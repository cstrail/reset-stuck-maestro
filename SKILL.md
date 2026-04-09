---
name: reset-stuck-maestro
description: Resets provisioning when errored with another request already in process
---

**First run setup:**
The script will automatically create a `.venv` virtual environment and install `oracledb` on first run.

Using wrapper script: `reset.sh` (auto-creates venv and runs scripts/reset_maestro.py)

To reset a provisioning already in process error in maestro:

1. Ask user to input a 10 digit phonenumber if not provided in prompt

2. Run wrapper script to query results:
   ```bash
   ./reset.sh query <phonenumber>
   ```

3. Print out a formatted table with all the results for viewing

4. From results, extract (use these exact column positions - 0-based indexing):
   - **ticket_id** - Unique values from column index 0, always including the provided phone number as a ticket_id
   - **trans_id** - Unique non-None values from column index 15 (NOT index 1!)
   
   The query returns these columns in order:
   - Index 0: ticket_id (from bpm_event_log) ← USE THIS for bpm cleanup
   - Index 1: event_id (from bpm_event_log, bel.id) ← DO NOT USE
   - Index 15: trans_id (from maestro_transactions, mt.id) ← USE THIS for maestro cleanup
   
   CRITICAL: Do NOT use event_id (index 1) for maestro cleanup! Use trans_id (index 15)!

5. Let user know which ticket_ids and trans_ids have been selected

6. **BPM Cleanup** - Present the intended query to user and get approval before running:
   ```bash
   ./reset.sh bpm-cleanup <ticket_id1,ticket_id2,...>
   ```
   This updates process_status to 'FAILURE' for ticket_ids where process_status is 'IN_PROGRESS' or 'RETRY'
   Save rows updated for followup summary

7. **Maestro Cleanup** - Present the intended query to user and get approval before running:
   ```bash
   ./reset.sh maestro-cleanup <trans_id1,trans_id2,...>
   ```
   This updates status to 'FAILURE', is_complete to 'Y', message to 'Manual completion'
   Save rows updated for followup summary

8. Provide user with a summary of all rows updated and status
