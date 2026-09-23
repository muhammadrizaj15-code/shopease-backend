/* =========================================================
   ShopEase — Global JavaScript (Premium UI)
   ========================================================= */
document.addEventListener('DOMContentLoaded', function () {

    // ===================== AOS scroll animations =====================
    if (window.AOS) {
        AOS.init({ duration: 700, once: true, offset: 60 });
    }

    // ===================== Toast notifications (from Django messages) =====================
    document.querySelectorAll('.toast').forEach(function (toastEl) {
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    });

    // ===================== Dark Mode Toggle (persisted via localStorage) =====================
    const root = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');

    function applyTheme(theme) {
        root.setAttribute('data-bs-theme', theme);
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
        }
    }
    const savedTheme = localStorage.getItem('shopease-theme') || 'light';
    applyTheme(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const current = root.getAttribute('data-bs-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            applyTheme(next);
            localStorage.setItem('shopease-theme', next);
        });
    }

    // ===================== Quantity Selector (Product Detail) =====================
    const qtyInput = document.getElementById('qtyInput');
    const qtyIncrease = document.getElementById('qtyIncrease');
    const qtyDecrease = document.getElementById('qtyDecrease');

    if (qtyInput && qtyIncrease && qtyDecrease) {
        qtyIncrease.addEventListener('click', function () {
            const max = parseInt(qtyInput.getAttribute('max') || 999);
            let val = parseInt(qtyInput.value) || 1;
            if (val < max) qtyInput.value = val + 1;
        });
        qtyDecrease.addEventListener('click', function () {
            let val = parseInt(qtyInput.value) || 1;
            if (val > 1) qtyInput.value = val - 1;
        });
    }

    // ===================== Cart Quantity Auto-submit =====================
    document.querySelectorAll('.cart-qty-form select, .cart-qty-form input[type="number"]').forEach(function (el) {
        el.addEventListener('change', function () {
            el.closest('form').submit();
        });
    });

    // ===================== Product Image Gallery (thumbnail swap) =====================
    document.querySelectorAll('.thumbnail-img').forEach(function (thumb) {
        thumb.addEventListener('click', function () {
            const mainImg = document.getElementById('mainProductImage');
            if (mainImg) mainImg.src = thumb.getAttribute('data-full');
            document.querySelectorAll('.thumbnail-img').forEach(t => t.classList.remove('border-primary'));
            thumb.classList.add('border-primary');
        });
    });

    // ===================== Image Zoom on Product Detail =====================
    const zoomImg = document.getElementById('mainProductImage');
    if (zoomImg) {
        zoomImg.addEventListener('mousemove', function (e) {
            const rect = zoomImg.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            zoomImg.style.transformOrigin = `${x}% ${y}%`;
        });
        zoomImg.addEventListener('mouseenter', function () { zoomImg.style.transform = 'scale(1.6)'; });
        zoomImg.addEventListener('mouseleave', function () { zoomImg.style.transform = 'scale(1)'; zoomImg.style.transformOrigin = 'center'; });
    }

    // ===================== Bootstrap Tooltips =====================
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));

    // ===================== Price Range Filter Sync (Products page) =====================
    const minPrice = document.getElementById('id_min_price');
    const maxPrice = document.getElementById('id_max_price');
    if (minPrice && maxPrice) {
        [minPrice, maxPrice].forEach(function (el) {
            el.addEventListener('change', function () {
                if (minPrice.value && maxPrice.value && parseFloat(minPrice.value) > parseFloat(maxPrice.value)) {
                    alert('Minimum price cannot be greater than maximum price.');
                    el.value = '';
                }
            });
        });
    }

    // ===================== Live AJAX Search =====================
    const searchInput = document.getElementById('liveSearchInput');
    const resultsBox = document.getElementById('liveSearchResults');
    let searchTimer = null;

    if (searchInput && resultsBox) {
        searchInput.addEventListener('input', function () {
            const q = searchInput.value.trim();
            clearTimeout(searchTimer);
            if (q.length < 2) {
                resultsBox.classList.add('d-none');
                resultsBox.innerHTML = '';
                return;
            }
            searchTimer = setTimeout(function () {
                fetch(`/search/live/?q=${encodeURIComponent(q)}`)
                    .then(res => res.json())
                    .then(data => {
                        if (!data.results || data.results.length === 0) {
                            resultsBox.innerHTML = '<div class="p-3 text-muted small">No products found.</div>';
                        } else {
                            resultsBox.innerHTML = data.results.map(function (p) {
                                const img = p.image ? `<img src="${p.image}" alt="">` : '';
                                return `<a href="${p.url}" class="live-search-item text-decoration-none text-dark">
                                            ${img}
                                            <div>
                                                <div class="fw-semibold small">${p.name}</div>
                                                <div class="text-muted small">${p.category} — $${p.price}</div>
                                            </div>
                                        </a>`;
                            }).join('');
                        }
                        resultsBox.classList.remove('d-none');
                    })
                    .catch(() => { resultsBox.classList.add('d-none'); });
            }, 300);
        });

        document.addEventListener('click', function (e) {
            if (!resultsBox.contains(e.target) && e.target !== searchInput) {
                resultsBox.classList.add('d-none');
            }
        });
    }

    // ===================== Flash Sale Countdown =====================
    document.querySelectorAll('.flash-countdown').forEach(function (el) {
        const endTime = new Date(el.getAttribute('data-end')).getTime();
        function tick() {
            const now = new Date().getTime();
            let diff = endTime - now;
            if (diff < 0) diff = 0;
            const d = Math.floor(diff / (1000 * 60 * 60 * 24));
            const h = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const s = Math.floor((diff % (1000 * 60)) / 1000);
            const set = (sel, val) => { const t = el.querySelector(sel); if (t) t.textContent = String(val).padStart(2, '0'); };
            set('.cd-days', d); set('.cd-hours', h); set('.cd-mins', m); set('.cd-secs', s);
        }
        tick();
        setInterval(tick, 1000);
    });

    // ===================== Mobile nav / bottom bar coordination =====================
    // Hide the fixed bottom nav while the hamburger menu is open so it never
    // covers "Products" / "Admin Dashboard" and other nav links on mobile.
    const mainNavbarEl = document.getElementById('mainNavbar');
    const bottomNavEl = document.querySelector('.mobile-bottom-nav');
    if (mainNavbarEl && bottomNavEl) {
        mainNavbarEl.addEventListener('show.bs.collapse', function () {
            bottomNavEl.classList.add('d-none');
        });
        mainNavbarEl.addEventListener('hidden.bs.collapse', function () {
            bottomNavEl.classList.remove('d-none');
        });
    }
});
