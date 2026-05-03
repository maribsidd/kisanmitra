// Auto-dismiss flash messages after 5s
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".flash").forEach(el => {
    setTimeout(() => el.remove(), 5000);
  });
});

// Tab switching
function switchTab(id, btn) {
  document.querySelectorAll(".tab-pane").forEach(p => p.style.display = "none");
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById(id).style.display = "block";
  btn.classList.add("active");
}

// Confirm before destructive actions
document.querySelectorAll("[data-confirm]")?.forEach(el => {
  el.addEventListener("click", e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});
