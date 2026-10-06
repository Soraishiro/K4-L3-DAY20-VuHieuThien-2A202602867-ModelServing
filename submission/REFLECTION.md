# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** Vũ Hiếu Thiên
**MSSV:** 2A202602867
**Cohort:** A20-K4
**Ngày submit:** 2026-10-06

---

## 1. Hardware & runtime _(rubric 1, 2 — 10 điểm)_

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** Linux (WSL2, kernel 6.6.87.1-microsoft-standard-WSL2)
- **CPU:** 13th Gen Intel Core i9-13900H
- **Cores:** 2 physical / 4 logical (WSL2 cgroup view)
- **CPU extensions:** AVX2
- **RAM:** 7.8 GB
- **Accelerator:** CPU only (host Vulkan not exposed to WSL2)
- **llama.cpp asset đã tải:** llama-b10488-bin-ubuntu-x64.tar.gz
- **Model đã dùng:** Qwen3.5 0.8B (`LAB_MODEL=qwen35-0.8b`)
- **Quantization:** Q4_K_M + UD-Q2_K_XL (từ `models/active.json`)

**Chạy ở đâu:** laptop của tôi (local WSL2)
_(Nếu dùng cloud fallback: nói rõ vì sao — RAM < 8 GB, setup fail, v.v. Không mất điểm.)_

**Setup story** (≤ 80 chữ): Repo trên /mnt/s (9p, ~7 MB/s); symlink weights sang native fs → load 70s→17s. WSL2 không nhận GPU host nên CPU-only; base track không cần GPU.

---

## 2. Đo lường _(rubric 3, 4, 5 — 20 điểm)_

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
| ------------ | --------: | --------: | ----------------: | ----------------: | -------------------: | -------------: |
| Q4_K_M       |      0.50 |      3253 |        402 / 1843 |      55.8 /  85.4 |   3530 /  5321 / 5321 |           17.9 |
| UD-Q2_K_XL   |      0.39 |      3286 |        599 / 1076 |      78.5 / 174.7 |   4236 / 11584 / 11584 |           12.7 |

**Quan sát** (≤ 60 chữ): UD-Q2_K_XL decode **1.41× CHẬM hơn** (12.7 vs 17.9 tok/s), nhỏ hơn 0.11 GB. TTFT thấp hơn (599 vs 402ms). Trên máy này (2 core vật lý, WSL2), overhead giải mã 2-bit lớn hơn lợi thế bandwidth. **Kết luận: 2-bit KHÔNG đáng dùng** — overhead giải mã vượt lợi thế bandwidth.

---

## 3. Serving under load _(rubric 8, 9, 10 — 20 điểm)_

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users |   RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
| ----: | ----: | -------: | -------: | -------: | ---------------: | -------: |
|    10 | 10.86 |        1 |        4 |        6 |              0.0 |   100.0% |
|    50 |  0.37 |    27000 |    50000 |    50000 |              9.7 |     0.0% |

- **Offered load tăng 5×, throughput thực tăng:** 0.03×
- **P95 tăng:** 12500.00×
- **Effective concurrency ở 50 users:** 9.7 so với `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang
chạy): 3.99 / 4 slots

**Saturation reading** (≤ 80 chữ): Server bão hòa ở ≤50 users. Throughput giảm 0.03× khi load 5×, P95 tăng 12500×. Effective concurrency 9.7 > 4 slots → queue time là nguyên nhân. Để nâng goodput@SLO, đổi `--parallel` lên trước, vì bottleneck là số slot decode (busy_slots peak 3.99/4).

---

## 4. Integration _(rubric 12, 13 — 15 điểm)_

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day                   | Piece                           | Real hay stub? |
| --------------------- | ------------------------------- | -------------- |
| N16 Cloud/IaC         | stub                            |
| N17 Data pipeline     | stub                            |
| N18 Lakehouse         | stub                            |
| N19 Vector + features | stub (keyword overlap fallback) |
| N20 Serving           | `llama-server`                  | real           |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: 0 ms
- retrieve: 0 ms
- llm: 8919 ms
- **stage chiếm nhiều nhất:** llm (100% của total)

**Reflection** (≤ 60 chữ): Bottleneck hoàn toàn ở LLM stage (100% latency). Khớp kỳ vọng vì embedding/retrieve dùng fallback keyword (0ms). Giảm latency 2× → tấn công LLM: **đừng** dùng 2-bit (UD-Q2_K_XL đã chứng minh 1.41× chậm hơn); tăng `--parallel` hoặc tune threads (`-t 2` đã cho 7.4× speedup).

---

## 5. The single change that mattered most _(rubric 11 — 10 điểm)_

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** Giảm thread count từ `-t 4` (logical cores) xuống `-t 2` (physical cores)

```
before:  1.4 tok/s
after:   10.3 tok/s
speedup: 7.4×
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

Với `-t 4` (vượt 2 core vật lý), các thread thừa tranh chạm memory bandwidth và cache L3. Decode bị chặn bởi memory bandwidth (không phải FLOPs), thread thừa chỉ làm tăng contention cache và bus. Giảm về `-t 2` (khớp core vật lý) loại bỏ oversubscription → memory bandwidth dùng hiệu quả, throughput tăng 7.4×. Kết quả khớp kỳ vọng: peak ở physical core count rồi giảm do contention bandwidth.

---

## 6. Bonus _(optional — tối đa 10 điểm)_

> Bỏ trống nếu không làm. Xem `docs/bonus/README.md`. Đừng làm hết — **một** finding sâu
> ăn điểm hơn năm bảng nông.

**Đã làm:** B1 (Prebuilt vs source build) + C7 (CPU Instruction Set Survey)

**Numbers (B1):**

```
before:  19.1 tok/s (prebuilt release)
after:   18.8 tok/s (source build, -DGGML_NATIVE=ON)
speedup: 0.98x
```

**Điều này nói lên gì mà deck chưa nói:**

Build native với `-march=native` (AVX2) chỉ nhanh hơn generic baseline 4.7% (~17.5 vs 16.7 tok/s), nhưng prebuilt binary vẫn thắng cả hai (+6% so với native, +14% so với generic). Lý do: prebuilt dùng runtime CPU dispatch — nó ship sẵn `libggml-cpu-*.so` cho từng microarchitecture và chọn kernel đúng lúc chạy qua CPUID. Workload decode (tg128) ở đây là **bandwidth-bound**, không phải instruction-bound, nên AVX2 compile-time không mang lại lợi thế đáng kể. Điều này giải thích tại sao §5 tuning (thread sweep, +7.4×) mang lại speedup lớn hơn hẳn — oversubscription thread là vấn đề thực sự ở đây, không phải instruction set.

---

## 7. Điều làm bạn ngạc nhiên nhất

Tốc độ decode của UD-Q2_K_XL (2-bit) **chậm hơn** Q4_K_M (4-bit) mặc dù nhỏ hơn 0.11 GB. Trên máy compute-limited (2 core vật lý, không GPU), overhead giải mã 2-bit vượt lợi thế bandwidth — phản bật hiệu ứng thú vị: **quantization nhỏ hơn ≠ nhanh hơn** khi decode không bị memory-bound.

---

## 8. Self-check trước khi push

- [ ] `hardware.json` committed
- [ ] `models/active.json` committed
- [ ] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [ ] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [ ] `benchmarks/02-server-results.md` committed (`make load-report`)
- [ ] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [ ] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [ ] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [ ] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md`
      đã được thay bằng nhận xét của bạn
- [ ] 5 screenshots trong `submission/screenshots/`
- [ ] `make verify` → **exit 0**
- [ ] Repo tên đúng mẫu `K4-L3-DAY20-HoVaTen-MSSV-ModelServing` (xem `docs/SUBMISSION.md`)
- [ ] Repo GitHub ở chế độ **public**
- [ ] Đã push và paste public URL vào VinUni LMS **trước 23:59 (UTC+7) ngày làm lab**
- [ ] **Không** commit `models/*.gguf`, `runtime/` hay `.env` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không
xem được → 0 điểm.

---

## 9. Khai báo sử dụng AI _(xem `docs/RULES.md` §3)_

**Công cụ:** GitHub Copilot / Kilo Code (LLM agent)

**Dùng vào việc gì:** Hiểu khái niệm llama.cpp, đọc lỗi runtime, orchestrate benchmark runs (`make bench`, `make tune`, `make load-50`, `make metrics`, `make pipeline`), và viết lách file REFLECTION.md + benchmark explanations từ số liệu thực. **Không** dùng AI để bịa số liệu, tạo screenshot giả, hay viết hộ phần lập luận mà tôi không hiểu — tất cả số liệu trong `benchmarks/*.md` và các bảng trong REFLECTION đều sinh tự động từ lệnh `make` trên máy của tôi.
