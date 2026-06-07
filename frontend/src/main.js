import { createApp } from "./app.js";

const mountNode = document.querySelector("#app");

if (!mountNode) {
  throw new Error("App mount node not found");
}

createApp(mountNode).render();
