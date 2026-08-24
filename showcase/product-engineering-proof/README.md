# Product Engineering Proof

Public, sanitized engineering proof for showing product-minded backend work without exposing private product code, data, routes, vendors, or business rules.

This folder is not a copy of any private project. It is a neutral proof sample that makes the engineering thinking inspectable: state rules, API behavior, error boundaries, duplicate-request handling, and repeatable tests.

## What This Proves

| Proof point | Where to inspect | What it shows |
|---|---|---|
| State rules are explicit | `src/state-machine.js` | Allowed transitions, blocked transitions, role limits, and audit entries are handled in one place |
| API boundary is controlled | `src/api.js` | Request parsing, route matching, response shape, and typed errors are separated from workflow rules |
| Duplicate requests are handled | `src/state-machine.js` | Idempotency keys prevent the same accepted action from being recorded twice |
| Behavior is verified | `test/state-machine.test.js` | Happy path, invalid state jumps, forbidden roles, and duplicate commands are tested |
| API output is verified | `test/api.test.js` | Real HTTP requests check success and failure responses instead of only testing internal functions |

## What Is Intentionally Not Here

| Not public | Reason |
|---|---|
| Private source code | Protects the actual product implementation |
| Real route names | Avoids exposing internal API shape |
| Real business rules | Avoids leaking product strategy |
| Real database schema | Avoids leaking data design |
| Real vendors, keys, or supplier choices | Avoids security and supplier exposure |
| Real screenshots or accounts | Avoids user/data leakage |

## Proof 01: Work Item State Flow

This proof uses a neutral `work item` example. It models a small workflow where each action must be allowed by the current state and actor role.

Main ideas:

- Keep workflow rules in one explicit module.
- Return stable errors that a UI or client can understand.
- Record audit entries for each accepted state change.
- Ignore duplicate actions when the same idempotency key is used again.
- Verify behavior with built-in Node.js tests.

## Why This Is Product Engineering

Product code is not only about writing endpoints. A real workflow must answer product questions in code:

- Who is allowed to do this action?
- From which state is the action valid?
- What error does the client receive when the action is blocked?
- Can the same request be safely retried?
- Is there an audit record for what changed?
- Can the behavior be verified without clicking through the UI by hand?

This sample keeps the business situation fake, but the engineering concerns are real.

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

This proof is deliberately small. The point is not to claim a full product is public; the point is to make the engineering thinking inspectable:

- Where are the rules?
- What happens when an action is invalid?
- Can the behavior be tested repeatedly?
- Can a reviewer understand the safety boundary without seeing private code?
