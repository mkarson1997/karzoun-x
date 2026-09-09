# KARZOUN-X Phase 6 Communication-Delay Results

Experiment: `phase6-communication-delay-v1`
Phase 5 v2 RAG scenarios reused: **12**

This deterministic counterfactual timing study reuses the measured local RAG inference latencies from Phase 5 v2. The hypothetical ground-dependent path uses the same compute latency and adds only round-trip light-time, so the comparison isolates propagation delay. It is not a live network or mission-operations test.

| Profile | OWLT (s) | Local completion | Ground completion | Mean local (s) | Mean ground (s) | Propagation penalty (s) |
|---|---:|---:|---:|---:|---:|---:|
| zero_delay_reference | 0.0 | 1.0000 | 1.0000 | 27.159 | 27.159 | 0.000 |
| lunar_reference | 1.0 | 1.0000 | 1.0000 | 27.159 | 29.159 | 2.000 |
| mars_near_reference | 240.0 | 1.0000 | 1.0000 | 27.159 | 507.159 | 480.000 |
| mars_far_reference | 1440.0 | 1.0000 | 1.0000 | 27.159 | 2907.159 | 2880.000 |
| ground_link_outage | 0.0 | 1.0000 | 0.0000 | 27.159 | n/a | n/a |

## Deadline availability

Rates below are the fraction of the 12 held-out synthetic cases whose decision is available by each deadline.

| Profile | Path | 30 s | 60 s | 10 min | 30 min | 60 min |
|---|---|---:|---:|---:|---:|---:|
| zero_delay_reference | local | 0.6667 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| zero_delay_reference | ground | 0.6667 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| lunar_reference | local | 0.6667 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| lunar_reference | ground | 0.5833 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| mars_near_reference | local | 0.6667 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| mars_near_reference | ground | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 |
| mars_far_reference | local | 0.6667 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| mars_far_reference | ground | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| ground_link_outage | local | 0.6667 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ground_link_outage | ground | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

> NASA reference profiles are used only to parameterize propagation delay. The experiment does not model DSN scheduling, relay latency, packet loss, human approval time, or ground compute differences.
> The reused Phase 5 v2 cases are synthetic and are not evidence of flight readiness.
