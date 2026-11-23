/**
 * Copy into a project's tests/ folder beside layout-check.mjs, and put layout.config.json
 * at the project root:
 *
 *   { "dir": "public", "pages": ["/", "/about/"], "widths": [375, 601, 1040, 1280], "root": "body" }
 *
 * "dir" is a built site to serve; give "baseUrl" instead for one already running.
 * "widths" and "root" are optional. LAYOUT_CONFIG names another config file.
 * Run: node --test tests/
 */
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { DEFAULT_WIDTHS, openSession } from "./layout-check.mjs";

const PROJECT = resolve(import.meta.dirname, "..");
const config = JSON.parse(readFileSync(resolve(PROJECT, process.env.LAYOUT_CONFIG ?? "layout.config.json"), "utf8"));
let session;

before(async () => {
  session = await openSession({ dir: config.dir && resolve(PROJECT, config.dir), baseUrl: config.baseUrl, root: config.root });
});

after(async () => {
  await session?.close();
});

for (const width of config.widths ?? DEFAULT_WIDTHS) {
  test(`every box holds its content at ${width}px`, async () => {
    const failures = [];
    for (const page of config.pages) {
      const { problems } = await session.inspect(page, width);
      failures.push(...problems.map((p) => `${page}: ${p}`));
    }
    assert.deepEqual(failures, []);
  });
}
