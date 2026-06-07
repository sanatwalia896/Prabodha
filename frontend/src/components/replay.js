export function renderReplay() {
  const section = document.createElement("section");
  section.className = "page";
  section.innerHTML = `
    <article class="card stack">
      <span class="eyebrow">Replay Viewer</span>
      <h2>Clip playback controls</h2>
      <div class="video-shell">Replay stream surface</div>
    </article>
  `;
  return section;
}
