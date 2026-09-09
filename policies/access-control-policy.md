# Access Control Policy

## Purpose

Establishes the rules for granting, reviewing, and revoking access to
systems and data, so that access is limited to what a role genuinely
requires and can always be traced to an individual.

## Principle of Least Privilege

Access is granted based on job function, not convenience. Standing
administrative access to production systems is prohibited; elevated access
is granted just-in-time through a request-and-approval workflow and expires
automatically after 8 hours or the end of the task, whichever is sooner.

## Authentication Requirements

All access to internal systems requires multi-factor authentication (MFA).
Shared or generic accounts are not permitted for interactive use; service
accounts used by automation must be scoped to the minimum set of actions
required and have their credentials rotated at least every 90 days.

## Access Reviews

Access to production systems and customer data is reviewed quarterly by the
resource owner. Access for employees who change roles or teams is reviewed
within 5 business days of the change. Access for departing employees is
revoked within 4 hours of their final day, and immediately upon involuntary
termination.

## Role-Based Access Control

Access is assigned through defined roles rather than individual grants
wherever the underlying system supports it. New roles must be documented
with their intended scope and approved by the relevant system owner before
being assigned to any user.

## Logging and Monitoring

All authentication events and privileged actions are logged to a
centralized, tamper-evident log store. Logs are retained per the Data
Retention Policy and are monitored for anomalous access patterns, such as
access outside normal working hours or from an unrecognized location.

## Violations

Access granted outside this policy, or access retained past its approved
window, is treated as a security incident and handled under the Incident
Response Policy.
