# インストール

Node.js 20 以上が必要です。

1. パッケージを入れる。

   ```
   npm install -g cachectl
   ```

2. 設定ファイルを作る。

   ```
   cachectl init
   ```

   カレントディレクトリに `cache.toml` ができる。

3. 接続を確かめる。

   ```
   cachectl ping
   ```

   `PONG` と表示されれば完了。
