#!/usr/bin/env python3
"""
Static Blog & SEO Generator for truongngoctai.github.io
Converts Markdown files in `_posts/*.md` into standalone SEO-optimized HTML pages in `posts/*.html`,
and updates `sitemap.xml`, `robots.txt`, `.nojekyll`, and `llms.txt`.
Zero external dependencies required (runs on standard Python 3).
"""

import html
import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
POSTS_SRC_DIR = ROOT_DIR / "_posts"
POSTS_OUT_DIR = ROOT_DIR / "posts"
SITE_URL = "https://truongngoctai.github.io"


def parse_frontmatter(raw_text: str):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_text, re.DOTALL)
    if not match:
        return {}, raw_text
    fm_block, body = match.group(1), match.group(2)
    meta = {}
    for line in fm_block.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip()
    return meta, body.strip()


def format_inline(text: str) -> str:
    # Escape HTML first except we'll handle code/bold/italic
    escaped = html.escape(text)
    # Inline code `...`
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    # Bold **...**
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    # Italic *...*
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def markdown_to_html(md_text: str) -> str:
    lines = md_text.splitlines()
    html_parts = []
    in_code = False
    code_Lines = []
    in_ul = False
    in_ol = False
    in_table = False
    table_rows = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            html_parts.append("</ul>")
            in_ul = False
        if in_ol:
            html_parts.append("</ol>")
            in_ol = False

    def close_table():
        nonlocal in_table, table_rows
        if in_table and table_rows:
            html_parts.append('<table class="comparison-table" style="margin: 1.5rem 0;">')
            for idx, row in enumerate(table_rows):
                cells = [c.strip() for c in row.strip("|").split("|")]
                if idx == 0:
                    html_parts.append("<thead><tr>" + "".join(f"<th>{format_inline(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                elif idx == 1 and all(set(c) <= set(":-") for c in cells):
                    continue
                else:
                    html_parts.append("<tr>" + "".join(f"<td>{format_inline(c)}</td>" for c in cells) + "</tr>")
            html_parts.append("</tbody></table>")
        in_table = False
        table_rows = []

    for line in lines:
        if line.strip().startswith("```"):
            close_lists()
            close_table()
            if not in_code:
                in_code = True
                code_Lines = []
            else:
                in_code = False
                html_parts.append("<pre><code>" + html.escape("\n".join(code_Lines)) + "</code></pre>")
            continue

        if in_code:
            code_Lines.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            close_lists()
            close_table()
            continue

        # Table detection
        if stripped.startswith("|") and stripped.endswith("|"):
            close_lists()
            in_table = True
            table_rows.append(stripped)
            continue
        else:
            close_table()

        # Headings
        if stripped.startswith("### "):
            close_lists()
            html_parts.append(f"<h3>{format_inline(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            close_lists()
            html_parts.append(f"<h2>{format_inline(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            close_lists()
            html_parts.append(f"<h1>{format_inline(stripped[2:])}</h1>")
        elif stripped.startswith("> "):
            close_lists()
            html_parts.append(f"<blockquote><p style='margin:0'>{format_inline(stripped[2:])}</p></blockquote>")
        elif stripped.startswith("- "):
            if in_ol:
                html_parts.append("</ol>")
                in_ol = False
            if not in_ul:
                html_parts.append("<ul>")
                in_ul = True
            html_parts.append(f"<li>{format_inline(stripped[2:])}</li>")
        elif re.match(r"^\d+\.\s+", stripped):
            if in_ul:
                html_parts.append("</ul>")
                in_ul = False
            if not in_ol:
                html_parts.append("<ol>")
                in_ol = True
            item_text = re.sub(r"^\d+\.\s+", "", stripped)
            html_parts.append(f"<li>{format_inline(item_text)}</li>")
        else:
            close_lists()
            html_parts.append(f"<p>{format_inline(stripped)}</p>")

    close_lists()
    close_table()
    return "\n".join(html_parts)


def render_post_page(meta: dict, body_html: str) -> str:
    title = meta.get("title", "Bài viết kỹ thuật")
    slug = meta.get("slug", "post")
    date_iso = meta.get("date", "2026-10-15")
    display_date = meta.get("display_date", date_iso)
    category_label = meta.get("category_label", "CNTT & AI")
    read_time = meta.get("read_time", "7 phút đọc")
    description = meta.get("description", "")
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    tags_html = "".join(f'<span class="pill">#{html.escape(t)}</span>' for t in tags)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)} | Trương Ngọc Tài Blog</title>
  <meta name="description" content="{html.escape(description)}" />
  <meta name="author" content="Trương Ngọc Tài" />
  <link rel="canonical" href="{SITE_URL}/posts/{slug}.html" />

  <!-- Open Graph -->
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{SITE_URL}/posts/{slug}.html" />
  <meta property="og:title" content="{html.escape(title)}" />
  <meta property="og:description" content="{html.escape(description)}" />

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet" />

  <link rel="stylesheet" href="../assets/css/style.css" />

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{html.escape(title)}",
    "description": "{html.escape(description)}",
    "datePublished": "{date_iso}",
    "author": {{
      "@type": "Person",
      "name": "Trương Ngọc Tài",
      "url": "{SITE_URL}/"
    }},
    "mainEntityOfPage": "{SITE_URL}/posts/{slug}.html"
  }}
  </script>
</head>
<body>

  <header class="site-header">
    <div class="container nav-wrapper">
      <a href="../index.html" class="brand-logo">
        <div class="brand-badge">TNT</div>
        <div>
          <span>Trương Ngọc Tài</span>
          <span class="brand-sub">Web Systems &bull; Private Local AI</span>
        </div>
      </a>

      <nav class="nav-links" aria-label="Điều hướng">
        <a href="../index.html#dich-vu">Dịch vụ</a>
        <a href="../index.html#ai-local">Giải pháp AI Local</a>
        <a href="../index.html#blog" class="active">Blog CNTT &amp; AI</a>
        <a href="../index.html#lien-he">Liên hệ</a>
      </nav>

      <div class="nav-actions">
        <button id="theme-toggle" class="theme-toggle" aria-label="Chuyển chế độ Sáng/Tối">☀️</button>
        <a href="../index.html#lien-he" class="btn btn-primary">Tư vấn Dự án</a>
      </div>
    </div>
  </header>

  <main class="article-container">
    <a href="../index.html#blog" class="read-more" style="margin-bottom: 1.5rem; display: inline-flex;">&larr; Quay lại danh sách bài viết</a>

    <article>
      <header class="article-header">
        <div class="post-meta">
          <span class="post-category">{html.escape(category_label)}</span>
          <span>{html.escape(display_date)}</span>
          <span>&bull; {html.escape(read_time)}</span>
        </div>
        <h1>{html.escape(title)}</h1>
        <p style="color: var(--text-secondary); font-size: 1.08rem;">{html.escape(description)}</p>
        <div class="tech-stack-pills" style="border: none; padding-top: 0.75rem;">
          {tags_html}
        </div>
      </header>

      <div class="article-content">
        {body_html}
      </div>
    </article>

    <!-- Call to Action Box inside Post -->
    <div class="panel-card" style="margin-top: 3.5rem; background: var(--gradient-surface);">
      <h3>Bạn cần tư vấn triển khai Hệ thống Web hoặc AI Local cho doanh nghiệp?</h3>
      <p style="color: var(--text-secondary); margin: 0.5rem 0 1.25rem;">
        Tôi cung cấp dịch vụ thiết kế kiến trúc, phát triển hệ thống phần mềm Web theo yêu cầu và triển khai giải pháp Private LLM / RAG chạy nội bộ bảo mật dữ liệu 100%.
      </p>
      <div style="display: flex; flex-wrap: wrap; gap: 0.85rem;">
        <a href="../index.html#lien-he" class="btn btn-primary">Nhận tư vấn Kiến trúc &amp; Báo giá &rarr;</a>
        <a href="../index.html#ai-local" class="btn btn-outline">Thử công cụ tính cấu hình GPU</a>
      </div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        <strong>Trương Ngọc Tài</strong> &mdash; Blog CNTT, AI &amp; Dịch vụ Phát triển Hệ thống Web, AI Local.
      </div>
      <div style="display: flex; gap: 1.25rem;">
        <a href="../index.html">Trang chủ</a>
        <a href="../index.html#dich-vu">Dịch vụ</a>
        <a href="../index.html#lien-he">Liên hệ</a>
      </div>
    </div>
  </footer>

  <script src="../assets/js/main.js"></script>
</body>
</html>
"""


def main():
    POSTS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    posts_meta = []

    for md_file in sorted(POSTS_SRC_DIR.glob("*.md"), reverse=True):
        raw = md_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        if "slug" not in meta:
            meta["slug"] = md_file.stem
        body_html = markdown_to_html(body)
        full_html = render_post_page(meta, body_html)
        out_path = POSTS_OUT_DIR / f"{meta['slug']}.html"
        out_path.write_text(full_html, encoding="utf-8")
        posts_meta.append(meta)
        print(f"[OK] Built {out_path.relative_to(ROOT_DIR)}")

    # Create .nojekyll
    (ROOT_DIR / ".nojekyll").write_text("", encoding="utf-8")

    # Create robots.txt
    robots_txt = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    (ROOT_DIR / "robots.txt").write_text(robots_txt, encoding="utf-8")

    # Create sitemap.xml
    urls = [f"  <url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>"]
    for m in posts_meta:
        urls.append(
            f"  <url><loc>{SITE_URL}/posts/{m['slug']}.html</loc><lastmod>{m.get('date', '2026-10-15')}</lastmod><priority>0.8</priority></url>"
        )
    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (ROOT_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

    # Create llms.txt for AI Search Engines (AEO / GEO)
    llms_lines = [
        "# Trương Ngọc Tài — Blog CNTT, AI & Giải pháp Hệ thống Web, AI Local",
        "",
        "> Chuyên trang chia sẻ kiến thức Công nghệ thông tin, Kiến trúc Hệ thống Web, AI ứng dụng và cung cấp dịch vụ phát triển Hệ thống Web theo yêu cầu, triển khai AI Local (Private LLM / RAG nội bộ) cho doanh nghiệp.",
        "",
        "## Dịch vụ cung cấp",
        "- Phát triển Hệ thống Web & Phần mềm quản trị doanh nghiệp (ERP, CRM, CMS, Portal, API/Microservices).",
        "- Triển khai Hệ thống AI Local & Private RAG (vLLM, Ollama, Qdrant, Hybrid Search, On-Premise LLM bảo mật dữ liệu 100%).",
        "- Tích hợp AI Agents, Tự động hóa quy trình nghiệp vụ (OCR chứng từ, Function Calling, MCP) & Tư vấn hạ tầng GPU Server.",
        "",
        "## Bài viết Kỹ thuật (Blog)",
    ]
    for m in posts_meta:
        llms_lines.append(f"- [{m.get('title')}]({SITE_URL}/posts/{m['slug']}.html): {m.get('description', '')}")
    llms_lines.extend([
        "",
        "## Liên hệ",
        "- Website: https://truongngoctai.github.io/",
        "- Email: truongngoctai.it.hcmus@gmail.com",
        "- GitHub: https://github.com/TruongNgocTai",
    ])
    (ROOT_DIR / "llms.txt").write_text("\n".join(llms_lines) + "\n", encoding="utf-8")
    print("[OK] Generated .nojekyll, robots.txt, sitemap.xml, and llms.txt")


if __name__ == "__main__":
    main()
