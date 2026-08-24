# Product Engineering Labs

Public, sanitized engineering samples for showing product-minded backend work without exposing private product code, data, routes, vendors, or business rules.

This folder is not a copy of any private project. It is a small neutral lab that demonstrates how I think about product flow, API boundaries, verification, and AI-assisted delivery.

## What This Proves

| Area | What is demonstrated |
|---|---|
| State flow | Allowed transitions, blocked transitions, and clear error reasons |
| API boundary | Request parsing, action validation, and consistent response shape |
| Product judgment | Rules are explicit instead of hidden in UI behavior |
| Delivery discipline | Tests cover happy paths, invalid paths, duplicate requests, and audit output |
| AI collaboration | Code is still reviewed through behavior, logs, and repeatable tests |

## What Is Intentionally Not Here

| Not public | Reason |
|---|---|
| Private source code | Protects the actual product implementation |
| Real route names | Avoids exposing internal API shape |
| Real business rules | Avoids leaking product strategy |
| Real database schema | Avoids leaking data design |
| Real vendors or keys | Avoids security and supplier exposure |
| Real screenshots or accounts | Avoids user/data leakage |

## Lab 01: Work Item State Flow

This lab uses a neutral `work item` example. It models a small workflow where each action must be allowed by the current state and actor role.

Main ideas:

- Keep workflow rules in one explicit module.
- Return stable errors that a UI or client can understand.
- Record audit entries for each accepted state change.
- Ignore duplicate actions when the same idempotency key is used again.
- Verify behavior with built-in Node.js tests.

## Run

```bash
npm test
```

```bash
npm start
```

Then send a request:

```bash
curl -X POST http://localhost:4310/work-items/demo-1/actions \
  -H "content-type: application/json" \
  -d "{\"action\":\"submit\",\"actorRole\":\"owner\",\"idempotencyKey\":\"demo-submit-1\"}"
```

## Example Response

```json
{
  "ok": true,
  "workItem": {
    "id": "demo-1",
    "state": "submitted"
  },
  "audit": {
    "action": "submit",
    "from": "draft",
    "to": "submitted",
    "actorRole": "owner"
  }
}
```

## Design Notes

This lab is deliberately small. The point is not to claim a full product is public; the point is to make the engineering thinking inspectable:

- Where are the rules?
- What happens when an action is invalid?
- Can the behavior be tested repeatedly?
- Can a reviewer understand the safety boundary without seeing private code?
