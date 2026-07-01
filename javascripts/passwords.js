(function () {
  const PASSWORD = "training";
  const STORAGE_KEY = "tfi_authenticated";

  function isAuthenticated() {
    return sessionStorage.getItem(STORAGE_KEY) === "true";
  }

  function renderGate() {
    document.documentElement.style.background = "#ffffff";
    document.body.innerHTML = `
      <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:Arial,sans-serif;padding:2rem;box-sizing:border-box;">
        <div style="max-width:420px;width:100%;border:1px solid #ddd;border-radius:12px;padding:2rem;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
          <h1 style="margin-top:0;font-size:1.5rem;">Protected site</h1>
          <p style="margin-bottom:1rem;">Enter the password to continue.</p>
          <input id="site-password" type="password" style="width:100%;padding:0.75rem;margin-bottom:0.75rem;border:1px solid #bbb;border-radius:8px;font-size:1rem;" />
          <button id="submit-password" style="width:100%;padding:0.75rem;border:none;border-radius:8px;font-size:1rem;cursor:pointer;">Enter</button>
          <p id="password-error" style="color:#b00020;margin-top:0.75rem;min-height:1.2em;"></p>
        </div>
      </div>
    `;

    const input = document.getElementById("site-password");
    const button = document.getElementById("submit-password");
    const error = document.getElementById("password-error");

    function submitPassword() {
      if (input.value === PASSWORD) {
        sessionStorage.setItem(STORAGE_KEY, "true");
        window.location.reload();
      } else {
        error.textContent = "Incorrect password";
        input.value = "";
        input.focus();
      }
    }

    button.addEventListener("click", submitPassword);
    input.addEventListener("keydown", function (event) {
      if (event.key === "Enter") submitPassword();
    });

    input.focus();
  }

  function protectPage() {
    if (!isAuthenticated()) {
      renderGate();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", protectPage);
  } else {
    protectPage();
  }
})();