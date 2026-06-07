export function renderLayout({ route, store, content }) {
  const shell = document.createElement("div");
  shell.className = "shell";
  shell.innerHTML = `
    <aside class="sidebar">
      <div class="brand">
        <span class="brand__mark"></span>
        <div>
          <strong>Prabodha</strong>
          <p>Productivity Command Center</p>
        </div>
      </div>
      <nav class="nav">
        ${navLink("/", "Dashboard", route.path)}
        ${navLink("/session", "Session", route.path)}
        ${navLink("/monitor", "Monitor", route.path)}
        ${navLink("/replay/demo", "Replay", route.path)}
        ${navLink("/journal/demo", "Journal", route.path)}
        ${navLink("/coach", "Coach", route.path)}
        ${navLink("/analytics", "Analytics", route.path)}
        ${navLink("/settings", "Settings", route.path)}
      </nav>
    </aside>
    <div class="workspace">
      <header class="topbar">
        <div>
          <span class="eyebrow">Current Focus</span>
          <h1>${store.user.focusLevel}</h1>
        </div>
        <div class="topbar__status">
          <span class="pill ${store.session.isActive ? "pill--active" : ""}">${store.session.isActive ? "Session Active" : "Session Idle"}</span>
          <span class="pill">Agent OK</span>
        </div>
      </header>
      <main class="content">${content.outerHTML}</main>
    </div>
  `;
  return shell;
}

function navLink(path, label, activePath) {
  const active = activePath === path || activePath.startsWith(path + "/");
  return `<a class="nav__link ${active ? "nav__link--active" : ""}" href="#${path}">${label}</a>`;
}
