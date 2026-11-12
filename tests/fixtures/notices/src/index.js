// SPDX-FileCopyrightText: 2026 Palette Contributors
// SPDX-License-Identifier: Apache-2.0

function channel(n) {
  return n.toString(16).padStart(2, '0');
}

function toHex({ r, g, b }) {
  return `#${channel(r)}${channel(g)}${channel(b)}`;
}

module.exports = { toHex };
