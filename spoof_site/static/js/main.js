// Spoof site front-end behavior: cosmetic urgency only.
// It does NOT touch the password field, read saved credentials, or trigger any
// password-manager behavior. It just animates a countdown and shows the popup,
// to demonstrate social-engineering pressure tactics.

// Countdown timer (purely visual).
(function () {
  const el = document.getElementById("countdown");
  if (!el) return;
  let total = 5 * 60; // 5 minutes
  setInterval(function () {
    if (total > 0) total -= 1;
    const m = String(Math.floor(total / 60)).padStart(2, "0");
    const s = String(total % 60).padStart(2, "0");
    el.textContent = `${m}:${s}`;
  }, 1000);
})();

// "Exclusive discount" popup on first load of the home page.
// Shown/hidden by toggling the `.open` class (NOT the hidden attribute, which the
// overlay's CSS display rule would override).
(function () {
  const popup = document.getElementById("popup");
  if (!popup) return;

  const open = function () { popup.classList.add("open"); };
  const close = function () { popup.classList.remove("open"); };

  setTimeout(open, 1200);

  // "No thanks" button closes it.
  const closeBtn = document.getElementById("popup-close");
  if (closeBtn) closeBtn.addEventListener("click", close);

  // Clicking the dark backdrop (outside the popup box) also closes it.
  popup.addEventListener("click", function (e) {
    if (e.target === popup) close();
  });

  // Esc closes it too.
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") close();
  });
})();

console.log("Spoof SIMULATION loaded on", window.location.origin,
            "— educational demo, stores nothing.");
