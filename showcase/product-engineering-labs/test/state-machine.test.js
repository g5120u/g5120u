import assert from "node:assert/strict";
import test from "node:test";

import { DomainError } from "../src/errors.js";
import { applyAction, createWorkItem, STATES } from "../src/state-machine.js";

test("moves through the expected happy path with audit records", () => {
  let item = createWorkItem("demo-1");

  item = applyAction(item, {
    action: "submit",
    actorRole: "owner",
    idempotencyKey: "submit-1",
  }).workItem;

  item = applyAction(item, {
    action: "accept",
    actorRole: "operator",
    idempotencyKey: "accept-1",
  }).workItem;

  item = applyAction(item, {
    action: "start",
    actorRole: "operator",
    idempotencyKey: "start-1",
  }).workItem;

  item = applyAction(item, {
    action: "request_review",
    actorRole: "operator",
    idempotencyKey: "review-1",
  }).workItem;

  item = applyAction(item, {
    action: "complete",
    actorRole: "reviewer",
    idempotencyKey: "complete-1",
  }).workItem;

  assert.equal(item.state, STATES.DONE);
  assert.deepEqual(
    item.audit.map((entry) => entry.action),
    ["submit", "accept", "start", "request_review", "complete"],
  );
});

test("rejects actions that skip required states", () => {
  const item = createWorkItem("demo-2");

  assert.throws(
    () =>
      applyAction(item, {
        action: "complete",
        actorRole: "reviewer",
      }),
    (error) =>
      error instanceof DomainError &&
      error.code === "invalid_transition" &&
      error.details.currentState === STATES.DRAFT,
  );
});

test("rejects roles that are not allowed for the action", () => {
  const item = applyAction(createWorkItem("demo-3"), {
    action: "submit",
    actorRole: "owner",
  }).workItem;

  assert.throws(
    () =>
      applyAction(item, {
        action: "accept",
        actorRole: "owner",
      }),
    (error) => error instanceof DomainError && error.code === "forbidden_action",
  );
});

test("returns duplicate result for repeated idempotency key", () => {
  const first = applyAction(createWorkItem("demo-4"), {
    action: "submit",
    actorRole: "owner",
    idempotencyKey: "same-command",
  });

  const second = applyAction(first.workItem, {
    action: "submit",
    actorRole: "owner",
    idempotencyKey: "same-command",
  });

  assert.equal(second.duplicate, true);
  assert.equal(second.audit, null);
  assert.equal(second.workItem.audit.length, 1);
});
