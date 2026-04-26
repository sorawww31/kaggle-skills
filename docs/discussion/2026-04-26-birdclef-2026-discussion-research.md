<!--
2026-04-26-birdclef-2026-discussion-research.md
Where: docs/discussion.
What: Kaggle discussion research summary for BirdCLEF+ 2026.
Why: Preserve actionable ideas and source links from topics, comments, and writeups.
-->

# BirdCLEF+ 2026 Discussion Research

- 取得日: 2026-04-26
- 対象: BirdCLEF+ 2026 (`birdclef-2026`)
- 依頼: 公開 Discussion を広く見て、実装に使える投稿を Markdown にまとめる
- 調査範囲: `list_forum_topics` の Top/Hot/Recent/Active page 1、Recent page 2、Admin Recent、`search_content(documentTypes=["Topic"], canonicalOrderBy="DateUpdated")`
- 候補数: 40 collected / 6 read / 8 skim-or-skip noted / 26 unreviewed
- 注意: `context()` MCP は利用不可。`get_forum(forumSlug="birdclef-2026")` は `forums.get` denied。`search_content(documentTypes=["Topic"])` は Kernel/Dataset が混ざるため `document_type` と `parent_url` で topic のみ採用した。`list_forum_topics` は `searchQuery="birdclef-2026"` 付きだと sort を変えても先頭集合がかなり似ていた。

## 結論

- 公式に確定しているデータ修正は `train_soundscapes_labels.csv` の重複削除で、追加ラベル投入ではない。soundscape 学習時は重複前提で集計しない。
- 公開ベースラインで再現性が高い流れは、`HGNetV2-B0 + LSE/AttnSED` 系と `Perch v2 distillation` 系に収束している。
- 推論高速化は OpenVINO が最速だが、Tawara の計測では Torch と出力差があり score 悪化リスクがある。まず TorchScript、次に OpenVINO を検証するのが無難。
- Perch v2 を学習に取り込む実装は、ONNX I/O binding の feature extractor 化と stop-gradient distillation が実用段階まで共有されている。

## 実装ヒント

- データ:
  - `train_soundscapes_labels.csv` は重複削除を前処理に入れる。
  - 重複は単純 row 数の問題だけでなく、同一 timestamp に矛盾ラベルが混ざる可能性も議論されているので、soundscape 由来 validation は目視確認する。
- 学習:
  - HGNetV2-B0 baseline は 32kHz, `n_fft=2048`, `hop_length=313`, `n_mels=256`, `lms_shape=(256, 256)`, 4-fold, MixUp, AdamW, OneCosineLR で共有されている。
  - `hengck23` のコメントでは HGNetV2-B0 に LSE head を載せると LB 0.876、postprocess 追加で 0.883、Perch distill 追加で 0.898 まで伸びた。
  - Tawara の baseline では 5 秒窓から 2.5 秒 shift TTA を加えて fold avg 0.888 まで上がっている。
- Distillation / feature extraction:
  - `hengck23` は Perch v2 ONNX を CUDA I/O binding で直接 feature extractor 化している。
  - ONNX を wave-to-spect と spect-to-latent に分割し、SpecAug 下で distillation する発想まで共有されている。
  - `Tucker Arrants` は stop-gradient SED 分離で一貫して `+0.02 LB` と報告し、事前 embedding cache で学習時間を削れると明記した。
- 推論:
  - Tawara の比較では OpenVINO は Torch の約 2 倍速だが、出力差があるため本番提出前に score 退行を要確認。
  - TorchScript は Torch よりやや速く、互換性面ではまずこちらを試す価値が高い。

## 候補一覧

| 判定 | 優先 | topic id | title | 発見元 | votes | comments | last activity | 理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| read | high | 681297 | `train_soundscapes_labels.csv` has duplicated records | Top, Hot, Recent, Active | 35 | 16 | 2026-04-08 | host が duplication removal を明言 |
| read | high | 683822 | An example of training process (HGNetV2-B0 Baseline) | Top, Hot, Recent, Active | 57 | 31 | 2026-04-13 | 再現可能な training baseline と follow-up コメントが多い |
| read | high | 685318 | warping perchv2 inside pytorch for training | Top, Hot, Recent, Active | 58 | 16 | 2026-04-15 | Perch ONNX / distillation の具体コードあり |
| read | high | 689012 | Compare Inference Speed of Torch, Torch-jit-trace, OpenVINO | Top, Hot, Recent, Active | 28 | 4 | 2026-04-15 | 推論速度と score 劣化リスクを比較 |
| read | high | 694479 | Distilled SED Baseline (0.912 LB) | Top, Hot, Recent, Active | 19 | 5 | 2026-04-25 | distillation の派生 baseline と前処理の補足あり |
| read | medium | 680267 | How to get started + Competition's Official Discord | Recent, Admin | 9 | 1 | 2026-03-23 | staff の公式導線と public/private sharing rule |
| skim | medium | 681000 | Google Perch model is quite good as a baseline | Top, Hot, Recent, Active | 46 | 16 | 2026-03-28 | ベースライン価値は高いが今回は派生議論を優先 |
| skim | medium | 683791 | What is your best single model LB score ? | Top, Hot, Recent, Active, search_content | 41 | 114 | 2026-04-26 | スコア共有は多いが raw leaderboard chatter も多い |
| skim | medium | 680906 | Direct Validation? | Recent | 12 | 17 | 2026-03-16 | validation 設計の議論候補 |
| skip | low | 681202 | My notebook submissions "succeed" but find no files in test_soundscapes | Recent | 6 | 5 | 2026-03-18 | 個人環境の提出/実行エラー中心 |
| skip | low | 681227 | Where do I find the Log file for my submission? | Recent | 7 | 2 | 2026-03-14 | UI/提出ログの質問のみ |
| skip | low | 684505 | Cannot submit to BirdCLEF+ 2026 - persistent rate limit for 14+ hours | Recent | 1 | 1 | 2026-03-25 | 一時的な submit 障害報告 |
| skip | low | 680949 | Make competition available for users in Syria | Recent | 8 | 2 | 2026-03-12 | 実装ヒントに直結しない運営依頼 |

## Topic別メモ

### `train_soundscapes_labels.csv` has duplicated records

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/681297
- topic id: 681297
- votes/comments: 35/16
- 要点:
  - Tawara が `train_soundscapes_labels.csv` に完全重複 739 行があると報告。
  - host Stefan Kahl が「追加ラベルはなく、duplicate を削除する」と明言している。
  - 参加者側では、同一 timestamp に矛盾ラベルが混ざるケースが validation を壊す可能性も指摘されている。
- 重要コメント:
  - Stefan Kahl (2026-03-17, comment 3422218): 追加ラベルはなく duplicate を削除するだけ。https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3422218
  - Stefan Kahl (2026-03-19, comment 3423971): 各 entry の duplicate を remove する方針を再確認。https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3423971
  - Fernandosr85 (2026-03-19, comment 3424366): 同一 file/timestamp に別 class が乗る例を報告し、AUC が壊れる可能性を指摘。https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3424366
- 信頼度: 高 - host 回答あり

### An example of training process (HGNetV2-B0 Baseline)

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/683822
- topic id: 683822
- votes/comments: 57/31
- 要点:
  - Tawara が training/inference notebook と主要 hyperparameter を公開。
  - LSE head と TTA 追加で public LB を 0.888 まで改善。
  - `.ogg` 全読込より必要 5 秒のみを `soundfile` で切り出す実装と、事前 wav 変換で data loader ボトルネックを潰している。
- 重要コメント:
  - hengck23 (2026-03-28, comment 3430379): LSE base 0.876 に対し、TTA + temporal filtering + site/time prior で 0.883、Perch distill 追加で 0.898。https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3430379
  - MengYe (2026-04-03, comment 3434544): smoothing kernel を共有し 0.891 LB を報告。https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3434544
  - MengYe (2026-04-08, comment 3438256): segment を 5 秒から 10 秒へ伸ばして 0.90+ LB と報告。https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3438256
- 信頼度: 中 - 公開 notebook と複数参加者追試あり、ただし closed test での再現は未確認

### warping perchv2 inside pytorch for training

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/685318
- topic id: 685318
- votes/comments: 58/16
- 要点:
  - `hengck23` が Perch v2 ONNX を CUDA I/O binding で PyTorch pipeline に埋め込むコードを共有。
  - 5 秒窓の音声から `embedding` と `spatial_embedding` を直接引き出し、feature extractor / online distillation に使う。
  - ONNX を 2 つに分割して spect augmentation と distillation を両立させる発想も共有されている。
- 重要コメント:
  - hengck23 (2026-03-28, comment 3430592): stop-gradient を外すと 0.889、ONNX spatial embed 直結 MLP で 0.885 と補足。https://www.kaggle.com/competitions/birdclef-2026/discussion/685318#3430592
  - Lixin73 (2026-04-15, comment 3442180): ONNX と PyTorch 変換後 embedding の cosine/MAE 差がほぼゼロであることを報告。https://www.kaggle.com/competitions/birdclef-2026/discussion/685318#3442180
- 信頼度: 高 - コード断片と追試コメントが具体的

### Compare Inference Speed of Torch, Torch-jit-trace, OpenVINO

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/689012
- topic id: 689012
- votes/comments: 28/4
- 要点:
  - Tawara が 600 ogg を使って Torch / TorchScript / OpenVINO を複数回ベンチマーク。
  - OpenVINO は Torch 比で概ね 2 倍速いが、Torch と出力差があるので score 劣化注意と結論。
- 重要コメント:
  - Ali Ozan Memetoglu (2026-04-15, comment 3442571): ONNX でも十分動くと補足。https://www.kaggle.com/competitions/birdclef-2026/discussion/689012#3442571
- 信頼度: 中 - ベンチは具体的だが hardware/worker 条件依存が強い

### Distilled SED Baseline (0.912 LB)

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/694479
- topic id: 694479
- votes/comments: 19/5
- 要点:
  - Tucker Arrants が `hengck23` 由来の stop-gradient distillation を自分の SED pipeline に移植。
  - 同一 model 比で `+0.02 LB`、smoothing と temporal shift TTA まで含めると 0.920 public LB と報告。
  - 学習高速化には waveform / embedding の事前 cache が有効。
- 重要コメント:
  - Tucker Arrants (2026-04-25, comment 3448423): ProtoSSM trend と比べて、distilled CNN は既存 BirdCLEF tricks を使いやすい middle ground と説明。https://www.kaggle.com/competitions/birdclef-2026/discussion/694479#3448423
  - Tucker Arrants (2026-04-25, comment 3448482): `.pt` waveform cache を作る前処理コードを共有。https://www.kaggle.com/competitions/birdclef-2026/discussion/694479#3448482
- 信頼度: 中 - 派生実装だがコードと改善幅が具体的

### How to get started + Competition's Official Discord

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/680267
- topic id: 680267
- votes/comments: 9/1
- 要点:
  - Kaggle staff Ashley Oldacre が公式 Discord を案内。
  - Discord competition channels は public 扱いで、private code/data sharing は不可。
  - 重要な質問や知見は forum に残すよう明記されている。
- 信頼度: 高 - staff 投稿

## 未確認・リスク

- `list_forum_topics` の searchQuery 付き sort は Top/Hot/Recent/Active の差が薄く、広く見るには page2 以降や Admin、`search_content` の併用が必要。
- `search_content(documentTypes=["Topic"])` は Topic 以外も返したため、そのまま topic 候補表に混ぜると誤る。
- まだ未読 topic が多い。特に `Direct Validation?`, `soundscape adaptation`, `best single model LB` は追加追跡余地がある。
- 公開 LB 改善コメントは多いが、private leaderboard で効くかは別。site/time prior や smoothing は leakage にならない形で適用条件を再確認する。

## Source Index

| 種別 | id | title/comment | URL | メモ |
| --- | --- | --- | --- | --- |
| topic | 680267 | How to get started + Competition's Official Discord | https://www.kaggle.com/competitions/birdclef-2026/discussion/680267 | staff の公式導線 |
| topic | 681297 | `train_soundscapes_labels.csv` has duplicated records | https://www.kaggle.com/competitions/birdclef-2026/discussion/681297 | host が duplicate removal を回答 |
| comment | 3422218 | duplicate removal only | https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3422218 | host 確定情報 |
| comment | 3423971 | every entry has a duplicate | https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3423971 | host 再確認 |
| comment | 3424366 | contradictory labels on same timestamp | https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3424366 | 参加者観測 |
| topic | 683822 | An example of training process (HGNetV2-B0 Baseline) | https://www.kaggle.com/competitions/birdclef-2026/discussion/683822 | 公開 baseline |
| comment | 3430379 | LSE + postprocess + distill follow-up | https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3430379 | `hengck23` の改善案 |
| comment | 3434544 | smoothing weights | https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3434544 | 後処理 |
| comment | 3438256 | 10-second segment | https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3438256 | 参加者追試 |
| topic | 685318 | warping perchv2 inside pytorch for training | https://www.kaggle.com/competitions/birdclef-2026/discussion/685318 | Perch ONNX 利用 |
| comment | 3430592 | no-stop-grad / direct MLP results | https://www.kaggle.com/competitions/birdclef-2026/discussion/685318#3430592 | 追加実験 |
| comment | 3442180 | ONNX vs PyTorch embedding match | https://www.kaggle.com/competitions/birdclef-2026/discussion/685318#3442180 | 変換検証 |
| topic | 689012 | Compare Inference Speed of Torch, Torch-jit-trace, OpenVINO | https://www.kaggle.com/competitions/birdclef-2026/discussion/689012 | 推論速度比較 |
| comment | 3442571 | onnx also works | https://www.kaggle.com/competitions/birdclef-2026/discussion/689012#3442571 | 参加者補足 |
| topic | 694479 | Distilled SED Baseline (0.912 LB) | https://www.kaggle.com/competitions/birdclef-2026/discussion/694479 | 派生 baseline |
| comment | 3448423 | distilled CNN vs ProtoSSM | https://www.kaggle.com/competitions/birdclef-2026/discussion/694479#3448423 | 参加者質問への回答 |
| comment | 3448482 | waveform cache preprocessing | https://www.kaggle.com/competitions/birdclef-2026/discussion/694479#3448482 | 前処理コード |
