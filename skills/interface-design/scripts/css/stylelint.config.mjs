/**
 * Shared stylelint configuration: readable text, as far as a stylesheet settles it.
 *
 * Copy this folder (stylelint.config.mjs, stylelint-shortarrow.mjs, contrast.mjs) into
 * a project, install stylelint (17.16.0 is what it was tested with), and extend it:
 *
 *   export default { extends: ["./stylelint/stylelint.config.mjs"], rules: { ... } };
 *
 * Refused: text-align or text-align-last justify; a fixed height or block-size on a
 * rule that can hold text; a color and background pair under 7:1.
 */
import { fileURLToPath } from "node:url";

export default {
  plugins: [fileURLToPath(new URL("./stylelint-shortarrow.mjs", import.meta.url))],
  rules: {
    "declaration-property-value-disallowed-list": {
      "text-align": ["justify"],
      "text-align-last": ["justify"],
    },
    "shortarrow/no-fixed-text-height": true,
    "shortarrow/text-contrast": [true, { minimum: 7 }],
  },
};
