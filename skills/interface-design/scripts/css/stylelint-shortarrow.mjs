/**
 * Two stylelint rules for what a stylesheet alone can settle about readable text.
 *
 * shortarrow/no-fixed-text-height
 *   A rule that sets height or block-size to a length can cut off or spill the text
 *   it holds once the text grows: a longer translation, a larger font, a narrow
 *   screen. CSS does not say which elements hold text, so this is judged by the
 *   rule: refused unless every selector ends in a media or form element (img, svg,
 *   video, canvas, ...), the rule scrolls (overflow auto or scroll), or it draws an
 *   empty decoration (content: ""). A percentage, a keyword, 0 or a var() passes.
 *
 * shortarrow/text-contrast  [true, { minimum: 7 }]
 *   A rule that sets both color and a background colour is refused when the pair is
 *   under the minimum ratio (7:1 by default, WCAG 1.4.6). var() is resolved from
 *   :root or html, once for the base values and once for each theme that overrides
 *   them (inside an at-rule such as prefers-color-scheme, or :root[data-theme=...]).
 *   Not judged: translucent colours, currentColor, transparent, gradients and images,
 *   color-mix() and relative colours, a var() with no value, and a pair split across
 *   rules — the stylesheet alone does not settle what is painted under the text.
 */
import stylelint from "stylelint";
import { contrastRatio, parseColor } from "./contrast.mjs";

const {
  createPlugin,
  utils: { report, ruleMessages, validateOptions },
} = stylelint;

const LENGTH = /(^|[\s(,+*/-])(\d*\.?\d+)(px|r?em|ex|r?lh|ch|cap|ic|[sld]?v[hwbi]|vmin|vmax|cm|mm|q|in|pt|pc)\b/i;
const NOT_TEXT = new Set(["img", "svg", "video", "canvas", "iframe", "picture", "object", "embed", "hr", "audio",
  "progress", "meter", "input", "select"]);

function lastCompoundTag(selector) {
  const last = selector.trim().split(/\s*[\s>+~]\s*/).pop() ?? "";
  return (last.match(/^[a-z][a-z0-9-]*/i) ?? [""])[0].toLowerCase();
}

function declared(rule, ...props) {
  const found = {};
  rule.each((node) => {
    if (node.type === "decl" && props.includes(node.prop.toLowerCase())) found[node.prop.toLowerCase()] = node;
  });
  return found;
}

const heightRule = "shortarrow/no-fixed-text-height";
const heightMessages = ruleMessages(heightRule, {
  rejected: (prop, value) =>
    `${prop}: ${value} fixes the height of a box that can hold text; let it follow its content (min-height, or auto)`,
});

const noFixedTextHeight = (primary) => (root, result) => {
  if (!validateOptions(result, heightRule, { actual: primary })) return;
  root.walkDecls(/^(height|block-size)$/i, (decl) => {
    const rule = decl.parent;
    if (rule?.type !== "rule") return;
    const value = decl.value.trim();
    if (/var\(/i.test(value) || value.includes("%") || !LENGTH.test(value)) return;
    const { overflow, "overflow-y": overflowY, "overflow-block": overflowBlock, content } =
      declared(rule, "overflow", "overflow-y", "overflow-block", "content");
    if ([overflow, overflowY, overflowBlock].some((d) => d && /\b(auto|scroll)\b/i.test(d.value))) return;
    if (content && /^(""|'')$/.test(content.value.trim())) return;
    if (rule.selectors.every((s) => NOT_TEXT.has(lastCompoundTag(s)))) return;
    report({ ruleName: heightRule, result, node: decl, message: heightMessages.rejected(decl.prop, value) });
  });
};
noFixedTextHeight.ruleName = heightRule;
noFixedTextHeight.messages = heightMessages;

const contrastRule = "shortarrow/text-contrast";
const contrastMessages = ruleMessages(contrastRule, {
  rejected: (ratio, minimum, scope) =>
    `color on background is ${ratio.toFixed(2)}:1${scope ? ` in ${scope}` : ""}, under ${minimum}:1`,
});

const ROOT_SELECTOR = /^(:root|html)((\[[^\]]+\])|(\.[\w-]+))*$/;

/** [{ label, vars }]: the base custom properties, then each theme layered over them. */
function themes(root) {
  const base = {};
  const layers = new Map();
  root.walkRules((rule) => {
    if (!rule.selectors.every((s) => ROOT_SELECTOR.test(s.trim()))) return;
    const atRules = [];
    for (let p = rule.parent; p && p.type !== "root"; p = p.parent) if (p.type === "atrule") atRules.unshift(`@${p.name} ${p.params}`);
    const plain = atRules.length === 0 && rule.selectors.every((s) => /^(:root|html)$/.test(s.trim()));
    const label = [...atRules, plain ? "" : rule.selector].filter(Boolean).join(" ");
    const target = plain ? base : layers.get(label) ?? layers.set(label, {}).get(label);
    rule.walkDecls(/^--/, (decl) => { target[decl.prop] = decl.value.trim(); });
  });
  return [{ label: "", vars: base }, ...[...layers].map(([label, vars]) => ({ label, vars: { ...base, ...vars } }))];
}

function resolve(value, vars, depth = 0) {
  const match = value.trim().match(/^var\(\s*(--[\w-]+)\s*(?:,\s*(.+))?\)$/i);
  if (!match) return value.trim();
  if (depth > 8) return null;
  const next = vars[match[1]] ?? match[2];
  return next === undefined ? null : resolve(next, vars, depth + 1);
}

const textContrast = (primary, secondary) => (root, result) => {
  if (!validateOptions(result, contrastRule, { actual: primary }, {
    actual: secondary, possible: { minimum: [(n) => typeof n === "number" && n >= 1 && n <= 21] }, optional: true,
  })) return;
  const minimum = secondary?.minimum ?? 7;
  const scopes = themes(root);
  root.walkRules((rule) => {
    const { color, "background-color": bgColor, background } = declared(rule, "color", "background-color", "background");
    const bg = bgColor ?? background;
    if (!color || !bg) return;
    const uses = /var\(/i.test(color.value + bg.value);
    for (const { label, vars } of uses ? scopes : scopes.slice(0, 1)) {
      const fgValue = resolve(color.value, vars);
      const bgValue = resolve(bg.value, vars);
      const fg = fgValue && parseColor(fgValue);
      const back = bgValue && parseColor(bgValue);
      if (!fg || !back || fg.a < 1 || back.a < 1) continue;
      const ratio = contrastRatio(fg, back);
      if (ratio < minimum) {
        report({ ruleName: contrastRule, result, node: rule, word: "color", message: contrastMessages.rejected(ratio, minimum, label) });
        return;
      }
    }
  });
};
textContrast.ruleName = contrastRule;
textContrast.messages = contrastMessages;

export default [createPlugin(heightRule, noFixedTextHeight), createPlugin(contrastRule, textContrast)];
