# Bonus C7 - CPU Instruction Set Survey

## Thiết lập

| Build | CMake flag | Target |
|-------|------------|--------|
| Generic (baseline) | `-DGGML_NATIVE=OFF` | x86-64 baseline (no AVX2) |
| Native | `-DGGML_NATIVE=ON` | `-march=native` (AVX2) |
| Prebuilt | — | Runtime CPU dispatch |

CPU: 13th Gen Intel i9-13900H (WSL2, 2P/4L cores, AVX2, no AVX-512)  
Model: Qwen3.5-0.8B Q4_K_M · threads=2 · ngl=0 · metric: tg128

## Số liệu

| Build | tg128 (tok/s) | vs Generic |
|-------|---------------|------------|
| Generic (`-DGGML_NATIVE=OFF`) | 16.74 ± 2.30 | 1.00x |
| Native (`-DGGML_NATIVE=ON`) | 17.53 ± 2.64 | **1.05x** (+4.7%) |
| Prebuilt (runtime dispatch) | 19.10 | 1.14x |

## Phân tích

**Native nhanh hơn Generic 4.7%** — đúng kỳ vọng: bật `-march=native` cho phép compiler dùng AVX2 cho các kernel decode (dot product, matmul). CPU i9-13900H hỗ trợ AVX2; generic baseline không dùng AVX2 nên chậm hơn.

**Tuy nhiên prebuilt vẫn nhanh nhất (19.1 vs 17.5 tok/s, +9%)** — lý do: prebuilt binary dùng **runtime CPU dispatch**. Build release ship sẵn nhiều `libggml-cpu-*.so` (haswell, skylake, skylakex, zen4, v.v.) và chọn đúng kernel lúc runtime qua CPUID. Workload `tg128` (decode) bị chặn bởi **memory bandwidth** chứ không phải instruction throughput, nên lợi thế của AVX2 compile-time bị giới hạn. Runtime dispatch của prebuilt chọn đúng kernel AVX2 lúc chạy + các tối ưu linker/Release → nhanh hơn cả native build.

**Kết luận**: Trên CPU có AVX2, build native cho +5% so với generic baseline. Nhưng prebuilt binary với runtime dispatch vẫn thắng nhờ chọn kernel tối ưu lúc runtime + build Release tối ưu. "Compile for your CPU" không luôn thắng prebuilt có runtime dispatch — workload bandwidth-bound thì instruction extension không phải bottleneck chính.