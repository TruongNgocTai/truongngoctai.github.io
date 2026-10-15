---
slug: trien-khai-ai-local-rag-doanh-nghiep
title: Hướng dẫn triển khai Hệ thống AI Local & RAG nội bộ cho doanh nghiệp với vLLM và Qdrant
date: 2026-10-15
display_date: 15/10/2026
category: ai-local
category_label: AI & Local LLM
read_time: 8 phút đọc
tags: vLLM, Qdrant, PrivateRAG, OnPremiseAI
description: Kiến trúc chi tiết giúp doanh nghiệp xây dựng hệ thống hỏi đáp tài liệu nội bộ (Private RAG) kết hợp Hybrid Search (Dense + BM25), Reranker và vLLM chạy hoàn toàn trong mạng LAN không cần Internet.
---

Trong bối cảnh trí tuệ nhân tạo tạo sinh (Generative AI) bùng nổ, bài toán lớn nhất khiến các doanh nghiệp tài chính, sản xuất, y tế và pháp lý e ngại khi sử dụng các API đám mây (như OpenAI, Claude hay Gemini) chính là **quyền riêng tư và bảo mật dữ liệu nội bộ**. Không một tổ chức nào muốn tải hợp đồng thương mại, báo cáo tài chính hay mã nguồn độc quyền lên máy chủ bên thứ ba.

Đó là lý do **Hệ thống AI Local kết hợp Private RAG (Retrieval-Augmented Generation)** trở thành kiến trúc tiêu chuẩn cho doanh nghiệp hiện đại. Bài viết này chia sẻ kiến trúc thực chiến để triển khai hệ thống RAG nội bộ đạt độ chính xác cao và độ trễ thấp.

## 1. Kiến trúc tổng thể của Hệ thống Private RAG Doanh nghiệp

Một hệ thống RAG cấp độ Production không chỉ đơn thuần là cắt văn bản (chunking) và nhúng vào Vector Database. Để trả lời chính xác các văn bản pháp규, SOP kỹ thuật và bảng biểu phức tạp bằng tiếng Việt, hệ thống cần 5 thành phần cốt lõi chạy hoàn toàn trong mạng nội bộ (On-Premise / Private LAN):

1. **Document Ingestion & Layout Parser**: Bóc tách cấu trúc PDF, Word, Excel giữ nguyên ngữ cảnh bảng biểu và tiêu đề mục (sử dụng Docling hoặc Unstructured).
2. **Embedding & Reranking Local**: Sử dụng mô hình đa ngôn ngữ mạnh cho tiếng Việt như `BAAI/bge-m3` (hỗ trợ cả Dense Vector lẫn Sparse/Lexical Vector) kết hợp `bge-reranker-v2-m3`.
3. **Vector Database (Qdrant)**: Lưu trữ vector kèm bộ lọc phân quyền truy cập theo phòng ban (Role-Based Access Control metadata filtering).
4. **High-Throughput LLM Engine (vLLM)**: Phục vụ các mô hình mã nguồn mở hàng đầu như `Qwen2.5-14B/32B-Instruct` hoặc `Llama-3.1` với kỹ thuật PagedAttention.
5. **Enterprise Web Gateway**: Giao diện hỏi đáp kèm trích dẫn trang tài liệu gốc và kiểm soát nhật ký truy vấn (Audit Log).

## 2. Triển khai vLLM và Qdrant bằng Docker Compose

Dưới đây là cấu hình `docker-compose.yml` mẫu để khởi chạy cụm **Qdrant** và **vLLM** trên máy chủ Linux có trang bị GPU NVIDIA:

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: enterprise-qdrant
    restart: always
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage

  vllm-engine:
    image: vllm/vllm-openai:latest
    container_name: enterprise-vllm
    restart: always
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    ports:
      - "8000:8000"
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    command: >
      --model Qwen/Qwen2.5-14B-Instruct-AWQ
      --quantization awq
      --max-model-len 16384
      --gpu-memory-utilization 0.88
      --served-model-name local-enterprise-llm
```

> **Lưu ý thực tế:** Khi vận hành hoàn toàn Offline (Air-gapped), bạn chỉ cần tải trước trọng số mô hình (Model Weights) vào thư mục cục bộ và mount trực tiếp vào container cùng biến môi trường `HF_HUB_OFFLINE=1`.

## 3. Bí quyết tăng độ chính xác cho tiếng Việt với Hybrid Search + Reranker

Nhiều hệ thống RAG thử nghiệm thất bại vì chỉ dùng tìm kiếm tương đồng ngữ nghĩa (Dense Vector Search). Khi người dùng tìm kiếm mã hợp đồng cụ thể như `HD-2026-089` hoặc mã linh kiện kỹ thuật, Dense Vector thường bỏ sót từ khóa chính xác.

Giải pháp là kết hợp:
- **Dense Retrieval** (hiểu ngữ nghĩa câu hỏi) + **Sparse/BM25 Retrieval** (khớp chính xác mã số, tên riêng, thuật ngữ viết tắt).
- Sau khi lấy ra Top-25 đoạn văn bản từ Qdrant, đưa qua bước **Cross-Encoder Reranker** (`bge-reranker-v2-m3`) để chấm điểm lại và chọn ra Top-5 đoạn liên quan nhất đưa vào Prompt của LLM.
- Thiết lập System Prompt yêu cầu mô hình **chỉ trả lời dựa trên ngữ cảnh được cung cấp** và đính kèm tên file, số trang tham chiếu để triệt tiêu hiện tượng ảo giác (Hallucination).

## 4. Phân quyền tài liệu (RBAC) ngay từ tầng Vector Database

Trong doanh nghiệp, nhân viên phòng Kinh doanh không được phép truy vấn tài liệu lương thưởng của phòng Nhân sự. Thay vì lọc sau khi LLM đã sinh câu trả lời, mỗi đoạn văn bản (chunk) khi đưa vào Qdrant cần gắn nhãn `allowed_roles`:

```python
from qdrant_client.models import Filter, FieldCondition, MatchAny

search_filter = Filter(
    must=[
        FieldCondition(
            key="allowed_roles",
            match=MatchAny(any=current_user.roles)
        )
    ]
)
```

Nhờ cơ chế tiền lọc (Pre-filtering) ngay trên chỉ mục HNSW của Qdrant, dữ liệu nhạy cảm được cách ly tuyệt đối ở cấp độ truy vấn cơ sở dữ liệu.
