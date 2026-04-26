# MCP Servers Configuration

このディレクトリには、Kaggle MCP サーバーの設定テンプレートが含まれています。

## Kaggle MCP とは

Kaggle MCP は、Kaggle API への統合アクセスを提供する MCP（Model Context Protocol）サーバーです。これを設定することで、Claude Code、Cursor、Gemini などから直接 Kaggle のコンペティションやデータセットにアクセスできます。

## ファイル

- `.mcp.json` — Claude Code / VS Code / Cursor 向け MCP 設定
- `config.toml` — Codex 向け MCP 設定

## 認証

両方の設定で `KAGGLE_API_TOKEN` 環境変数を使用します。これは以下で設定：

```bash
export KAGGLE_API_TOKEN="your-kaggle-api-token"
```

または `.env` ファイルに記入：

```
KAGGLE_API_TOKEN=your-kaggle-api-token
```

## セットアップ

### Claude Code / VS Code / Cursor

`.mcp.json` をプロジェクトルートにコピーしてください：

```bash
cp .agents-source/.agents/mcp/.mcp.json ./mcp.json
```

**既存の `.mcp.json` がある場合は、`mcpServers.kaggle` セクションをマージしてください：**

```json
{
  "mcpServers": {
    "your-existing-server": { ... },
    "kaggle": {
      "type": "http",
      "url": "https://www.kaggle.com/mcp",
      "headers": {
        "Authorization": "Bearer ${KAGGLE_API_TOKEN}"
      }
    }
  }
}
```

### Codex

`config.toml` をマージしてください：

```toml
[mcp_servers.kaggle]
url = "https://www.kaggle.com/mcp"
bearer_token_env_var = "KAGGLE_API_TOKEN"
enabled = true
```

Codex の設定ファイルは通常 `~/.config/codex/config.toml` です。

## Kaggle API Token の取得

1. [Kaggle.com](https://kaggle.com) にログイン
2. 右上のプロフィール → "Settings"
3. 左サイドバー → "API"
4. "Create New API Token" をクリック
5. ダウンロードされた `kaggle.json` から `key` をコピー
6. `.env` に設定：`KAGGLE_API_TOKEN=<key>`

## トラブルシューティング

### MCP が接続できない場合

- `KAGGLE_API_TOKEN` が正しく設定されているか確認
- トークンが有効期限切れでないか確認
- インターネット接続を確認
- エディタを再起動してみる

### 複数の MCP サーバーを使用する場合

`.mcp.json` に複数のサーバーを指定できます：

```json
{
  "mcpServers": {
    "kaggle": { ... },
    "notion": { ... },
    "github": { ... }
  }
}
```

各サーバーに対して、認証情報（環境変数）を設定してください。
