import { DomainError, toProblem } from "./errors.js";
import { applyAction, serializeWorkItem } from "./state-machine.js";

export async function routeRequest(req, res, store) {
  try {
    if (req.method === "GET" && req.url === "/health") {
      return sendJson(res, 200, { ok: true, service: "product-engineering-proof" });
    }

    const match = req.url.match(/^\/work-items\/([^/]+)\/actions$/);
    if (req.method === "POST" && match) {
      const id = decodeURIComponent(match[1]);
      const command = await readJson(req);
      const current = store.getOrCreate(id);
      const result = applyAction(current, command);

      store.save(result.workItem);

      return sendJson(res, result.duplicate ? 200 : 202, {
        ok: true,
        duplicate: result.duplicate,
        workItem: serializeWorkItem(result.workItem),
        audit: result.audit,
      });
    }

    throw new DomainError("not_found", "Route was not found", {
      method: req.method,
      url: req.url,
    });
  } catch (error) {
    const problem = toProblem(error);
    const status = statusFor(problem.error.code);
    return sendJson(res, status, problem);
  }
}

export async function readJson(req) {
  const chunks = [];

  for await (const chunk of req) {
    chunks.push(chunk);
  }

  const text = Buffer.concat(chunks).toString("utf8").trim();
  if (!text) {
    return {};
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new DomainError("invalid_json", "Request body must be valid JSON");
  }
}

export function sendJson(res, status, body) {
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
  });
  res.end(`${JSON.stringify(body, null, 2)}\n`);
}

function statusFor(code) {
  if (code === "not_found") return 404;
  if (code === "forbidden_action") return 403;
  if (code.startsWith("invalid_")) return 400;
  if (code === "unknown_action") return 400;
  return 500;
}
