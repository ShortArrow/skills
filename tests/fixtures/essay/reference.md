# キャッシュ設定リファレンス

`cache.toml` に書ける項目。
既定値は、項目を省略したときの値である。

| 項目 | 既定値 | 説明 |
|---|---|---|
| `cache.backend` | `memory` | 保存先。`memory` か `redis` |
| `cache.max_entries` | `10000` | 保持するエントリ数の上限 |
| `cache.key_prefix` | `app:` | すべてのキーに付ける接頭辞 |
| `redis.url` | `redis://localhost:6379` | `redis` のときの接続先 |
| `redis.timeout` | `2s` | Redis への接続と応答のタイムアウト |
| `metrics.enabled` | `true` | ヒット率と件数の集計を出すか |
