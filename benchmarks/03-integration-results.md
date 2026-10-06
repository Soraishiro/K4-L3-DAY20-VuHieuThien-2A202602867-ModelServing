# 03 - Integrate: RAG pipeline run

Host `Linux-x86_64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.0 | 14000.7 | 14000.8 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 5141.3 | 5141.3 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.0 | 7615.3 | 7615.3 |

Mean per stage (ms): embed **0.0** · retrieve **0.0** ·
llm **8919.1** · total **8919.1**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Based on the context provided, **Goodput** is more useful than raw throughput because it focuses on the specific metrics that define a system's performance:

1.  **It counts only requests per second meeting targets:** Goodput specifically counts the requests per second that met the **TTFT** (Throughput to Failure Threshold) and **TPOT** (Throughput to Performance Overhead) targets.
2.  **It ignore

**What problem does PagedAttention actually solve?**

> PagedAttention solves the problem of **internal fragmentation** in GPU memory.

Specifically, it addresses the issue where the KV cache is stored in non-contiguous pages, causing wasted space. By removing this fragmentation, it allows the engine to utilize more of the available GPU memory for cache operations.

**When does splitting prefill and decode help?**

> Based on the provided context, splitting prefill and decode helps when **prefill is compute-bound and decode is memory-bandwidth-bound**.

The context explicitly states that prefilling the model requires significant computation (likely GPU memory or CPU cores), while decoding requires significant memory bandwidth. By splitting these operations into separate pools, the system can utilize different 


## Which N16-N19 pieces are real

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | stub |
| N17 Data pipeline | stub |
| N18 Lakehouse | stub |
| N19 Vector + features | stub (keyword overlap fallback) |
| N20 Serving | `llama-server` | real |

Dominant stage llm (100%) đúng kỳ vọng — embedding/retrieve dùng fallback keyword overlap (0ms). Giảm latency 2× → tấn công LLM: **đừng** dùng 2-bit (UD-Q2_K_XL đã chứng minh 1.41× chậm hơn); tăng `--parallel` hoặc tune threads (`-t 2` đã cho 7.4× speedup).
