---
name: unmachine-prose
description: Write technical documentation that does not read as machine-generated. The tells are mostly structural, they differ between English and Japanese, and they are recognised when several stack in one passage rather than from any single word. Use when writing a README, an ADR, a commit message, a design document, a note or a PR body, and when revising prose that reads as generic despite being correct.
allowed-tools: Read, Edit, Write, Grep, Glob
---

# Unmachine Prose

Nothing here is about disguising authorship. Every pattern below is a way
of saying less than it appears to, and technical writing is worse for it
regardless of who wrote it.

**The tells stack.** A corpus of 7,600 catalogued signals concludes that
prose becomes recognisable when signals co-occur, not from any one of
them. Fix the density, not the dictionary.

**The two languages barely overlap.** English tells are syntactic —
trailing participles, `not X but Y`, em dashes. Japanese has none of those
constructions. Its tells are in 文末, 接続詞 and 段落の閉じ方. Checking
Japanese against an English list finds nothing and proves nothing.

---

# English

## Participial trailers

The most reliable tell in technical English. A clause hangs off the end of
a sentence and appears to conclude something while adding nothing:

> The cache is invalidated on write, **ensuring consistency**.
> The script validates the marker, **preventing silent failures**.

Either it restates the sentence, or it is a separate claim that deserves
its own sentence and its own evidence.

Look for sentence-final `-ing`: ensuring, highlighting, underscoring,
reflecting, contributing to, allowing for, fostering, showcasing.

> The cache is invalidated on write. A reader arriving mid-write sees the
> old value, which is why the read path takes the lock.

## Excess parallelism

Balanced structure above the rate of natural writing, at word, phrase,
sentence and paragraph level. The rule of three is the common case:

> It is fast, reliable, and easy to maintain.

Three adjectives imply a completeness never established. Give the one that
carries weight, and say why it holds.

## Negative parallelism

> This is **not just** a config change, **it is** a change in ownership.
> The problem is **not** the syntax, **but** the assumption behind it.

The construction manufactures a reveal. A real contrast occasionally needs
it; three on one page means none of them are real.

## Significance inflation

> This **plays a crucial role** in the build.
> The change **underscores the importance** of validation.

`underscores` runs about 11× its pre-2022 rate, `delve` 28×, `showcasing`
10× (Kobak et al., 2025). The vocabulary follows the habit: asserting that
something matters instead of showing what it does.

`serves as`, `stands as`, `functions as`, `represents`, `boasts`,
`features` — all `is` wearing a coat. Use `is`.

## Formatting

**Inline-header bullets.** `- **Term**: description` is the most
recognisable shape in machine-written documentation. Keep it for genuine
key-value data. When the descriptions are sentences, write sentences.

**Bold by default.** Bolding every scannable term emphasises nothing.

**Title Case Headings.** Sentence case, unless the project already differs.

**Em dashes.** Not forbidden, overused. More than one per paragraph is a
rhythm, and the rhythm is the tell.

## Content

**Elegant variation.** Swapping synonyms to avoid repetition damages
technical writing specifically: a `cache`, a `store` and a `layer` are
three things. Repeat the noun.

**Vague attribution.** `Industry reports suggest`, `best practice is`.
Cite it, measure it, or own it as your judgement.

**Hedging without information.** `This may potentially help in some cases`
says nothing. `This helps when the working set exceeds RAM` does.

---

# 日本語

英語の一覧は使えない。日本語の兆候は語彙より**文末・接続・段落の閉じ方**に出る。

## 文末が同型で続く

最も出やすい。「〜できる」「〜である」「〜します」が等間隔で連続し、リズムが一定になる。

> キャッシュは書き込み時に破棄されます。読み取りはロックを取得します。
> 整合性が保たれます。

人間が書くと文の長さも語尾も揺れる。**3 文続けて同じ語尾なら疑う。**

## 「〜ことで」構文

英語の分詞句後置に相当する日本語の癖。

> マーカーを検証する**ことで**、無言の失敗を防いでいます。
> shim を経由する**ことで**、バージョンが固定されます。

前半と後半の因果が自明なら、後半は情報を足していない。切って、因果が非自明な部分だけ書く。

> マーカーが無ければ落とす。無ければ、ローカルの ignore が消えた設定が
> 正常に生成される。

## 判断を保留する語尾

> 〜と言えるでしょう / 〜ではないでしょうか / 場合によります /
> 一概には言えません / 〜が求められます

技術文書で条件を書かずにぼかすのは、読者に判断を投げているだけ。**条件を書く。**

> 5 万行を超えるとインデックスが効かなくなる。それ未満なら問題ない。

## 抽象語の多用

「重要」「有効」「最適」「価値」「〜性」「〜化」。定義せずに使うと、何も言っていない文になる。

> 保守性が向上します → 設定が 1 箇所になり、変更時に触るファイルが 3 つから 1 つになる

## 接続詞が過剰

「また」「さらに」「そして」「したがって」を各文頭に置くと、論理の接続が丁寧すぎて進行感が消える。**繋がりが自明なら接続詞は要らない。**

## 段落が毎回きれいに閉じる

段落の末尾で必ずまとめに入る。人間の技術文書は、次の段落に continue する形で終わることが多い。

## 見出しの内容を本文冒頭で繰り返す

> ## PATH の予算
> PATH の予算について説明します。

見出しが既に言っている。本文は事実から始める。

## 英語圏の記法が混入する

- 文末のコロン（`以下のとおりです：`）は日本語の習慣にない
- 半角スペースで単語を区切る
- 箇条書きが `**用語**: 説明` になる

## メリット・デメリットの並列で終わる

利点と欠点を対称に並べて、**どちらを選んだかを書かない**。技術文書で必要なのは選択と理由。

---

## 自分の草稿を検査する

**英語** — 文末だけを縦に読む。分詞句と significance inflation は両方そこに出る。

200 語あたりで数える。

- 文末 `-ing` 節
- 三つ組
- `not X but Y`
- `- **Bold**:` 行
- em dash

**日本語** — 文末だけを縦に読む。同じ語尾が続いていないか。

200 字あたりで数える。

- 同一語尾の連続
- 「〜ことで」
- 「〜でしょう」「〜ではないでしょうか」
- 文頭の接続詞
- 定義なしの「重要」「最適」「〜性」

どちらも、1 つなら文体。複数が重なると信号になる。

## 長さ

削ると上のほとんどが同時に消える。これらのパターンは、**書くことが尽きた後に紙面を埋めるもの**だから。後置分詞も、三つ組も、締めの段落も、内容の終わりを越えて書き続けるための手段になっている。

3 分の 1 削って事実が 1 つも減らないなら、その語数が兆候だった。

## 兆候ではないもの

正しい綴り。正確に使われた長い語。一貫した書式。内容の形に沿った構造。平明に書いて正しいことは、直す対象ではない。
