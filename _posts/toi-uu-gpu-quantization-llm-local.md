---
slug: toi-uu-gpu-quantization-llm-local
title: Tối ưu phần cứng GPU & Lượng tử hóa (AWQ, GGUF, FP8) khi vận hành LLM Local
date: 2026-10-08
display_date: 08/10/2026
category: devops-security
category_label: Tối ưu GPU & Bảo mật
read_time: 9 phút đọc
tags: Quantization, GPU, VRAM, Inference
description: Giải mã các chuẩn lượng tử hóa mô hình ngôn ngữ lớn: Sự khác biệt giữa GGUF, AWQ, GPTQ và FP8. Cách tính toán KV Cache, PagedAttention và tối ưu thông lượng phục vụ nhiều người dùng đồng thời.
---

Khi doanh nghiệp bắt tay vào xây dựng máy chủ **AI Local (On-Premise LLM)**, câu hỏi đầu tiên luôn là: *"Cần bao nhiêu GB VRAM để chạy mô hình 14B, 32B hay 70B cho 20 nhân sự sử dụng cùng lúc?"*. Nếu tính toán sai, hệ thống sẽ liên tục gặp lỗi tràn bộ nhớ (`CUDA Out of Memory`) hoặc tốc độ phản hồi quá chậm không thể đưa vào thực tế.

Bài viết này cung cấp công thức tính toán chính xác và hướng dẫn chọn chuẩn lượng tử hóa (Quantization) phù hợp nhất cho từng kịch bản phần cứng.

## 1. Công thức tính dung lượng VRAM thực tế cho LLM

Tổng bộ nhớ GPU (VRAM) tiêu thụ khi vận hành một mô hình ngôn ngữ lớn gồm 3 phần chính:

$$\text{Tổng VRAM} = \text{Model Weights} + \text{KV Cache (Ngữ cảnh)} + \text{CUDA Overhead (1.2 - 2 GB)}$$

Trong đó:
- **Ở định dạng gốc FP16/BF16**: Mỗi 1 tỷ tham số (1B) cần khoảng **2 GB VRAM**. Ví dụ mô hình `32B` ở chuẩn FP16 cần tới ~64 GB VRAM chỉ riêng cho trọng số.
- **Ở định dạng lượng tử hóa 4-bit (INT4 / AWQ / GGUF Q4_K_M)**: Mỗi 1 tỷ tham số chỉ cần khoảng **0.55 – 0.65 GB VRAM**, trong khi vẫn giữ được **98% – 99% chất lượng suy luận** so với bản gốc. Như vậy, mô hình `32B-AWQ` chỉ tốn ~19 GB VRAM trọng số, hoàn toàn chạy mượt trên 1 card **RTX 4090 (24GB)** hoặc **2x RTX 4090 / 1x L40S (48GB)** khi mở rộng KV Cache dài.

## 2. Khi nào chọn GGUF (Llama.cpp/Ollama) và khi nào chọn AWQ/FP8 (vLLM)?

| Chuẩn lượng tử hóa | Engine tối ưu | Ưu điểm nổi bật | Kịch bản khuyên dùng |
| :--- | :--- | :--- | :--- |
| **GGUF (`Q4_K_M`, `Q8_0`)** | Ollama, Llama.cpp | Hỗ trợ chạy kết hợp CPU + GPU (Offloading) và Apple Silicon Unified Memory. | Máy trạm cá nhân, PoC nhanh, số người dùng đồng thời thấp (1–5 users). |
| **AWQ (4-bit Activation-aware)** | vLLM, SGLang, TensorRT-LLM | Giữ nguyên độ chính xác các trọng số quan trọng, thông lượng Continuous Batching cực cao. | Hệ thống Production cho doanh nghiệp chạy trên GPU NVIDIA chuyên dụng. |
| **FP8 (8-bit Floating Point)** | vLLM, TensorRT-LLM | Hỗ trợ phần cứng gốc trên kiến trúc Ada Lovelace (RTX 4090, L40S) & Hopper (H100). | Bài toán yêu cầu độ chính xác cao nhất và tốc độ xử lý đồng thời lớn. |

## 3. Tối ưu KV Cache và PagedAttention cho đa người dùng

Khi nhiều nhân viên cùng gửi tài liệu dài (ví dụ 16.000 tokens) vào hệ thống RAG, bộ nhớ **KV Cache** sẽ phình to rất nhanh. Để tránh lãng phí VRAM:

1. Sử dụng **vLLM** hoặc **SGLang** với cơ chế **PagedAttention** và **Automatic Prefix Caching** (`--enable-prefix-caching`): Giúp tái sử dụng bộ nhớ đệm của System Prompt và tài liệu chung giữa nhiều lượt hỏi, giảm thời gian phản hồi từ đầu tiên (TTFT) tới 70%.
2. Bật tùy chọn `--kv-cache-dtype fp8` trên các dòng GPU kiến trúc mới để tăng gấp đôi dung lượng ngữ cảnh tối đa trên cùng một lượng VRAM.
