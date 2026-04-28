# Kaggle Skills & MCP

Kaggle 向けの AI-agent スキルと MCP サーバー設定を提供します。Claude Code、Cursor、Gemini で使用可能です。

## 📦 含まれるもの

### Skills
- `new-exp` — 新しい実験ディレクトリの作成
- `commit` — Git コミット補助
- `kaggle-fetch-competition` — Kaggle コンペティションデータの取得
- `kaggle-discussion-research` — Kaggle Discussion とコメントの調査記録
- `kaggle-to-notion` — Kaggle データを Notion に連携
- `plan-create` — 実装プラン作成
- `empirical-prompt-tuning` — プロンプトチューニング
- `skill-creator` — 新しいスキルの作成
- その他

### MCP Servers
- **Kaggle MCP** — Kaggle API への統合アクセス（`KAGGLE_API_TOKEN` で認証）

## 🚀 既存プロジェクトに追加する

### 方法1: Submodule を使う（推奨）

```bash
# リポジトリのルートで実行
git submodule add https://github.com/sorawww31/kaggle-skills.git .agents-source

# 親リポジトリのルートで一括導入
python .agents-source/sync_agent_assets.py
```

この 1 コマンドで以下を同期します：
- `./.agents/skills/` に共有スキルをコピー
- `./.codex/skills/` にも同じ共有スキルをコピー
- `./sync_agent_assets.py` を配置
- `./.mcp.json` に Kaggle MCP 設定を追加
- `./.codex/config.toml` に Kaggle Codex 設定を追加
- `.claude/`, `.cursor/`, `.gemini/`, `.github/` 向け生成ファイルを更新

Codex 設定は共有テンプレート `.agents-source/.agents/mcp/config.toml`（互換パス: `.agents-source/.codex/config.toml`）から生成されます。
既存の `.mcp.json` は他サーバーを残したまま `kaggle` を追加します。既存の `.codex/config.toml` にすでに `[mcp_servers.kaggle]` がある場合は上書きせず、その旨を表示します。
プロジェクトルートに `AGENTS.md` がある場合、`CLAUDE.md` などの指示ファイルは `.agents-source/AGENTS.md` ではなく、その `AGENTS.md` から生成します。

### 方法2: セットアップスクリプトを使う

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/kaggle-project/kaggle-skills/master/setup-kaggle-skills.sh)
```

## ⚙️ セットアップ

### 1. Kaggle API トークンを設定

```bash
echo "export KAGGLE_API_TOKEN=your-token-here" >> .env
```

または `.env.example` をコピーして編集：

```bash
cp .env.example .env
# .env を編集して KAGGLE_API_TOKEN を記入
```

### 2. Sync を実行（Submodule の場合）

```bash
# 親リポジトリのルートで実行
python .agents-source/sync_agent_assets.py
```

これで以下が自動生成されます：
- `./.agents/skills/` — Codex 用の共有スキル
- `./.codex/skills/` — Codex ローカル設定配下にも置く共有スキル
- `./sync_agent_assets.py` — 以後の更新用スクリプト
- `./.mcp.json` — Claude Code / Cursor 向け Kaggle MCP 設定
- `./.codex/config.toml` — Codex 向け Kaggle MCP 設定
- `.claude/skills/` — Claude Code 用スキル
- `.cursor/commands/` — Cursor 用コマンド
- `.gemini/commands/` — Gemini CLI 用コマンド

### Sync オプション

```bash
# スキル + 指示ファイルを同期（デフォルト）
python .agents-source/sync_agent_assets.py

# MCP 設定も含めて同期（⚠️ 既存設定を上書き）
python .agents-source/sync_agent_assets.py --mcp

# スキルのみ同期（指示ファイルをスキップ）
python .agents-source/sync_agent_assets.py --skills

# チェック（生成ファイルが最新か確認）
python .agents-source/sync_agent_assets.py --check

# 不要なファイルを削除
python .agents-source/sync_agent_assets.py --prune
```

**各オプションの説明:**
- `--mcp` — MCP サーバー設定（`.cursor/mcp.json`, `.vscode/mcp.json`, `.gemini/settings.json`）も生成します。⚠️ 既存の MCP 設定を上書きします
- `--skills` — 指示ファイル（`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/project-guidelines.mdc`）の生成をスキップ。プロジェクト側 `AGENTS.md` からの自動生成を止めたい場合に使用
- `--check` — 生成ファイルが最新かチェック（修正は行わない）
- `--prune` — 不要になった生成ファイルを削除

## 📖 使用例

### Claude Code での使用

```
/new-exp exp=002  # 新しい実験を作成
/commit "fix: bug in training loop"  # コミット補助
```

### Kaggle データの取得

```
/kaggle-fetch-competition competition-name
```

### Kaggle Discussion の調査

```
/kaggle-discussion-research <competition-slug> の有用Discussionを docs/discussion にまとめて
```

## 🔗 MCP（Model Context Protocol）サーバー設定

**重要**: Kaggle スキルを最大限活用するには、MCP サーバーの設定が必須です。

### MCP とは

MCP は、Claude や Cursor などの AI エディタが、外部 API（Kaggle など）に統合アクセスするためのプロトコルです。これを設定することで、エディタ内から直接 Kaggle コンペティションやデータセットを操作できます。

### セットアップ方法

詳細は [`.agents/mcp/README.md`](.agents/mcp/README.md) を参照してください。

**簡潔な手順：**

1. **新規プロジェクト（MCP 設定がない場合）**
   ```bash
   # 親リポジトリのルートで実行
   python .agents-source/sync_agent_assets.py --mcp
   ```

2. **既存プロジェクト（MCP 設定がある場合）**
   ルートの `.mcp.json` は自動マージされます。Codex の `./.codex/config.toml` は、`[mcp_servers.kaggle]` が未定義なら自動追加されます。

   `--mcp` は、そのマージ後のルート `.mcp.json` を元に、以下の生成ファイルも更新します：
   
   **Claude Code / Cursor** — `.cursor/mcp.json`
   ```json
   {
     "mcpServers": {
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
   
   **VS Code** — `./.vscode/mcp.json`
   ```json
   {
     "servers": {
       "kaggle": {
         "url": "https://www.kaggle.com/mcp",
         "type": "http",
         "headers": {
           "authorization": "Bearer ${KAGGLE_API_TOKEN}"
         }
       }
     }
   }
   ```
   
   **Gemini CLI** — `.gemini/settings.json`
   ```json
   {
     "mcpServers": {
       "kaggle": {
         "type": "http",
         "httpUrl": "https://www.kaggle.com/mcp",
         "headers": {
           "Authorization": "Bearer ${KAGGLE_API_TOKEN}"
         }
       }
     }
   }
   ```
   
   **Codex** — `./.codex/config.toml`
   ```toml
   [mcp_servers.kaggle]
   url = "https://www.kaggle.com/mcp"
   bearer_token_env_var = "KAGGLE_API_TOKEN"
   enabled = true
   ```

   ⚠️ `--mcp` は以下の生成ファイルを上書きします：
   - `.cursor/mcp.json`
   - `.vscode/mcp.json`
   - `.gemini/settings.json`

3. **認証情報の設定**
   ```bash
   # .env に Kaggle API Token を設定
   echo "KAGGLE_API_TOKEN=your-token-here" >> .env
   ```

### Kaggle API Token の取得

1. [Kaggle.com](https://kaggle.com) にログイン
2. 右上のプロフィール → "Settings"
3. 左サイドバー → "API"
4. "Create New API Token" をクリック
5. ダウンロードされた `kaggle.json` から `key` をコピー

詳細は [`.agents/mcp/README.md`](.agents/mcp/README.md) の「Kaggle API Token の取得」セクションを参照。

## 🔄 更新

Submodule で追加した場合、最新版に更新：

```bash
git submodule update --remote .agents-source

# 親リポジトリのルートで実行
python .agents-source/sync_agent_assets.py
```

### MCP 設定を更新する場合

```bash
# ルートの .mcp.json / .codex/config.toml / .agents/skills / .codex/skills を更新
python .agents-source/sync_agent_assets.py

# 生成先の MCP ファイル (.cursor/.vscode/.gemini) も更新する場合
python .agents-source/sync_agent_assets.py --mcp
```

## 📝 ライセンス

MIT

## 💬 サポート

問題が発生した場合は、GitHub Issues で報告してください。

---

**Note**: このリポジトリは [sync_agent_assets.py](tools/sync_agent_assets.py) を使用して、複数の AI エディタ向けにアセットを自動生成しています。
