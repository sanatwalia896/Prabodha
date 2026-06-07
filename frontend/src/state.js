export function createStore(initialState = {}) {
  let state = {
    user: {
      username: "sam",
      streak: 12,
      focusLevel: "Focused",
    },
    session: {
      isActive: true,
      startTime: "09:00",
      currentSessionId: "session-demo-001",
      overallScore: 87,
    },
    live: {
      currentFocusLevel: 87,
      gazeDirection: "center",
      activeApp: "VSCode",
      isUserAway: false,
    },
    settings: {
      driftThreshold: 0.8,
      privacyMode: true,
    },
    ...initialState,
  };

  const listeners = new Set();

  return {
    getState() {
      return state;
    },
    setState(update) {
      state = typeof update === "function" ? update(state) : { ...state, ...update };
      listeners.forEach((listener) => listener(state));
    },
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}
