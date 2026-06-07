export function renderAnalytics() {
  const section = document.createElement("section");
  section.className = "page grid";
  section.innerHTML = `
    <article class="card stack">
      <span class="eyebrow">Analytics</span>
      <h2>Focus trend</h2>
      <div class="chart"></div>
    </article>
    <article class="card stack">
      <span class="eyebrow">App Distribution</span>
      <div class="donut"></div>
    </article>
  `;
  return section;
}
