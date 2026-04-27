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

通常は、親リポジトリのルートで以下を実行すれば十分です：

```bash
python .agents-source/sync_agent_assets.py
```

このコマンドが `.mcp.json` を自動更新します。さらに `--mcp` を付けると、そのマージ後の `.mcp.json` を元に `.cursor/mcp.json`、`.vscode/mcp.json`、`.gemini/settings.json` も生成します。手動で反映したい場合は、以下の内容をプロジェクトルートにコピーしてください：

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

通常は `python .agents-source/sync_agent_assets.py` が `./.codex/config.toml` へ Kaggle 設定を追加します。手動で反映する場合は、以下をマージしてください：

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
