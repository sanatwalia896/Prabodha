export function renderCoach() {
  const section = document.createElement("section");
  section.className = "page grid";
  section.innerHTML = `
    <article class="card stack">
      <span class="eyebrow">AI Coach</span>
      <h2>Session reflections</h2>
      <p>Prompt: Analyze my fatigue patterns.</p>
    </article>
    <article class="card stack">
      <span class="eyebrow">Insight</span>
      <p>You stayed strong until your app-switch cluster near mid-session.</p>
    </article>
  `;
  return section;
}
