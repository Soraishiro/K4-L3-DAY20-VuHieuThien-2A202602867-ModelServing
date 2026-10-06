# 01 - Tune: thread-count sweep

Model `Qwen3.5-0.8B-Q4_K_M.gguf` · host `Linux-x86_64` · llama.cpp `b10488`
CPU: **2 physical · 4 logical** cores · `ngl=0` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
| :----------- | ------------: | ------: |
| 1            |           7.7 |     75% |
| 2            |          10.3 |    100% |
| 4            |           1.4 |     13% |

**Best**: `-t 2` at 10.3 tok/s
**Slowest tested**: `-t 4` at 1.4 tok/s (7.49x spread)
**Against the physical-core default** (`-t 2`, 10.3 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=2 make bench
```

## Your explanation

Knee ở `-t 2` (physical cores). Trên đó (`-t 4`) throughput sụt từ 10.3 → 1.4 tok/s (7.5×). Thread thừa (`-t 4` > 2 core vật lý) tranh memory bandwidth và cache L3. Decode bị chặn bởi bandwidth, thread thừa chỉ làm tăng contention bus/cache. Peak đúng ở physical core count, rồi giảm do oversubscription bandwidth.
