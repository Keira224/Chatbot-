document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    window.setTimeout(() => alert.classList.remove("show"), 5000);
  });

  document.querySelectorAll(".quick-question").forEach((button) => {
    button.addEventListener("click", () => {
      const input = document.querySelector("#id_question");
      if (!input) return;
      input.value = button.dataset.question;
      input.focus();
    });
  });

  const chatMessages = document.querySelector("#chatMessages");
  if (chatMessages) {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});
