# Data Retention Policy

## Purpose

This policy defines how long the organization retains different categories
of data, and the process for secure disposal once retention periods expire.
It exists to balance legal/regulatory retention obligations against the
principle of data minimization.

## Scope

Applies to all data processed or stored by the organization, including
customer data, employee records, system logs, and backups, across all
environments (production, staging, and development).

## Retention Periods

Customer account data is retained for the duration of the active contract
plus 90 days after termination, to support account recovery requests.
Financial and billing records are retained for 7 years to satisfy tax and
audit requirements. Application and infrastructure logs (including access
logs and audit trails) are retained for 12 months in hot storage and a
further 24 months in cold/archival storage. Employee HR records are retained
for the duration of employment plus 6 years, in line with local labor law.
Marketing consent records are retained until consent is withdrawn, plus 3
years to demonstrate historical compliance.

## Disposal Process

When a retention period expires, data must be disposed of using
cryptographic erasure for encrypted volumes or secure overwrite for
unencrypted media. Disposal must be logged with a timestamp, data category,
and the identity of the system or person that performed it. Backups
containing expired data are excluded from restoration and are rotated out
within one backup cycle.

## Exceptions

Data subject to a legal hold, active litigation, or an open regulatory
investigation is exempt from scheduled disposal until the hold is formally
lifted by Legal. Exceptions must be logged in the Legal Hold Register with a
review date no more than 90 days out.

## Review Cadence

This policy is reviewed annually by the Data Governance team, or immediately
following a material change in applicable law (e.g. GDPR guidance updates).
