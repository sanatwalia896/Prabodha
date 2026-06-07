const fallbackDashboard = {
  quote: "Attention is a skill. Train it like one.",
  metrics: [
    { label: "Avg Focus", value: "84%" },
    { label: "Hours Tracked", value: "4.3" },
    { label: "Top Distraction", value: "Slack" },
  ],
};

export async function fetchDashboardData() {
  const response = await tryFetch("/api/v1/analytics/trends?user_id=00000000-0000-0000-0000-000000000001");
  if (!response) {
    return fallbackDashboard;
  }
  return {
    quote: "Attention is a skill. Train it like one.",
    metrics: [
      { label: "Avg Focus", value: `${Math.round(mean(response.points.map((point) => point.focus_score)))}%` },
      { label: "Hours Tracked", value: `${(response.points.length * 0.75).toFixed(1)}` },
      { label: "Top Distraction", value: "Slack" },
    ],
  };
}

export async function fetchSessionData(route) {
  const fallback = {
    route,
    timer: "01:42:18",
    score: 87,
    events: [
      "Focused -> Possible Distraction at T+42m",
      "Recovered at T+47m",
    ],
  };

  if (!route.path.startsWith("/session")) {
    return fallback;
  }

  const response = await tryFetch("/api/v1/sessions/00000000-0000-0000-0000-000000000001");
  if (!response) {
    return fallback;
  }
  return {
    route,
    timer: "01:42:18",
    score: response.overall_score ?? 87,
    events: [`Session ${response.label ?? "Focus"} is active`, "Live session metrics loaded"],
  };
}

async function tryFetch(pathname) {
  try {
    const response = await fetch(pathname, { headers: { Accept: "application/json" } });
    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch {
    return null;
  }
}

function mean(values) {
  if (!values.length) {
    return 84;
  }
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}
