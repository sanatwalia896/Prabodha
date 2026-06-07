export function renderJournal() {
  const section = document.createElement("section");
  section.className = "page";
  section.innerHTML = `
    <article class="card stack">
      <span class="eyebrow">Journal</span>
      <h2>Reflect on the session</h2>
      <textarea class="text-area" rows="8" placeholder="Write what helped or hurt your focus."></textarea>
    </article>
  `;
  return section;
}
