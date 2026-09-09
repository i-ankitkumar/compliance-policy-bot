# Incident Response Policy

## Purpose

Defines how the organization detects, triages, contains, and reports
security and privacy incidents, so that response is consistent and
regulatory notification deadlines are never missed.

## Severity Classification

Incidents are classified as Critical, High, Medium, or Low. Critical
incidents involve confirmed unauthorized access to customer data or a full
production outage. High incidents involve a credible but unconfirmed breach,
or a significant service degradation. Medium and Low incidents cover
contained security events with no evidence of data exposure.

## Response Timelines

Critical incidents require an on-call responder to acknowledge within 15
minutes and a response team assembled within 30 minutes. High incidents
require acknowledgment within 1 hour. All incidents require an initial
written summary within 24 hours of detection, regardless of severity.

## Containment and Eradication

Once an incident is confirmed, the response team isolates affected systems
before investigating root cause, to limit further exposure. Credentials
suspected of compromise are rotated immediately. Affected systems are not
returned to production until the root cause is identified and a fix or
mitigation has been verified.

## Regulatory Notification

Where an incident constitutes a personal data breach under applicable data
protection law (including GDPR Article 33), the Data Protection Officer must
be notified within 4 hours of confirmation, so that any required regulator
notification can be made within the 72-hour statutory window. Affected data
subjects are notified without undue delay where the breach is likely to
result in a high risk to their rights and freedoms.

## Post-Incident Review

Every Critical or High incident receives a blameless post-incident review
within 5 business days of resolution, documenting timeline, root cause,
impact, and corrective actions with owners and due dates. Repeat root causes
across incidents are escalated to the risk register.

## Roles

The Incident Commander owns overall coordination and external communication
during an active incident. The on-call engineer owns technical triage and
containment. Legal and the DPO are engaged for any incident with a plausible
data protection dimension.
