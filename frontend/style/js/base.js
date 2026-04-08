// ================= BASE.JS =================
// Global script for shared UI behavior

document.addEventListener("DOMContentLoaded", () => {

  // ================= PROFILE DROPDOWN =================
  const userInfo = document.querySelector(".user-info");

  if (userInfo) {
    let dropdown = document.createElement("div");
    dropdown.className = "base-dropdown hidden";

    dropdown.innerHTML = `
      <a href="/profile">Profile</a>
      <a href="/logout">Logout</a>
    `;

    userInfo.style.position = "relative";
    userInfo.appendChild(dropdown);

    userInfo.addEventListener("click", () => {
      dropdown.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
      if (!userInfo.contains(e.target)) {
        dropdown.classList.remove("show");
      }
    });
  }

  // ================= ACTIVE LINK SAFETY =================
  // (Fallback in case Jinja fails)
  const links = document.querySelectorAll(".topnav .nav-link");
  const currentPath = window.location.pathname;

  links.forEach(link => {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });

  // ================= SMOOTH SCROLL (OPTIONAL) =================
  document.querySelectorAll("a[href^='#']").forEach(anchor => {
    anchor.addEventListener("click", function (e) {
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: "smooth"
        });
      }
    });
  });

});