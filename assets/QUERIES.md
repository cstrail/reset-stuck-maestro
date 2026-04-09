**maestro Results Query:
execute the following query:
SELECT
    bel.ticket_id AS ticket_id,
    bel.id AS event_id, 
    bel.bpm_process_name AS event, 
    bel.process_status AS event_status, 
    TO_CHAR(bel.start_time, 'YYYY-MM-DD HH:MI:SS') AS event_start, 
    TO_CHAR(bel.end_time, 'YYYY-MM-DD HH:MI:SS') AS event_end,
    replace(replace(bel.log_msg1,'[','_'),']','_') as log_msg1, 
    replace(replace(bel.log_msg2,'[','_'),']','_') as log_msg2, 
    replace(replace(bel.log_msg3,'[','_'),']','_') AS log_msg3, 
    bel.bpm_process_id, 
    bel.bpm_parent_process_id AS bpm_parent_id, 
    bel.manual_task, 
    bel.manual_task_id, 
    bel.manual_task_reason, 
    bel.server_host_name,
    mt.id AS trans_id, 
    mt.external_system AS source, 
    mt.member_phone, 
    mt.status AS trans_status, 
    mt.environment
FROM bpm_event_log bel
LEFT OUTER JOIN maestro_transactions mt ON bel.MAESTRO_ID = mt.ID
WHERE (mt.MEMBER_PHONE = '{phoneumber}' OR substr(bel.log_msg3, 5, 10) = '{phonenumber}')
ORDER BY bel.start_time DESC;

**bpm cleanup:
UPDATE bpm_event_log SET process_status = 'FAILURE', end_time = start_time, log_msg1 = 'Internal provisioning error'
WHERE ticket_id in({ticket_ids_to_reset}) AND process_status IN ('IN_PROGRESS','RETRY');

**maestro cleanup:
UPDATE maestro_transactions SET status= 'FAILURE', is_complete = 'Y', message = 'Manual completion', last_modified_date = SYSDATE
WHERE id in({trans_ids_to_reset});
