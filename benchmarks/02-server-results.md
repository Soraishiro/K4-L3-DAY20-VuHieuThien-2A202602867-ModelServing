# 02 - Serve: load test + saturation reading

Host `Linux-x86_64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=2` ·
`ngl=0`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 635 | 10.86 | 1 | 4 | 6 | 0.0 | 100.0% |
| 50 | 20 | 0.37 | 27000 | 50000 | 50000 | 9.7 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **0.03x** (1% of linear) |
| P95 latency | **12500.00x** |
| Effective concurrency at 50 users | 9.7 vs `--parallel 4` slots (occupancy/slot ratio 2.42) |

**Saturated.** Throughput delivered only 0.03x for 5x the offered load, and effective concurrency (9.7) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 0.03x while P95 moved 12500.00x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

## Your reading

Server bão hòa ở ≤50 users. Bằng chứng: throughput giảm 0.03× khi load 5×, P95 tăng 12500×, effective concurrency 9.7 > 4 slots. Con số thuyết phục: `n_busy_slots_per_decode` peak 3.99/4 từ metrics — 4 slot decode full, queue deferred=46. Để nâng goodput@SLO, đổi `--parallel` lên trước (tăng slot decode), vì bottleneck là số slot decode (busy_slots peak 3.99/4).
