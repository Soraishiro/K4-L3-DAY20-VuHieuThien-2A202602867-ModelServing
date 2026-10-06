# 01 - Measure: latency baseline

Model `Qwen3.5 0.8B` · host `Linux-x86_64` · llama.cpp `b10488`
Settings: `threads=2` `ngl=0` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `Q4_K_M` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 3253 | 402 / 1843 | 55.8 / 85.4 | 3530 / 5321 / 5321 | 17.9 |
| UD-Q2_K_XL | 0.39 | 3286 | 599 / 1076 | 78.5 / 174.7 | 4236 / 11584 / 11584 | 12.7 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.41x SLOWER** than `Q4_K_M` here, despite being 0.11 GB smaller. That is a real result, not a mistake: fewer bits only buys speed when decode is limited by memory bandwidth. On a machine that is compute-limited instead — few cores, no GPU offload — the extra dequantization work of a heavily-quantized format can cost more than the bytes it saves. Say which case yours is.

## Your observation

UD-Q2_K_XL decode **1.41× CHẬM hơn** (12.7 vs 17.9 tok/s), nhỏ hơn 0.11 GB. TTFT thấp hơn (599 vs 402ms P50). Trên máy này (2 core vật lý, WSL2), overhead giải mã 2-bit lớn hơn lợi thế bandwidth. Thử ask cùng câu trên `make serve` vs `--compare`: 2-bit câu trả lời ngắn gọn hơn nhưng chậm hơn. **Kết luận: 2-bit KHÔNG đáng dùng** trên máy này — overhead giải mã vượt lợi thế bandwidth.
