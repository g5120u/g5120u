import { DomainError } from "./errors.js";

export const STATES = Object.freeze({
  DRAFT: "draft",
  SUBMITTED: "submitted",
  ACCEPTED: "accepted",
  IN_PROGRESS: "in_progress",
  REVIEW: "review",
  DONE: "done",
  CANCELLED: "cancelled",
});

export const ACTIONS = Object.freeze({
  SUBMIT: "submit",
  ACCEPT: "accept",
  START: "start",
  REQUEST_REVIEW: "request_review",
  COMPLETE: "complete",
  CANCEL: "cancel",
});

const TRANSITIONS = Object.freeze({
  [ACTIONS.SUBMIT]: {
    from: [STATES.DRAFT],
    to: STATES.SUBMITTED,
    roles: ["owner"],
  },
  [ACTIONS.ACCEPT]: {
    from: [STATES.SUBMITTED],
    to: STATES.ACCEPTED,
    roles: ["operator"],
  },
  [ACTIONS.START]: {
    from: [STATES.ACCEPTED],
    to: STATES.IN_PROGRESS,
    roles: ["operator"],
  },
  [ACTIONS.REQUEST_REVIEW]: {
    from: [STATES.IN_PROGRESS],
    to: STATES.REVIEW,
    roles: ["operator"],
  },
  [ACTIONS.COMPLETE]: {
    from: [STATES.REVIEW],
    to: STATES.DONE,
    roles: ["reviewer"],
  },
  [ACTIONS.CANCEL]: {
    from: [STATES.DRAFT, STATES.SUBMITTED, STATES.ACCEPTED],
    to: STATES.CANCELLED,
    roles: ["owner", "operator"],
  },
});

export function createWorkItem(id, attrs = {}) {
  if (!id || typeof id !== "string") {
    throw new DomainError("invalid_work_item_id", "Work item id is required");
  }

  return {
    id,
    title: attrs.title ?? "Demo work item",
    state: attrs.state ?? STATES.DRAFT,
    audit: attrs.audit ?? [],
    idempotencyKeys: new Set(attrs.idempotencyKeys ?? []),
  };
}

export function applyAction(workItem, command, now = new Date()) {
  assertCommand(command);

  const rule = TRANSITIONS[command.action];
  if (!rule) {
    throw new DomainError("unknown_action", "Action is not supported", {
      action: command.action,
    });
  }

  if (command.idempotencyKey && workItem.idempotencyKeys.has(command.idempotencyKey)) {
    return {
      workItem,
      audit: null,
      duplicate: true,
    };
  }

  if (!rule.from.includes(workItem.state)) {
    throw new DomainError("invalid_transition", "Action is not allowed from the current state", {
      action: command.action,
      currentState: workItem.state,
      allowedFrom: rule.from,
    });
  }

  if (!rule.roles.includes(command.actorRole)) {
    throw new DomainError("forbidden_action", "Actor role cannot perform this action", {
      action: command.action,
      actorRole: command.actorRole,
      allowedRoles: rule.roles,
    });
  }

  const audit = {
    action: command.action,
    from: workItem.state,
    to: rule.to,
    actorRole: command.actorRole,
    at: now.toISOString(),
  };

  const next = {
    ...workItem,
    state: rule.to,
    audit: [...workItem.audit, audit],
    idempotencyKeys: new Set(workItem.idempotencyKeys),
  };

  if (command.idempotencyKey) {
    next.idempotencyKeys.add(command.idempotencyKey);
  }

  return {
    workItem: next,
    audit,
    duplicate: false,
  };
}

export function serializeWorkItem(workItem) {
  return {
    id: workItem.id,
    title: workItem.title,
    state: workItem.state,
    audit: workItem.audit,
  };
}

function assertCommand(command) {
  if (!command || typeof command !== "object") {
    throw new DomainError("invalid_command", "Command body is required");
  }

  if (!command.action || typeof command.action !== "string") {
    throw new DomainError("invalid_action", "Action is required");
  }

  if (!command.actorRole || typeof command.actorRole !== "string") {
    throw new DomainError("invalid_actor_role", "Actor role is required");
  }

  if (command.idempotencyKey !== undefined && typeof command.idempotencyKey !== "string") {
    throw new DomainError("invalid_idempotency_key", "Idempotency key must be a string");
  }
}
