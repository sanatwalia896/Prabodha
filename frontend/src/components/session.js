export function renderSession({ sessionData }) {
  const section = document.createElement("section");
  section.className = "page";
  section.innerHTML = `
    <div class="card stack">
      <span class="eyebrow">Focus Session</span>
      <h2>${sessionData.timer}</h2>
      <div class="gauge"><span style="width:${sessionData.score}%"></span></div>
      <div class="controls">
        <button class="button">Pause</button>
        <button class="button button--ghost">Stop</button>
        <button class="button button--danger">I'm Distracted</button>
      </div>
    </div>
  `;
  return section;
}
