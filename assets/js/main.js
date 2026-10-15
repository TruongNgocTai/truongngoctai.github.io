document.addEventListener('DOMContentLoaded', () => {
  // 1. Theme Toggle (Dark / Light)
  const themeToggle = document.getElementById('theme-toggle');
  const rootEl = document.documentElement;
  const savedTheme = localStorage.getItem('tnt_theme') || 'dark';

  function applyTheme(theme) {
    if (theme === 'light') {
      rootEl.setAttribute('data-theme', 'light');
      if (themeToggle) themeToggle.textContent = '🌙';
    } else {
      rootEl.removeAttribute('data-theme');
      if (themeToggle) themeToggle.textContent = '☀️';
    }
    localStorage.setItem('tnt_theme', theme);
  }

  applyTheme(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = rootEl.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
      applyTheme(current === 'light' ? 'dark' : 'light');
    });
  }

  // 2. Blog Filtering & Real-time Search
  const categoryButtons = document.querySelectorAll('.tab-btn');
  const searchInput = document.getElementById('blog-search');
  const postCards = document.querySelectorAll('.post-card');
  const emptyState = document.getElementById('blog-empty-state');

  let activeCategory = 'all';
  let searchQuery = '';

  function filterPosts() {
    let visibleCount = 0;
    postCards.forEach((card) => {
      const category = card.getAttribute('data-category') || '';
      const title = (card.getAttribute('data-title') || '').toLowerCase();
      const tags = (card.getAttribute('data-tags') || '').toLowerCase();
      const excerpt = (card.querySelector('.post-excerpt')?.textContent || '').toLowerCase();

      const matchesCategory = activeCategory === 'all' || category === activeCategory;
      const matchesSearch =
        !searchQuery ||
        title.includes(searchQuery) ||
        tags.includes(searchQuery) ||
        excerpt.includes(searchQuery);

      if (matchesCategory && matchesSearch) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (emptyState) {
      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  categoryButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      categoryButtons.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      activeCategory = btn.getAttribute('data-filter') || 'all';
      filterPosts();
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.trim().toLowerCase();
      filterPosts();
    });
  }

  // 3. Interactive Local AI GPU & VRAM Calculator
  const modelSelect = document.getElementById('calc-model');
  const quantSelect = document.getElementById('calc-quant');
  const contextSelect = document.getElementById('calc-context');
  const vramOutput = document.getElementById('calc-vram-output');
  const gpuOutput = document.getElementById('calc-gpu-output');
  const speedOutput = document.getElementById('calc-speed-output');

  function updateVramCalculator() {
    if (!modelSelect || !quantSelect || !contextSelect) return;

    const paramsB = parseFloat(modelSelect.value); // 8, 14, 32, 70
    const bytesPerParam = parseFloat(quantSelect.value); // 0.6 (4-bit), 1.05 (8-bit), 2.0 (FP16)
    const contextMultiplier = parseFloat(contextSelect.value); // KV cache overhead in GB

    const weightsGB = paramsB * bytesPerParam;
    const kvCacheGB = contextMultiplier * (paramsB / 14);
    const totalVram = Math.ceil((weightsGB + kvCacheGB + 1.5) * 10) / 10;

    let recommendedHardware = '';
    let estThroughput = '';

    if (totalVram <= 12) {
      recommendedHardware = '1x RTX 4070 Ti Super (16GB) hoặc RTX 3060 (12GB)';
      estThroughput = '~65 - 95 tokens/s (vLLM / Ollama)';
    } else if (totalVram <= 22) {
      recommendedHardware = '1x NVIDIA RTX 4090 (24GB) hoặc RTX 3090 (24GB)';
      estThroughput = '~55 - 85 tokens/s (Production 5-15 users)';
    } else if (totalVram <= 46) {
      recommendedHardware = '2x RTX 4090 (48GB) hoặc 1x NVIDIA L40S / A6000 (48GB)';
      estThroughput = '~40 - 65 tokens/s (vLLM Tensor Parallelism)';
    } else if (totalVram <= 80) {
      recommendedHardware = '1x NVIDIA A100/H100 (80GB) hoặc 2x L40S (96GB)';
      estThroughput = '~35 - 60 tokens/s (Enterprise Multi-user RAG)';
    } else {
      recommendedHardware = '2x NVIDIA A100/H100 (160GB) hoặc Mac Studio M2/M3 Ultra (192GB)';
      estThroughput = '~25 - 45 tokens/s (High-capacity Cluster)';
    }

    if (vramOutput) vramOutput.textContent = `~${totalVram} GB VRAM`;
    if (gpuOutput) gpuOutput.textContent = recommendedHardware;
    if (speedOutput) speedOutput.textContent = estThroughput;
  }

  if (modelSelect && quantSelect && contextSelect) {
    modelSelect.addEventListener('change', updateVramCalculator);
    quantSelect.addEventListener('change', updateVramCalculator);
    contextSelect.addEventListener('change', updateVramCalculator);
    updateVramCalculator();
  }

  // 4. Contact Form Handler (Static Mailto + Feedback)
  const contactForm = document.getElementById('consult-form');
  const formStatus = document.getElementById('form-status');

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('client-name')?.value.trim() || '';
      const contact = document.getElementById('client-contact')?.value.trim() || '';
      const service = document.getElementById('client-service')?.value || '';
      const message = document.getElementById('client-message')?.value.trim() || '';

      const subject = encodeURIComponent(`[Tư vấn Giải pháp] ${service} - ${name}`);
      const body = encodeURIComponent(
        `Xin chào Trương Ngọc Tài,\n\n` +
        `- Họ tên / Đơn vị: ${name}\n` +
        `- Email / SĐT liên hệ: ${contact}\n` +
        `- Hạng mục quan tâm: ${service}\n\n` +
        `Nội dung chi tiết:\n${message}\n`
      );

      if (formStatus) {
        formStatus.style.display = 'block';
        formStatus.textContent = 'Đang mở ứng dụng Email với nội dung yêu cầu tư vấn... Bạn cũng có thể gửi trực tiếp tới truongngoctai.it.hcmus@gmail.com.';
      }

      window.location.href = `mailto:truongngoctai.it.hcmus@gmail.com?subject=${subject}&body=${body}`;
    });
  }
});
