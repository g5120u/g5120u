import http from "node:http";
import { routeRequest } from "./api.js";
import { createMemoryStore } from "./work-item-store.js";

const port = Number.parseInt(process.env.PORT ?? "4310", 10);
const store = createMemoryStore();

const server = http.createServer((req, res) => {
  routeRequest(req, res, store);
});

server.listen(port, () => {
  console.log(`product-engineering-proof listening on http://localhost:${port}`);
});
