###Ticket_Id
SELECT DISTINCT
    bel.ticket_id
FROM bpm_event_log bel
INNER JOIN maestro_transactions mt ON bel.maestro_id = mt.id
WHERE bel.ticket_id IS NOT NULL
  AND mt.id IS NOT NULL
  AND (mt.member_phone = '{phonenumber}' OR SUBSTR(bel.log_msg3, 5, 10) = '{phonenumber}');

###Trans_Id
SELECT DISTINCT
    mt.id AS trans_id
FROM bpm_event_log bel
INNER JOIN maestro_transactions mt ON bel.maestro_id = mt.id
WHERE bel.ticket_id IS NOT NULL
  AND mt.id IS NOT NULL
  AND (mt.member_phone = '{phonenumber}' OR SUBSTR(bel.log_msg3, 5, 10) = '{phonenumber}');

###bpm cleanup
UPDATE bpm_event_log SET process_status = 'FAILURE', end_time = start_time, log_msg1 = 'Internal provisioning error'
WHERE ticket_id in({Ticket_Ids},{phonenumber}) AND process_status IN ('IN_PROGRESS','RETRY');

###maestro cleanup:
UPDATE maestro_transactions SET status= 'FAILURE', is_complete = 'Y', message = 'Manual completion', last_modified_date = SYSDATE
WHERE id in({Trans_Ids});
