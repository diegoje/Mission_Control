# HEARTBEAT.md

## Periodic Checks (run via heartbeat)

### Daily News Digest
- **Status:** Automated via cron (morning-news at 07:00)
- No action needed in heartbeat

### Friday Business Plan Review
- **When:** Fridays at 09:00 Europe/Berlin
- **Action:** Send reminder to user
- **Trigger:** User replies "RUN" to execute full review
- **Message:**
  ```
  📊 Friday Business Plan Review
  
  Time to review and update the MedForm3D Business Analysis!
  
  Reply with:
  • "RUN" — I'll execute the full review
  • Or ask specific questions about the business plan
  ```

### Sunday Accounting Reminder
- **When:** Sundays at 10:00 Europe/Berlin
- **Action:** Send reminder to Accounting group
- **Trigger:** User replies "process receipts" or sends receipt images
- **Message:**
  ```
  📊 Sunday Accounting Reminder
  
  Time to process receipts!
  
  Reply with:
  • "process receipts" — I'll process all receipts in '2026 to be processed'
  • Or send me receipt images directly
  ```

## Implementation
The heartbeat checks current day/time and sends reminders when conditions are met.
Track last sent reminders to avoid duplicates.
