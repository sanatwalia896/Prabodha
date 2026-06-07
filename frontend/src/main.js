import { createApp } from "./app.js";

const mountNode = document.querySelector("#app");

if (!mountNode) {
  throw new Error("App mount node not found");
}

function showFatalError(error) {
  mountNode.innerHTML = `
    <div class="shell shell--fallback">
      <main class="workspace">
        <div class="content">
          <section class="page">
            <article class="card stack">
              <span class="eyebrow">Frontend error</span>
              <h2>Failed to load the app</h2>
              <p>${error instanceof Error ? error.message : String(error)}</p>
            </article>
          </section>
        </div>
      </main>
    </div>
  `;
}

window.addEventListener("error", (event) => {
  showFatalError(event.error || event.message);
});

window.addEventListener("unhandledrejection", (event) => {
  showFatalError(event.reason);
});

try {
  createApp(mountNode).render();
} catch (error) {
  showFatalError(error);
}
