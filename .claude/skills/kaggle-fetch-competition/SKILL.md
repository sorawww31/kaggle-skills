---
name: kaggle-fetch-competition
description: Kaggle MCPなどで現在のリポジトリが対象にしているKaggleコンペを特定し、公式ページ、データ説明、ルール、評価、提出制約、賞金、開催履歴、Discussion候補を取得してREADME冒頭へ要約する。ユーザーが「Kaggleコンペ情報をfetch」「READMEにコンペ概要を追加」「BirdCLEFなど参加中コンペの情報をまとめて」「discussionから有用情報を拾って」などを依頼したときに使う。
---

<!--
SKILL.md
Where: .agents/skills/kaggle-fetch-competition.
What: Fetch Kaggle competition context and update README.
Why: Keep experiment repositories grounded in current official competition docs.
-->

# Kaggle Fetch Competition

このSkillは、Kaggle MCPを優先して参加中コンペの公式情報を集め、READMEのタイトル直下に短いコンペ概要を作るための手順を定める。
Kaggle上の情報は変わるため、推測だけでREADMEを書かず、取得元と取得日を明記する。

## 前提確認

1. リポジトリ内のREADME、config、実験ディレクトリ名、環境変数名からコンペslug候補を探す。
2. ユーザーがslugや年を明示した場合はそれを優先する。例: `birdclef-2026`。
3. Kaggle MCPツールが未ロードなら、tool discoveryでKaggle competition/search/page/data file系ツールを探す。
4. `context()` MCPが使える環境なら、Kaggle APIや利用ライブラリの挙動確認に使う。使えない場合は「context MCPは利用不可」と明示し、Kaggle MCPまたは公式Kaggleページで確認する。
5. READMEに未コミット差分がある場合は、既存差分を読んでから編集範囲を限定する。

## 情報取得

次をKaggle MCPで取得する。

1. コンペ検索:
   - `search_content`でslug候補を検索する。
   - `document_type == COMPETITION`、slug、title、subtitle、deadline、team_count、team_rank、prize、joined/bookmarked状態を確認する。
   - 検索結果が混ざる場合は、`document_type`とslug一致だけを採用する。
2. 公式ページ:
   - `list_competition_pages(competitionName=<slug>)`を呼ぶ。
   - 優先して読むページ: `abstract`、`Description`、`data-description`、`Timeline`、`Evaluation`、`rules`、`Prizes`、`Code Requirements`、`Acknowledgements`。
   - ルール本文は長いので、READMEには参加・提出・外部データ・ライセンス・コード要件だけを要約する。
3. データファイル:
   - `list_competition_data_files(competitionName=<slug>, pageSize=100)`を呼ぶ。
   - 全ファイルを貼らず、トップレベルファイルと主要ディレクトリ単位で要約する。
   - 音声・画像など大量ファイルは件数例、命名規則、サンプリング仕様を`data-description`から補う。
4. Discussion:
   - `search_content`で`documentTypes=["Topic"]`、`discussionFilters.sourceType="Competition"`、可能なら`competitionIds`を指定して検索する。
   - 取得結果は必ず`document_type == TOPIC`だけを採用する。
   - Kaggle MCPがTopicに絞れずKernelやBenchmarkを返す場合は、READMEに憶測を書かず「Discussion候補はMCP検索で未確定」とする。
   - 公式KaggleのDiscussionページをブラウズできる環境では、Kaggle公式URLだけを使って上位/新着/host投稿を確認する。
5. 開催履歴:
   - 年次コンペならslugの年を差し替え、`birdclef-2026`なら`birdclef-2025`、`birdclef-2024`のように候補を作る。
   - 各候補について`search_content`または`list_competition_pages`で存在確認する。
   - 存在確認できた年、title、subtitle、地域/対象、評価・データ上の大きな違いだけを短くまとめる。

## README更新

READMEの冒頭だけを更新し、既存の環境構築・実験管理説明は維持する。

1. タイトル直後に`## コンペ概要`を置く。既に同名セクションがあればそこだけ更新する。
2. 概要セクションは次の順にする。
   - 取得日、コンペURL、Kaggle slug。
   - 目的: 何を予測するコンペか。
   - データ: 主要ファイル、学習/テスト構造、隠しテストの注意。
   - 評価・提出: metric、submission形式、Notebook/CPU/Internetなどの制約。
   - 重要ルール: 外部データ、データライセンス、チーム/提出上限、最終期限。
   - 開催履歴: 確認できた過去年と大きな違い。
   - Discussionメモ: 確認できたTopicだけ。未確認ならその旨。
3. 原文の長い引用は避け、要約する。短い固有名詞、ファイル名、metric名はそのまま使う。
4. 取得元はKaggle公式URLまたはKaggle MCPページ名として明記する。
5. ユーザーの既存README差分を戻さない。

## BirdCLEF向けの注意

BirdCLEF系では次を特に確認する。

- 年ごとに地域、対象分類群、ラベル数、データ構成、評価実装が変わる。
- `test_soundscapes`は提出Notebook実行時に隠しテストが配置されることがある。
- 5秒窓ごとのmulti-label確率提出か、species列数はいくつかを確認する。
- 外部データは「公開かつ参加者全員が合理的にアクセス可能」か、コンペ固有ルールと矛盾しないかを確認する。
- Xeno-canto、iNaturalistなど元データサイトへの負荷やスクレイピング規約に注意する。

## 検証

1. 編集後にREADMEとSKILL.mdを読み直し、見出し順とMarkdownの崩れを確認する。
2. skillを追加した場合は、skill-creatorの`quick_validate.py`で対象skillを検証する。
3. `.claude`など同期生成物は、ユーザーが明示しない限り編集しない。
4. 最後に`git diff -- README.md .agents/skills/kaggle-fetch-competition`を確認し、変更範囲を報告する。
