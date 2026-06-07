export function renderDashboard({ dashboardData, store }) {
  const section = document.createElement("section");
  section.className = "page page--dashboard";
  section.innerHTML = `
    <div class="hero">
      <div>
        <span class="eyebrow">Welcome back, ${store.user.username}</span>
        <h2>Build the next clean block with intention.</h2>
        <p>${dashboardData.quote}</p>
      </div>
      <button class="button button--primary">Start Focus Session</button>
    </div>
    <div class="metrics">
      ${dashboardData.metrics.map((metric) => `
        <article class="card stat">
          <span>${metric.label}</span>
          <strong>${metric.value}</strong>
        </article>
      `).join("")}
    </div>
  `;
  return section;
}
