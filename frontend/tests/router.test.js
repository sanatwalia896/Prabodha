import test from "node:test";
import assert from "node:assert/strict";

import { createRouter, normalizeRoute } from "../src/router.js";

test("normalizeRoute trims and preserves route segments", () => {
  const route = normalizeRoute("#/replay/clip-123?speed=1.5");

  assert.equal(route.path, "/replay/clip-123");
  assert.deepEqual(route.segments, ["replay", "clip-123"]);
  assert.equal(route.search, "speed=1.5");
});

test("router resolves parameterized routes", () => {
  const router = createRouter({
    "/": () => "dashboard",
    "/replay/:clipId": () => "replay",
  });

  assert.equal(router.resolve("/replay/abc"), router.resolve("/replay/:clipId"));
  assert.equal(router.resolve("/missing"), router.resolve("/"));
});
