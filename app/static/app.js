document.addEventListener("DOMContentLoaded", () => {
  const panel = document.querySelector("[data-thresholds]");
  if (!panel) return;
  const rows = JSON.parse(panel.dataset.thresholds);
  const slider = document.getElementById("threshold");
  const format = value => `${(Number(value) * 100).toFixed(1)}%`;
  const render = () => {
    const row = rows[Number(slider.value)];
    document.getElementById("threshold-value").textContent = Number(row.threshold).toFixed(2);
    ["precision", "recall", "f1"].forEach(key => document.getElementById(key).textContent = format(row[key]));
    document.getElementById("contact-rate").textContent = format(row.contact_rate);
    ["tn", "fp", "fn", "tp"].forEach(key => document.getElementById(key).textContent = Number(row[key]).toLocaleString("vi-VN"));
  };
  slider.addEventListener("input", render);
  render();
});
