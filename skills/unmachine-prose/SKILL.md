---
name: unmachine-prose
description: Write technical documentation that does not read as machine-generated. The tells are mostly structural, they differ between English and Japanese, and they are recognised when several stack in one passage rather than from any single word. Use when writing a README, an ADR, a commit message, a design document, a note or a PR body, and when revising prose that reads as generic despite being correct. Also fires when writing or reviewing a bilingual documentation pair, and when delegating any such writing — the language-specific checklists must travel inside the delegation prompt, or they will not be applied.
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
英語から乗ってくるのも、記法より**修辞**のほうが被害が大きい。

## 比喩と擬人化が英語から乗ってくる

英語の技術文書は、物を主語にして人の動詞を与えるのが標準の書き方になっている。
日本語の技術文書ではならない。英語の比喩をそのまま訳すと擬人化になり、読みにくい
訳文の匂いだけが残る。

| 訳した比喩 | 元の英語 | 事実を書く |
|---|---|---|
| shim の**値段** | what a shim costs | shim を経由すると何 ms 増えるか |
| 実行が終わるまで**居座る** | stays in the middle | 実行が終わるまでプロセスとして残る |
| リンクは**腐る** | the link goes stale | リンク先が消えればリンクは切れる |
| 選ばなかったほうの**枝** | the wrong branch | 候補は 2 つあり、片方を選んだ |
| この仕掛けが**太らせる** | feeds this | 該当するウィンドウが増える |
| 原因候補が**手元にある** | is always available | 毎月あるので必ず見つかる |
| 最後にやったことを**肯定する** | confirms whatever you did last | 直後が順調なら対処に見える |

判定は 1 つ。**主語が物なのに、人にしか使わない動詞が付いていないか。** 居座る、
肯定する、待つ、太る、腐る、語る、知っている、抱える、背負う。付いていたら、その
動詞が指している観測事実に書き換える。

見出しでも同じ。日本語の技術見出しは、比喩より内容の名指しのほうが強い。

## 英語で書いてから訳している

上の兆候はまとめて 1 つの原因から出る。英語の草稿を作ってから日本語にする、その
手順そのもの。用語だけでなく語順と比喩が付いてくる。

日本語版は、同じ事実から日本語で書き直す。訳すのは用語だけにする。

見分け方は、日本語だけを読んで元の英語が透けるかどうか。無生物主語が続く、
関係代名詞をそのまま連体修飾に伸ばした長い主語、「〜のほうが〜」の多用。

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

## タイトルが冒頭の 1 節だけを指している

書きながら付けたタイトルは、最初に書いた節に引っ張られる。5 節ある記事の
1 節目が bat の不具合なら「bat が返ってこない理由」になり、残り 4 節を約束から
外してしまう。

**要約文と突き合わせる。** 要約は書き終えてから付けるので、たいてい要約のほうが
記事全体を正しく言っている。タイトルと要約が別のことを言っていたら、直すのは
タイトル。

> title: bat が返ってこない理由は shim だった
> summary: mise のツールを symlink 経由で起動している理由と、それができない 60 本

見出しを縦に並べて、タイトルが全部を覆っているかも見る。覆えていなければ、記事が
実際に主張していることを名指しする。

## 英語圏の記法が混入する

- 文末のコロン（`以下のとおりです：`）は日本語の習慣にない
- 半角スペースで単語を区切る
- 箇条書きが `**用語**: 説明` になる

## メリット・デメリットの並列で終わる

利点と欠点を対称に並べて、**どちらを選んだかを書かない**。技術文書で必要なのは選択と理由。

## 削っただけだと lorem ipsum になる

ここまでの禁止だけを適用すると、正しくて何も言っていない文が並ぶ。比喩を外した跡に
一般的な動詞を置くと、比喩が運んでいた情報のぶんだけ薄くなる。

| 外した比喩 | 置いた語（薄い） | 事実を戻した形 |
|---|---|---|
| 間に居座る | 間に残ります | ツールが終わるまで shim も終了しない |
| これを太らせる | 該当ウィンドウを増やします | 送られた先で即 cloak されるので件数が増える |
| いつでも手元にある | 見つかります | ほぼ毎月あるので、どの月の症状にも当たる |

判定は文単位。**その 1 文を消して、読者が失う事実はあるか。** 無ければ、比喩を
外した跡地が残っているだけ。

もう 1 つ出やすいのが否定の連鎖。「壊れていません」「説明がつきません」「入りま
せん」が並ぶと、成り立たないことの列挙で段落が終わる。**言えることは肯定で書く。**

- 「バイナリは壊れていません」→「同じ実行ファイルを直接叩けば普通に動きました」
- 「遅さでは説明がつきません」→「遅いだけならプロンプトは返ってくる」

対象そのものが不在や不成立なら、否定が並ぶのは正しい。cloak されたウィンドウの話で
「z オーダーを上げても出てこない」は事実そのもの。数で判定できるものではない。

日本語の技術文が読める形になるのは、1 文ごとに具体（数値、コマンド名、実際の動作）
が入っているとき。禁止を守っただけでは足りない。

---

## 二言語ペアを書くとき

二言語のドキュメントペアで最も多い事故は、片方の言語で書いてから
もう片方へ訳すこと。上の「英語で書いてから訳している」は、ペア執筆では
例外ではなく既定の手順になりやすい — 「両言語に同じ編集を」という
作業指示そのものが翻訳を招く。

- **各言語版は、共有した事実の列から別々に書く。** 訳してよいのは用語
  だけ。語順・比喩・構文が原文から乗ってきたら、それは訳した証拠。
- **検査は言語ごとに、その言語のリストで行う。** ペアの片側だけ検査して
  もう片側を「同じ内容だから」で通さない。日本語を英語のリストで検査
  しても何も出ない。
- **執筆を委譲するなら、チェックリストを指示文に載せる。** サブエージェント
  や同僚はこのスキルを読んでいない。指示は「両言語に同じ編集を」ではなく
  「同じ事実を、各言語の慣習で書く」とし、対象言語の検査項目を添える。

実例。二言語 README をペアで書いた結果、日本語側に「チェックアウトの中で
しか動かない」「プロトコルを話す」「読んでいる場所によって違う」が残り、
レビューの指摘まで誰も気づかなかった。どれも英語草稿が透けた訳文で、
日本語として読み直していれば書かない形をしている。

## 自分の草稿を検査する

**英語** — 文末だけを縦に読む。分詞句と significance inflation は両方そこに出る。

200 語あたりで数える。

- 文末 `-ing` 節
- 三つ組
- `not X but Y`
- `- **Bold**:` 行
- em dash

**日本語** — 2 回読む。1 回目は文末だけを縦に、同じ語尾が続いていないか。2 回目は
主語と動詞の組だけを拾い、物が主語の文に人の動詞が付いていないか。

200 字あたりで数える。

- 同一語尾の連続
- 物が主語の意志動詞（居座る、肯定する、待つ、腐る）
- 「〜ことで」
- 「〜でしょう」「〜ではないでしょうか」
- 文頭の接続詞
- 定義なしの「重要」「最適」「〜性」

**薄さは数えても出ない。** 敬体で書けば文末が「ます・です」に寄るのは当たり前で、
その比率は良く書けた文章でも 9 割を超える。文末の分布や文長の分散を閾値にすると、
問題の無い文章まで引っかかる。

かわりに、段落ごとに 1 文選んで消してみる。**消して困らない文が続いていたら、それが
lorem ipsum の実体。** 比喩を外した跡地はここに出る。

どちらも、1 つなら文体。複数が重なると信号になる。

日本語は、書いた本人が英語の草稿を持っているときほど検出が難しい。元の文が頭に
残っていると、訳したものが自然に読める。**英語を見ずに日本語だけを読む**のが唯一の
検査になる。

## 長さ

削ると上のほとんどが同時に消える。これらのパターンは、**書くことが尽きた後に紙面を埋めるもの**だから。後置分詞も、三つ組も、締めの段落も、内容の終わりを越えて書き続けるための手段になっている。

3 分の 1 削って事実が 1 つも減らないなら、その語数が兆候だった。

## 兆候ではないもの

正しい綴り。正確に使われた長い語。一貫した書式。内容の形に沿った構造。平明に書いて正しいことは、直す対象ではない。

日本語の誤り一般も、ここには入らない。二重敬語、主述のねじれ、「の」の連続、表記
ゆれは人間も同じだけ犯すもので、機械が書いた兆候ではない。それらは
`plain-japanese` が扱う。両方を順に当てるのはよいが、混ぜるとどちらの検査も鈍る。
