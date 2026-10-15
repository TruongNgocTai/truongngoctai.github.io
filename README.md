# truongngoctai.github.io — Blog CNTT, AI & Dịch vụ Phát triển Hệ thống Web, AI Local

Website cá nhân & Blog kỹ thuật của **Trương Ngọc Tài**, chia sẻ kiến thức chuyên sâu về:
- **Công nghệ thông tin & Kiến trúc Hệ thống Web**: Modular Monolith, Microservices, PostgreSQL, Redis, Bảo mật & Tối ưu hiệu năng.
- **Trí tuệ nhân tạo & AI Local (On-Premise LLM)**: Triển khai vLLM, Ollama, Qdrant Vector DB, Private RAG nội bộ, Lượng tử hóa GPU (AWQ/GGUF/FP8) và AI Agents.
- **Dịch vụ Công nghệ**:
  1. Phát triển Hệ thống Web & Phần mềm quản trị theo yêu cầu (ERP, CRM, CMS, Dashboard, API).
  2. Triển khai Hệ thống AI Local & Private RAG bảo mật dữ liệu 100% cho doanh nghiệp.
  3. Tích hợp AI Agent tự động hóa quy trình nghiệp vụ & Tư vấn hạ tầng GPU Server.

---

## Cấu trúc thư mục

```text
truongngoctai.github.io/
├── index.html                  # Trang chủ (Hero, Dịch vụ, Công cụ tính VRAM AI Local, Blog, Liên hệ)
├── assets/
│   ├── css/style.css           # Giao diện Dark/Light mode hiện đại, responsive
│   └── js/main.js              # Tìm kiếm/lọc bài viết, công cụ tính cấu hình GPU, xử lý form
├── _posts/                     # Nguồn bài viết định dạng Markdown (.md)
├── posts/                      # Các trang bài viết HTML chuẩn SEO được sinh tự động
├── scripts/
│   └── build_blog.py           # Script biên dịch Markdown -> HTML, cập nhật sitemap.xml & llms.txt
├── llms.txt                    # Chuẩn tối ưu hiển thị cho các công cụ tìm kiếm AI (AEO/GEO)
├── sitemap.xml                 # Sitemap chuẩn Google SEO
├── robots.txt                  # Cấu hình thu thập dữ liệu tìm kiếm
└── .nojekyll                   # Đảm bảo GitHub Pages phục vụ file tĩnh tức thì
```

## Cách thêm bài viết Blog mới

1. Tạo file Markdown mới trong thư mục `_posts/ten-bai-viet.md` với phần khai báo đầu trang (Frontmatter):
   ```markdown
   ---
   slug: ten-bai-viet
   title: Tiêu đề bài viết của bạn
   date: 2026-10-20
   display_date: 20/10/2026
   category: ai-local
   category_label: AI & Local LLM
   read_time: 7 phút đọc
   tags: AI, LocalLLM, WebSystem
   description: Tóm tắt ngắn gọn nội dung bài viết chuẩn SEO.
   ---

   Nội dung bài viết bằng Markdown...
   ```
2. Chạy lệnh biên dịch:
   ```bash
   python3 scripts/build_blog.py
   ```
3. Xem thử tại máy local:
   ```bash
   python3 -m http.server 8080
   ```

## Triển khai lên GitHub Pages

1. Tạo repository công khai có tên **`truongngoctai.github.io`** trên tài khoản GitHub `TruongNgocTai`.
2. Đẩy mã nguồn lên nhánh `main`:
   ```bash
   git remote add origin git@github.com:TruongNgocTai/truongngoctai.github.io.git
   git push -u origin main
   ```
3. Truy cập **Settings → Pages** trên GitHub, chọn **Source: Deploy from a branch (`main` / `root`)** và truy cập `https://truongngoctai.github.io`.
