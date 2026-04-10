---
name: reset-stuck-maestro
description: Resets stuck provisioning by cleaning up BPM and Maestro transaction states.
---

# CONTEXT
This skill resolves "request already in process" errors by updating status flags in Oracle.
Prefer to use sqlplus.  If not installed persuade user to install it.
Will store sql output in 2 variables:
Ticket_Ids and Trans_Ids.
**Ticket_Ids will ALWAYS include {phonenumber}.  Make sure of this**

# PRERQUISITES
- prompt user for 10 digit phonenumber if not provided
- prompt user for environment - TLQ or PROD

# DATA SOURCE
Connections = ./agents/skills/reset-stuck-maestro/assets/CONNECTIONS.md - PROD or TLQ depending on user input
Ticket_Ids = ./agents/skills/reset-stuck-maestro/assets/QUERIES.md Ticket_Id query
Trans_Ids = ./agents/skills/reset-stuck-maestro/assets/QUERIES.md Trans_id query
bpm_cleanup = ./agents/skills/reset-stuck-maestro/assets/QUERIES.md bpm cleanup
maestro_cleanup = ./agents/skills/reset-stuck-maestro/assets/QUERIES.md maestro cleanup

# WORKFLOW

### 1. Data Acquisition
- Connect to database
- Run the query to get Ticket_Ids
- Run the query to get Trans_Ids

### 2. Analysis & Extraction (CRITICAL)
- Show both lists to the user for confirmation before proceeding.

### 3. BPM Cleanup Phase
- Pre-condition: Have Ticket_Ids.
- Ticket_Ids needs to be a comma separated list surrounded by ''.  (e.g. 12345 23456 becomes '12345,'23456')
- display to user the exact 'bpm_cleanup' SQL statement to be executed
- Upon "yes", execute 'bpm_cleanup' query and capture "rows updated" count.

### 4. Maestro Cleanup Phase
- Pre-condition: Have Trans_Ids.
- display to user the exact 'maestro_cleanup' SQL statement to be executed
- Upon "yes", execute 'maestro_cleanup' and capture "rows updated" count.

### 5. Final Summary
Provide a summary table.
