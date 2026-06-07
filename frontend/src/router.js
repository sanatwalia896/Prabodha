export function normalizeRoute(route) {
  const trimmed = route.trim() || "/";
  const withoutHash = trimmed.startsWith("#") ? trimmed.slice(1) : trimmed;
  const path = withoutHash.startsWith("/") ? withoutHash : `/${withoutHash}`;
  const [pathname, search = ""] = path.split("?");
  const segments = pathname.split("/").filter(Boolean);
  return {
    path: pathname === "" ? "/" : pathname,
    search,
    segments,
  };
}

export function createRouter(routes) {
  return {
    resolve(pathname) {
      if (routes[pathname]) {
        return routes[pathname];
      }
      const pathSegments = pathname.split("/").filter(Boolean);
      for (const [pattern, renderer] of Object.entries(routes)) {
        const patternSegments = pattern.split("/").filter(Boolean);
        if (patternSegments.length !== pathSegments.length) {
          continue;
        }
        const matches = patternSegments.every((segment, index) => segment.startsWith(":") || segment === pathSegments[index]);
        if (matches) {
          return renderer;
        }
      }
      return routes["/"];
    },
  };
}
