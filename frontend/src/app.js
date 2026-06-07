import { createRouter, normalizeRoute } from "./router.js";
import { createStore } from "./state.js";
import { fetchDashboardData, fetchSessionData } from "./api.js";
import { renderLayout } from "./components/layout.js";
import { renderDashboard } from "./components/dashboard.js";
import { renderSession } from "./components/session.js";
import { renderMonitoring } from "./components/monitoring.js";
import { renderReplay } from "./components/replay.js";
import { renderJournal } from "./components/journal.js";
import { renderCoach } from "./components/coach.js";
import { renderAnalytics } from "./components/analytics.js";
import { renderSettings } from "./components/settings.js";

const routes = {
  "/": renderDashboard,
  "/session": renderSession,
  "/monitor": renderMonitoring,
  "/replay/:clipId": renderReplay,
  "/journal/:sessionId": renderJournal,
  "/coach": renderCoach,
  "/analytics": renderAnalytics,
  "/settings": renderSettings,
};

export function createApp(mountNode) {
  const store = createStore();
  const router = createRouter(routes);

  async function renderRoute() {
    const route = normalizeRoute(window.location.hash.replace(/^#/, "") || "/");
    const pageRenderer = router.resolve(route.path);
    const dashboardData = await fetchDashboardData();
    const sessionData = await fetchSessionData(route);

    mountNode.innerHTML = "";
    mountNode.appendChild(
      renderLayout({
        route,
        store: store.getState(),
        content: pageRenderer({
          route,
          store,
          dashboardData,
          sessionData,
        }),
      }),
    );
  }

  window.addEventListener("hashchange", renderRoute);

  return {
    render: renderRoute,
    destroy() {
      window.removeEventListener("hashchange", renderRoute);
    },
  };
}
