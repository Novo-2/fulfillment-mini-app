document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".tab-button");
  const tabs = document.querySelectorAll(".tab");

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");

      buttons.forEach((b) => b.classList.remove("active"));
      tabs.forEach((tab) => tab.classList.remove("active"));

      btn.classList.add("active");
      document.getElementById(`tab-${target}`).classList.add("active");
    });
  });
});
