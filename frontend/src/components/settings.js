export function renderSettings() {
  const section = document.createElement("section");
  section.className = "page";
  section.innerHTML = `
    <article class="card stack">
      <span class="eyebrow">Settings</span>
      <h2>Privacy and calibration</h2>
      <label class="field">Drift threshold <input type="range" min="0" max="1" step="0.05" value="0.8" /></label>
    </article>
  `;
  return section;
}
