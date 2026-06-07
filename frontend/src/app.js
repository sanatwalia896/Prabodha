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

  function renderRoute() {
    const route = normalizeRoute(window.location.hash.replace(/^#/, "") || "/");
    const pageRenderer = router.resolve(route.path);
    const renderFrame = (dashboardData, sessionData) => {
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
    };

    const fallbackDashboard = {
      quote: "Attention is a skill. Train it like one.",
      metrics: [
        { label: "Avg Focus", value: "84%" },
        { label: "Hours Tracked", value: "4.3" },
        { label: "Top Distraction", value: "Slack" },
      ],
    };
    const fallbackSession = {
      route,
      timer: "01:42:18",
      score: 87,
      events: [
        "Focused -> Possible Distraction at T+42m",
        "Recovered at T+47m",
      ],
    };

    renderFrame(fallbackDashboard, fallbackSession);

    Promise.all([fetchDashboardData(), fetchSessionData(route)])
      .then(([dashboardData, sessionData]) => {
        renderFrame(dashboardData, sessionData);
      })
      .catch(() => {
        renderFrame(fallbackDashboard, fallbackSession);
      });
  }

  window.addEventListener("hashchange", renderRoute);

  return {
    render: renderRoute,
    destroy() {
      window.removeEventListener("hashchange", renderRoute);
    },
  };
}
