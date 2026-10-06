# 02 - Continuous batching under load (u50)

Host `Linux-x86_64` · `--parallel 4` · 26 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.99 of 4 slots (100%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 837 |

Highest sampled value was **3.99 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Your observation

Peak batch width = 3.99/4 slots (≈100% utilization). Khớp effective concurrency 9.7 > 4 slots từ load-report (effective concurrency = RPS × avg latency = 9.7, tức queue depth ~2.4/slot). Continuous batching hoạt động: 4 slots decode song song, deferred=46 request xếp hàng. Batching effect rõ rệt (peak ≈ max slots).
