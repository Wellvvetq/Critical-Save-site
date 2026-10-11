document.addEventListener("DOMContentLoaded", () => {
  // 1. Critical Noir Theme Manager (Dark / Light / System)
  const themeToggle = document.getElementById("theme-toggle");
  const themeToggleIcon = document.querySelector(".theme-toggle-icon");
  const themeSelectButtons = document.querySelectorAll(".btn-theme-select");

  const getSystemTheme = () => (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");

  const applyTheme = (themeName) => {
    let resolvedTheme = themeName;
    if (themeName === "system") {
      resolvedTheme = getSystemTheme();
      localStorage.removeItem("cs_theme");
    } else {
      localStorage.setItem("cs_theme", themeName);
    }

    document.documentElement.setAttribute("data-theme", resolvedTheme);
    if (themeToggleIcon) {
      themeToggleIcon.textContent = resolvedTheme === "light" ? "☀️" : "🌙";
    }

    // Update active state on footer selector buttons
    themeSelectButtons.forEach(btn => {
      const btnTheme = btn.getAttribute("data-theme-val");
      const currentStored = localStorage.getItem("cs_theme") || "system";
      if (btnTheme === currentStored) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });
  };

  // Initial Theme Synchronization
  const storedTheme = localStorage.getItem("cs_theme") || "dark";
  applyTheme(storedTheme);

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
    });
  }

  themeSelectButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTheme = btn.getAttribute("data-theme-val");
      applyTheme(targetTheme);
    });
  });

  // Listen to system preference changes if in system mode
  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: light)").addEventListener("change", () => {
      if (!localStorage.getItem("cs_theme")) {
        applyTheme("system");
      }
    });
  }

  // 2. Mobile Menu Toggle & Keyboard Accessibility
  const toggleBtn = document.querySelector(".mobile-nav-toggle");
  const navLinks = document.querySelector(".nav-links");
  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener("click", () => {
      const isExpanded = toggleBtn.getAttribute("aria-expanded") === "true";
      toggleBtn.setAttribute("aria-expanded", !isExpanded);
      navLinks.classList.toggle("open");
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && navLinks.classList.contains("open")) {
        navLinks.classList.remove("open");
        toggleBtn.setAttribute("aria-expanded", "false");
        toggleBtn.focus();
      }
    });
  }

  // 3. SHA-256 Copy Checksum Action
  const copyButtons = document.querySelectorAll(".btn-copy-hash");
  copyButtons.forEach(btn => {
    btn.addEventListener("click", async () => {
      const hash = btn.getAttribute("data-hash");
      if (!hash) return;
      try {
        await navigator.clipboard.writeText(hash);
        const originalText = btn.innerHTML;
        btn.innerHTML = "✓ Copied!";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.innerHTML = originalText;
          btn.classList.remove("copied");
        }, 2200);
      } catch (err) {
        // Fallback for browsers with restricted clipboard permission
        const tempInput = document.createElement("input");
        tempInput.value = hash;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand("copy");
        document.body.removeChild(tempInput);
        btn.innerHTML = "✓ Copied!";
        setTimeout(() => {
          btn.innerHTML = "📋 Copy SHA-256";
        }, 2200);
      }
    });
  });

  // 4. Scroll-triggered reveal animations using IntersectionObserver
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
          observer.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: "0px 0px -40px 0px",
      threshold: 0.08
    });

    const revealElements = document.querySelectorAll(
      ".section-header, .section-editorial-header, .game-card, .article-card, .pillar-item, .career-item, " +
      ".flagship-showcase-card, .secondary-project-card, .catalog-lead-showcase, .catalog-dossier-card, " +
      ".axiom-card, .about-pillar-card, .journal-lead-card, .journal-stack-item, .journal-ledger-row, " +
      ".station-role-card, .terminal-console-panel, .dossier-terminal-box, .collaboration-terminal-card, " +
      ".fwr-feature-card, .fwr-gallery-item, .download-edition-card, .product-spotlight-card, .catalog-product-showcase"
    );
    revealElements.forEach(el => {
      el.classList.add("reveal-on-scroll");
      observer.observe(el);
    });
  }

  // 5. Accessible Lightbox Functionality for Gallery & Screenshots
  const galleryThumbs = document.querySelectorAll(".gallery-thumb");
  const modal = document.getElementById("lightbox-modal");
  const modalImg = document.getElementById("lightbox-img");
  const closeBtn = document.getElementById("lightbox-close");

  if (galleryThumbs.length > 0 && modal && modalImg) {
    galleryThumbs.forEach(thumb => {
      const openModal = () => {
        const fullSrc = thumb.getAttribute("data-full");
        const altText = thumb.querySelector("img")?.alt || "Enlarged Capture";
        if (fullSrc) {
          modalImg.src = fullSrc;
          modalImg.alt = altText;
          modal.classList.add("active");
          modal.setAttribute("aria-hidden", "false");
          closeBtn?.focus();
        }
      };

      thumb.addEventListener("click", openModal);
      thumb.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openModal();
        }
      });
    });

    const closeModal = () => {
      modal.classList.remove("active");
      modal.setAttribute("aria-hidden", "true");
    };

    closeBtn?.addEventListener("click", closeModal);
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.classList.contains("active")) {
        closeModal();
      }
    });
  }

  // 6. Homepage Hero Featured Project Floating Widget Cycling
  const heroFeatureCard = document.querySelector(".hero-noir-feature-card");
  if (heroFeatureCard) {
    const isRu = document.documentElement.lang === "ru" || window.location.pathname.startsWith("/ru");
    const featuredProjects = [
      {
        idx: "01 / 03",
        name: "Aegis Decay",
        sub: isRu ? "Научно-фантастическое выживание" : "Sci-fi narrative survival",
        slug: "project-aegis-decay"
      },
      {
        idx: "02 / 03",
        name: "Hollow Meridian",
        sub: isRu ? "Расследование и кинематографичная тайна" : "Investigative mystery & cinematic puzzle",
        slug: "hollow-meridian"
      },
      {
        idx: "03 / 03",
        name: "Project Aurora",
        sub: isRu ? "Сюрреалистический нарративный триллер" : "Surrealistic narrative thriller",
        slug: "project-aurora"
      }
    ];

    let currentIdx = 0;
    const indexEl = heroFeatureCard.querySelector(".feature-card-index");
    const nameEl = heroFeatureCard.querySelector(".feature-card-name");
    const subEl = heroFeatureCard.querySelector(".feature-card-sub");
    const prevBtn = heroFeatureCard.querySelector(".nav-arrow.prev");
    const nextBtn = heroFeatureCard.querySelector(".nav-arrow.next");

    const updateCard = (newIdx) => {
      currentIdx = (newIdx + featuredProjects.length) % featuredProjects.length;
      const proj = featuredProjects[currentIdx];
      if (indexEl) indexEl.textContent = proj.idx;
      if (nameEl) nameEl.textContent = proj.name;
      if (subEl) subEl.textContent = proj.sub;
    };

    if (prevBtn) {
      prevBtn.addEventListener("click", (e) => {
        e.preventDefault();
        updateCard(currentIdx - 1);
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener("click", (e) => {
        e.preventDefault();
        updateCard(currentIdx + 1);
      });
    }
  }
});
