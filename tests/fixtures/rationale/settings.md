# 設定リファレンス

エージェントの設定ファイル `agent.toml` に書ける項目。
既定値は、項目を省略したときの値である。

| 項目 | 既定値 | 説明 |
|---|---|---|
| `spool.path` | `/var/lib/logagent/spool` | スプールファイルの置き場所 |
| `spool.limit` | `256MB` | スプールの容量上限 |
| `spool.flush_bytes` | `4KB` | スプールへまとめて書き込む単位 |
| `server.url` | （必須） | 収集サーバーの URL |
| `server.timeout` | `30s` | 接続と送信のタイムアウト |
| `send.interval` | `10s` | 送信を試みる間隔 |
| `send.batch` | `500` | 一度の送信に含めるエントリの上限 |
| `log.level` | `info` | エージェント自身のログの詳細度 |
