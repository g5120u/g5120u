import assert from "node:assert/strict";
import http from "node:http";
import test from "node:test";

import { routeRequest } from "../src/api.js";
import { createMemoryStore } from "../src/work-item-store.js";

test("POST action returns a stable API response", async () => {
  const server = createTestServer();
  const baseUrl = await listen(server);

  try {
    const response = await fetch(`${baseUrl}/work-items/demo-api/actions`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        action: "submit",
        actorRole: "owner",
        idempotencyKey: "api-submit-1",
      }),
    });

    const body = await response.json();

    assert.equal(response.status, 202);
    assert.equal(body.ok, true);
    assert.equal(body.workItem.state, "submitted");
    assert.equal(body.audit.from, "draft");
    assert.equal(body.audit.to, "submitted");
  } finally {
    await close(server);
  }
});

test("invalid transition is returned as a typed problem", async () => {
  const server = createTestServer();
  const baseUrl = await listen(server);

  try {
    const response = await fetch(`${baseUrl}/work-items/demo-api/actions`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        action: "complete",
        actorRole: "reviewer",
      }),
    });

    const body = await response.json();

    assert.equal(response.status, 400);
    assert.equal(body.ok, false);
    assert.equal(body.error.code, "invalid_transition");
    assert.equal(body.error.details.currentState, "draft");
  } finally {
    await close(server);
  }
});

function createTestServer() {
  const store = createMemoryStore();
  return http.createServer((req, res) => {
    routeRequest(req, res, store);
  });
}

function listen(server) {
  return new Promise((resolve) => {
    server.listen(0, () => {
      const address = server.address();
      resolve(`http://127.0.0.1:${address.port}`);
    });
  });
}

function close(server) {
  return new Promise((resolve, reject) => {
    server.close((error) => {
      if (error) reject(error);
      else resolve();
    });
  });
}
