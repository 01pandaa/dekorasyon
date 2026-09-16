document.addEventListener("DOMContentLoaded", () => {
  const menuButton = document.querySelector("[data-menu-button]");
  const navLinks = document.querySelector("[data-nav-links]");

  function closeMenu() {
    navLinks.classList.remove("open");
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.setAttribute("aria-label", "Menüyü aç");
  }

  if (menuButton && navLinks) {
    menuButton.addEventListener("click", () => {
      const open = navLinks.classList.toggle("open");
      menuButton.setAttribute("aria-expanded", String(open));
      menuButton.setAttribute("aria-label", open ? "Menüyü kapat" : "Menüyü aç");
    });
    navLinks.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && navLinks.classList.contains("open")) {
        closeMenu();
        menuButton.focus();
      }
    });
    document.addEventListener("click", (event) => {
      if (!navLinks.contains(event.target) && !menuButton.contains(event.target)) closeMenu();
    });
  }

  // Only page/service/district context enters the data layer.
  // No analytics request is sent until an owner-configured tag is connected.
  function track(eventName, values) {
    try {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({
        event: eventName,
        page_path: document.body.dataset.pagePath || "/",
        service_slug: document.body.dataset.service || "",
        district_slug: document.body.dataset.district || "",
        ...values,
      });
    } catch (_) {
      // A measurement integration must never prevent a contact action.
    }
  }

  document.addEventListener("click", (event) => {
    const contact = event.target.closest("[data-contact]");
    if (!contact) return;
    track("contact_click", {
      contact_method: contact.dataset.contact,
      contact_placement: contact.dataset.placement || "content",
    });
  });

  document.querySelectorAll("[data-quote-form]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const service = form.elements.namedItem("service");
      const district = form.elements.namedItem("district");
      const size = form.elements.namedItem("size").value.trim();
      const details = form.elements.namedItem("details").value.trim();
      const message = [
        "Merhaba, Eskişehir Yapı Dekorasyon üzerinden teklif almak istiyorum.",
        "Hizmet: " + service.options[service.selectedIndex].text,
        "İlçe: " + district.options[district.selectedIndex].text,
      ];
      if (size) message.push("Yaklaşık ölçü: " + size);
      if (details) message.push("Yapılacak iş: " + details);
      message.push("Sayfa: " + form.dataset.source);
      const destination = "https://wa.me/" + form.dataset.whatsapp
        + "?text=" + encodeURIComponent(message.join("\n"));

      track("quote_whatsapp_open", {
        contact_method: "whatsapp",
        contact_placement: "quote_form",
        service_slug: service.value,
        district_slug: district.value,
      });
      window.location.assign(destination);
    });
    // The contact links remain available if JavaScript cannot run.
    form.hidden = false;
  });

  document.querySelectorAll("[data-year]").forEach((element) => {
    element.textContent = new Date().getFullYear();
  });
});
