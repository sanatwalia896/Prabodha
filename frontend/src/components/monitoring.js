export function renderMonitoring({ sessionData }) {
  const section = document.createElement("section");
  section.className = "page grid";
  section.innerHTML = `
    <article class="card stack">
      <span class="eyebrow">Live Monitoring</span>
      <h2>Webcam feed placeholder</h2>
      <p>Frame state: Focused</p>
    </article>
    <article class="card stack">
      <span class="eyebrow">Telemetry</span>
      <p>Gaze: center</p>
      <p>Yaw: 2.1</p>
      <p>Pitch: 1.7</p>
      <p>EAR: 0.24</p>
      <p>${sessionData.events.join("<br />")}</p>
    </article>
  `;
  return section;
}
