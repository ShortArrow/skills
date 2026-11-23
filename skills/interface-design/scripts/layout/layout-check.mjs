/**
 * Layout check: what leaves its box, page by page and width by width, in headless Chrome.
 *
 * Copy this file and layout.test.mjs into a project's tests/ folder; layout.test.mjs
 * reads layout.config.json at the project root. Needs Node 22 or later (global
 * WebSocket) and Chrome; CHROME_PATH overrides where Chrome is looked for. No npm
 * dependency: Chrome is driven over the DevTools protocol.
 *
 * Reported, for every element under the root selector that is displayed and has a size:
 *   - a child element whose box lies outside its parent's box, unless the parent
 *     scrolls (overflow auto or scroll) or the child is absolutely or fixed positioned;
 *   - text an element holds directly that lies outside the element's box, which is
 *     what a fixed height does to text, cut off or spilling;
 *   - the page scrolling sideways.
 * A width the viewport did not take, or a page with nothing to inspect, throws, so
 * the check cannot pass by looking at nothing.
 */
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { setPriority } from "node:os";
import { tmpdir } from "node:os";
import { extname, join, normalize, resolve } from "node:path";
import { setTimeout as sleep } from "node:timers/promises";

export const DEFAULT_WIDTHS = [375, 601, 1040, 1280];

const CHROMES = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
];
const MIME = {
  ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".mjs": "text/javascript",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".ico": "image/x-icon",
  ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".json": "application/json",
};

/** Runs in the page. Returns the number of elements inspected and the problems found. */
function inspect(rootSelector) {
  const tol = 1;
  const root = document.querySelector(rootSelector) ?? document.body;
  const label = (el) => el.tagName.toLowerCase() + (el.id ? `#${el.id}` : "") + [...el.classList].map((c) => `.${c}`).join("");
  const scrolls = (cs) => ["auto", "scroll"].includes(cs.overflowX) || ["auto", "scroll"].includes(cs.overflowY);
  const placed = (cs) => cs.position === "absolute" || cs.position === "fixed";
  const outside = (r, box) => r.left < box.left - tol || r.right > box.right + tol || r.top < box.top - tol || r.bottom > box.bottom + tol;
  const problems = [];
  let inspected = 0;
  const page = document.documentElement.scrollWidth;
  const viewport = document.documentElement.clientWidth;
  if (page > viewport + tol) problems.push(`the page scrolls sideways: ${page}px of content in a ${viewport}px viewport`);
  for (const el of [root, ...root.querySelectorAll("*")]) {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.display === "contents" || cs.visibility === "hidden") continue;
    const box = el.getBoundingClientRect();
    if (box.width === 0 && box.height === 0) continue;
    inspected++;
    const parent = el === root ? null : el.parentElement;
    if (parent && !placed(cs) && !scrolls(getComputedStyle(parent)) && outside(box, parent.getBoundingClientRect())) {
      problems.push(`${label(el)} lies outside its parent ${label(parent)}`);
    }
    if (scrolls(cs)) continue;
    for (const node of el.childNodes) {
      if (node.nodeType !== Node.TEXT_NODE || !node.data.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      const lines = [...range.getClientRects()].filter((r) => r.width > 0);
      if (lines.some((r) => outside(r, box))) {
        const bottom = Math.max(...lines.map((r) => r.bottom));
        problems.push(`${label(el)} cannot hold its text: it reaches ${Math.round(bottom - box.top)}px in a ${Math.round(box.height)}px box`);
        break;
      }
    }
  }
  return { inspected, problems };
}

function serve(dir) {
  const base = resolve(dir);
  const server = createServer((req, res) => {
    const path = normalize(decodeURIComponent(new URL(req.url, "http://x").pathname));
    let file = join(base, path);
    if (!file.startsWith(base)) return res.writeHead(403).end();
    if (path.endsWith("/") || path.endsWith("\\")) file = join(file, "index.html");
    if (!existsSync(file)) return res.writeHead(404).end();
    res.writeHead(200, { "content-type": MIME[extname(file)] ?? "application/octet-stream" });
    res.end(readFileSync(file));
  });
  return new Promise((ok) => server.listen(0, "127.0.0.1", () => ok(server)));
}

async function launch(chromePath) {
  const chrome = chromePath ?? process.env.CHROME_PATH ?? CHROMES.find(existsSync);
  if (!chrome) throw new Error("Chrome not found; set CHROME_PATH");
  try { setPriority(19); } catch {}
  const profile = mkdtempSync(join(tmpdir(), "layout-chrome-"));
  const proc = spawn(chrome, ["--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`,
    "--no-first-run", "--hide-scrollbars", "about:blank"], { stdio: "ignore" });
  const portFile = join(profile, "DevToolsActivePort");
  for (let i = 0; i < 150 && !existsSync(portFile); i++) await sleep(100);
  if (!existsSync(portFile)) throw new Error("Chrome did not open its debugging port");
  const port = readFileSync(portFile, "utf8").split("\n")[0];
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const ws = new WebSocket(targets.find((t) => t.type === "page").webSocketDebuggerUrl);
  await new Promise((ok, ng) => { ws.onopen = ok; ws.onerror = ng; });
  let id = 0;
  const pending = new Map();
  const waiters = [];
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id && pending.has(msg.id)) {
      const { ok, ng } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? ng(new Error(msg.error.message)) : ok(msg.result);
    } else if (msg.method) {
      for (const w of waiters.filter((w) => w.method === msg.method)) { waiters.splice(waiters.indexOf(w), 1); w.ok(msg.params); }
    }
  };
  const send = (method, params = {}) => new Promise((ok, ng) => { pending.set(++id, { ok, ng }); ws.send(JSON.stringify({ id, method, params })); });
  const once = (method) => new Promise((ok) => waiters.push({ method, ok }));
  await send("Page.enable");
  const close = async () => {
    ws.close();
    proc.kill();
    for (let i = 0; i < 20; i++) {
      try { rmSync(profile, { recursive: true, force: true }); break; } catch { await sleep(250); }
    }
  };
  return { send, once, close };
}

/**
 * Opens Chrome once and, for a folder, a local server over it.
 * Returns { inspect(page, width), close() }; page is a path under the folder or the base URL.
 */
export async function openSession({ dir, baseUrl, root = "body", chrome } = {}) {
  if (!dir && !baseUrl) throw new Error("give dir (a built site to serve) or baseUrl");
  const server = dir ? await serve(dir) : null;
  const base = server ? `http://127.0.0.1:${server.address().port}` : baseUrl.replace(/\/$/, "");
  const cdp = await launch(chrome);
  return {
    async inspect(page, width) {
      await cdp.send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 768 });
      const loaded = cdp.once("Page.loadEventFired");
      await cdp.send("Page.navigate", { url: base + page });
      await loaded;
      await cdp.send("Runtime.evaluate", { expression: "document.fonts.ready", awaitPromise: true });
      // A phone zooms out when a page is wider than it, which widens innerWidth; the
      // layout width the page was laid out at is documentElement.clientWidth.
      const laid = await cdp.send("Runtime.evaluate", { expression: "document.documentElement.clientWidth", returnByValue: true });
      if (laid.result.value !== width) throw new Error(`${page}: the page was laid out at ${laid.result.value}px, not ${width}px`);
      const { result } = await cdp.send("Runtime.evaluate", { expression: `(${inspect})(${JSON.stringify(root)})`, returnByValue: true });
      if (!result.value?.inspected) throw new Error(`${page} at ${width}px: nothing under ${root} to inspect`);
      return result.value;
    },
    async close() {
      await cdp.close();
      server?.close();
    },
  };
}

/** Every page at every width: [{ page, width, inspected, problems }]. */
export async function checkLayout({ pages, widths = DEFAULT_WIDTHS, ...options }) {
  const session = await openSession(options);
  try {
    const results = [];
    for (const page of pages) {
      for (const width of widths) results.push({ page, width, ...(await session.inspect(page, width)) });
    }
    return results;
  } finally {
    await session.close();
  }
}
