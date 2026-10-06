# Bonus B1 - Prebuilt vs source build

Host `Linux-x86_64` · CPU `13th Gen Intel(R) Core(TM) i9-13900H`
Vector extensions detected: AVX2
llama.cpp `b10488` both sides · `threads=2` ·
**both pinned to `ngl=0`** so this isolates the compiler ·
metric `tg128`, 3 repetitions

| Binary | Built for | tg128 (tok/s) | Relative |
|:--|--:|--:|--:|
| prebuilt release | runtime CPU dispatch | 19.1 | 1.00x |
| your source build | this CPU (`-DGGML_NATIVE=ON`) | 18.8 | 0.98x |

On this machine, **they are within 3% -- no meaningful difference**.

before: 19.1 tok/s (prebuilt release)
after:  18.8 tok/s (source build, -DGGML_NATIVE=ON)
speedup: 0.98x

Same source revision, same model, same backend, same `-ngl` -- the only difference
is what the compiler was allowed to assume about the CPU.
A gap this small usually means the prebuilt binary already dispatches to the right kernels at runtime (releases ship one libggml-cpu-*.so per microarchitecture and pick via CPUID), or that this workload is bandwidth-bound rather than instruction-bound. Both are real findings -- say which one you think it is.


## Your explanation

Prebuilt binary (19.1 tok/s) vs source build native (18.8 tok/s) — chênh lệch 3%, không có ý nghĩa. CPU i9-13900H hỗ trợ AVX2 (không có AVX-512). Prebuilt binary dùng **runtime CPU dispatch**: nó ship sẵn nhiều libggml-cpu-*.so cho từng microarchitecture (haswell, skylake, skylakex, zen4, v.v.) và chọn đúng kernel lúc chạy thông qua CPUID. Workload `tg128` (decode) bị chặn bởi **memory bandwidth** chứ không phải instruction throughput, nên việc compile tối ưu cho AVX2 native không mang lại lợi thế. Prebuilt binary chọn đúng kernel AVX2 lúc runtime → hiệu năng ngang ngang build native. Finding này đúng kỳ vọng: decode bị bandwidth-bound, không phải compute-bound.
