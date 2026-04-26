<!--
2026-04-27-birdclef-2026-discussion-research.md
Where: docs/discussion.
What: Kaggle discussion research summary for BirdCLEF+ 2026.
Why: Preserve actionable ideas and source links from topics, comments, and writeups.
-->

# BirdCLEF+ 2026 Discussion Research

- 取得日: 2026-04-27
- 対象: BirdCLEF+ 2026 (`birdclef-2026`)
- 依頼: birdclef2026の有益な情報を綿密にまとめる
- 調査範囲: `search_competitions("birdclef-2026")`、`list_forum_topics` の Top/Hot/Recent/Active page 1、validation補完検索、既存メモの再統合、`get_forum_topic(includeComments=true)` による本文+コメント読解
- 候補数: 24 collected / 11 read / 7 skim-or-skip noted / 6 unreviewed
- 注意: `context()` MCP は利用不可。`search_content(documentTypes=["Topic"])` は Kernel/Dataset が混ざるため補助用途に限定した。`list_forum_topics` は `searchQuery="birdclef-2026"` 付きだと sort を変えても先頭集合がかなり似るため、実際には page 2 やテーマ検索で差分を作る必要がある。

## 結論

- host が明確にしている今年の差分は、`train_soundscapes_labels.csv` を使った soundscape supervision が validation の土台になったことと、Perch v2 のような強い pretrained model を前提にして良いこと。この2点が 2025 との一番大きい差分。
- ルール/データ面で重要なのは、`train_soundscapes_labels.csv` の duplicate removal、exact site coordinate 非公開、test は train soundscapes と同じ大枠 deployment だが unseen location を含むこと、hidden test は約600本の1分音源であること。
- 実装の主流は `HGNetV2-B0 + LSE/SED` 系と `Perch v2 distillation / embedding probe` 系に二極化している。前者は再現性のある公開 baseline が多く、後者は public LB を押し上げやすいが推論時間と実装複雑度が高い。
- public LB だけを見て 5秒窓・高CV AUC を信じると外しやすい。generalization を壊している原因として、soundscape holdout の少なさ、rare class の偏り、5秒単位の local eval の楽観、label block の連続性が繰り返し指摘されている。
- 推論高速化は OpenVINO や ONNX が有望だが、どちらも Torch/TensorFlow と完全一致ではない。まずは reproducibility を固定し、その上で ONNX 化、TTA batching、audio prefetch、weight publish 分離を入れるのが順序として安全。

## 実装ヒント

- data:
  - `train_soundscapes_labels.csv` は重複除去を前提に読む。host は「追加ラベルではなく duplicate removal」と説明している。
  - soundscape labels は単なる補助ではなく、一部クラスにとって主要 train source になりうる。`train_audio` に無い class をここで拾う前提で設計する。
  - site 名は使えるが exact coordinate は非公開。geo feature を入れるなら train_audio 側の緯度経度と soundscape 側の site 名を混同しない。
- training:
  - HGNetV2-B0 baseline は 32kHz、`n_fft=2048`、`hop_length=313`、`n_mels=256`、4-fold、MixUp、AdamW、Cosine 系 scheduler の公開 recipe がある。
  - `hengck23` 系では Perch v2 ONNX を feature extractor にし、stop-gradient distillation、site/time prior、temporal smoothing を重ねる流れが繰り返し出ている。
  - yukiZ の baseline では reproducibility fix が強く意識されており、PyTorch 初期化、MixUp/CutMix の RNG、Dropout を放置しない。
- validation:
  - labeled soundscapes は local eval に使えるが、test と完全同分布ではない。same overall deployment だが unseen recording location が test にある。
  - high CV AUC がそのまま LB に移らない報告が多い。soundscape-only holdout、5秒窓の短すぎる評価、rare class 欠落 fold の扱いを見直す。
  - SGKF と rare class binning の組み合わせは有効な実装例として共有されている。
- inference:
  - hidden test は約600本 x 60秒、提出は 12 個の5秒 window 単位。sample submission から shape を合わせるのが安全。
  - ONNX 化、`ThreadPoolExecutor` による audio prefetch、TTA batching、training と inference notebook の分離は、時間制約の厳しい提出で効いている。
  - OpenVINO は速いが、Torch との差分で score 退行リスクがある。ONNX でも logit は5桁程度で差が出る。
- postprocess:
  - temporal filtering、smoothing kernel、site/time prior は public LB では効いた報告が多い。
  - label block の連続性を使う後処理は BirdCLEF 2026 特有の signal になっている。

## 候補一覧

| 判定 | 優先 | topic id | title | 発見元 | votes | comments | 理由 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| read | high | 680383 | Welcome to BirdCLEF+ 2026 - Meet the hosts | Top, Recent | 30 | 21 | host 確定情報がコメントに多い |
| read | high | 680906 | Direct Validation? | validation search | 12 | 17 | soundscape validation の役割を host が明言 |
| read | high | 681000 | Google Perch model is quite good as a baseline | Top, Recent | 46 | 16 | Perch baseline と distill 論点の起点 |
| read | high | 681297 | `train_soundscapes_labels.csv` has duplicated records | Top, Recent | 35 | 16 | duplicate removal の確定情報 |
| read | high | 683822 | An example of training process (HGNetV2-B0 Baseline) | Top, Recent | 57 | 31 | 再現可能 baseline と follow-up が多い |
| read | high | 684148 | [placeholder] tricks in BirdCLEF+ 2026 | Top, Recent | 22 | 19 | 2026特有の連続 block / prior 仮説 |
| read | high | 685318 | warping perchv2 inside pytorch for training | Top, Recent | 58 | 16 | Perch ONNX 埋め込みと distillation の具体案 |
| read | high | 686457 | Sharing baseline LB.928. Aiming to achieve both reproducibility and inference speed | Top, Recent | 35 | 8 | reproducibility と timeout 対策の具体例 |
| read | high | 689012 | Compare Inference Speed of Torch, Torch-jit-trace, OpenVINO | Top, Recent | 28 | 4 | 推論速度と精度差の比較 |
| read | medium | 690556 | Generalization Issues | validation search | 2 | 3 | local AUC と LB の乖離に対する具体経験 |
| read | medium | 691539 | LB stuck at 0.865, any improvement makes LB drop drastically | validation search | 1 | 12 | public LB で壊れやすい変更の失敗例 |
| read | high | 694479 | Distilled SED Baseline (0.912 LB) | Top, Recent | 19 | 5 | distillation 派生 baseline と cache 実務 |
| skim | medium | 680267 | How to get started + Competition's Official Discord | Existing memo | 9 | 1 | 公式導線と sharing rule のみ |
| skim | medium | 683791 | What is your best single model LB score ? | Top | 41 | 114 | chatter が多く、深掘り効率が悪い |
| skim | medium | 682951 | are we becoming Obsolete!? | Top | 17 | 31 | AI 雑談寄り、実装根拠が薄い |
| skim | medium | 684207 | Is everyone using LLM tools (i.e. GPT, Gemini, Claude)? | Top | 52 | 108 | 一般論中心 |
| skip | low | 681125 | Acknowledge Bird Sound Recordists of BirdCLEF 2026 | Top | 48 | 6 | 謝辞中心 |
| skip | low | 682718 | Animal images BirdCLEF+ 2026 | Top | 4 | 0 | 主題外 |
| skip | low | 688386 | Swarm Intelligence Prediction for BirdCLEF 2026 | Top | 7 | 1 | 再現可能な手法議論ではない |

## Topic別メモ

### Welcome to BirdCLEF+ 2026 - Meet the hosts

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/680383
- topic id: 680383
- votes/comments: 30/21
- 要点:
  - 公式ホスト thread だが、本当に重要なのはコメント欄の補足。
  - exact site location は保護上の理由で非公開。site names だけ提供される。
  - test と train soundscapes は同じ overall deployment に属するが、test には train soundscapes に無い recording location もある。
  - hidden test は約600本の1分音源で、提出は 12 個の5秒 window を埋める前提。
- 重要コメント:
  - Stefan Kahl (2026-03-19, comment 3423969): hidden test は around 600。https://www.kaggle.com/competitions/birdclef-2026/discussion/680383#3423969
  - Tom Denton (2026-03-22, comment 3426468): 1分音源 x 12 segment と sample submission を再確認。https://www.kaggle.com/competitions/birdclef-2026/discussion/680383#3426468
  - Tom Denton (2026-04-02, comment 3434385): test には train soundscapes に無い location が含まれる。https://www.kaggle.com/competitions/birdclef-2026/discussion/680383#3434385
  - Stefan Kahl (2026-04-13, comment 3440961): exact site location は非公開、site names は類似音環境を示す意図。https://www.kaggle.com/competitions/birdclef-2026/discussion/680383#3440961
- 信頼度: 高 - host 確定情報

### Direct Validation?

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/680906
- topic id: 680906
- votes/comments: 12/17
- 要点:
  - BirdCLEF 2026 では初めて labeled soundscapes を validation の足場として扱える。
  - ただし、単なる easy holdout ではなく、ここにしか train sample がない class がある。
  - time-frequency boxed annotation のような richer label が欲しいという参加者の声もある。
- 重要コメント:
  - Tom Denton (2026-03-11, comment 3419799): train_soundscapes と labels 提供を再確認。https://www.kaggle.com/competitions/birdclef-2026/discussion/680906#3419799
  - Stefan Kahl (2026-03-11, comment 3419807): BirdCLEF 初の validation data と明言。https://www.kaggle.com/competitions/birdclef-2026/discussion/680906#3419807
  - Stefan Kahl (2026-03-15, comment 3421327): labeled soundscapes は local eval の基盤であり、一部 class はここにしか train sample が無い。https://www.kaggle.com/competitions/birdclef-2026/discussion/680906#3421327
  - Stefan Kahl (2026-03-11, comment 3419827): annotations 自体は bounding box 由来だが、配布形式は既存 dataset に合わせた。https://www.kaggle.com/competitions/birdclef-2026/discussion/680906#3419827
- 信頼度: 高 - host 回答が具体的

### Google Perch model is quite good as a baseline

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/681000
- topic id: 681000
- votes/comments: 46/16
- 要点:
  - 更新版 Perch は 203/234 種に対応し、starter で 0.825 LB、推論は約90分という報告。
  - 強い zero-shot-ish baseline だが、そのままでは遅い。
  - classifier head を直接足すより、embedding distillation や lightweight student への蒸留の話に流れている。
- 重要コメント:
  - Konstantin Dmitriev (2026-03-13, comment 3420430): Perch は baseline としては強いが遅く、最終的には学習済み CNN の方が良いと示唆。https://www.kaggle.com/competitions/birdclef-2026/discussion/681000#3420430
  - Konstantin Dmitriev (2026-03-15, comment 3420750): fine-tune/custom head/TFLite の方向性を補足。https://www.kaggle.com/competitions/birdclef-2026/discussion/681000#3420750
  - hengck23 (2026-03-17, comment 3422238): unlabeled soundscapes を含めて embedding を作り、student model に distill する案。https://www.kaggle.com/competitions/birdclef-2026/discussion/681000#3422238
  - IvanYakovlev (2026-03-25, comment 3428731): precached embeddings 依存は closed test で危険ではないかと注意喚起。https://www.kaggle.com/competitions/birdclef-2026/discussion/681000#3428731
- 信頼度: 中 - 強い参加者観測が多いが host 確定ではない

### `train_soundscapes_labels.csv` has duplicated records

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/681297
- topic id: 681297
- votes/comments: 35/16
- 要点:
  - `train_soundscapes_labels.csv` に完全重複があり、host は duplicate removal だけを行うと明言。
  - 参加者側では、同一 timestamp に矛盾ラベルがありうるという観測も出ている。
- 重要コメント:
  - Stefan Kahl (2026-03-17, comment 3422218): 追加ラベルではなく duplicate removal。https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3422218
  - Stefan Kahl (2026-03-19, comment 3423971): every entry has a duplicate を再確認。https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3423971
  - Fernandosr85 (2026-03-19, comment 3424366): 同一 timestamp に矛盾ラベルがあり AUC を壊す可能性を指摘。https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3424366
- 信頼度: 高 - host 回答あり

### An example of training process (HGNetV2-B0 Baseline)

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/683822
- topic id: 683822
- votes/comments: 57/31
- 要点:
  - Tawara が training/inference notebook と主要 hyperparameter を共有。
  - HGNetV2-B0 に LSE/AttnSED、TTA、必要 window のみ切り出す audio loader で baseline を構築。
  - follow-up コメントがそのまま改善ロードマップになっている。
- 重要コメント:
  - hengck23 (2026-03-22, comment 3426626): `train_audio + train_soundscapes` は `clip only` より大きく良いと補足。https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3426626
  - hengck23 (2026-03-27, comment 3429672): 同一 backbone でも `LSE head` が LB で有利と補足。https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3429672
  - hengck23 (2026-03-28, comment 3430379): LSE base 0.876、postprocess 追加で 0.883、Perch distill 追加で 0.898。https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3430379
  - MengYe (2026-04-03, comment 3434544): smoothing kernel を共有し 0.891 LB。https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3434544
  - MengYe (2026-04-08, comment 3438256): 5秒から10秒へ伸ばして 0.90+ LB。https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3438256
- 信頼度: 中 - notebook と追試があるが private 再現は不明

### [placeholder] tricks in BirdCLEF+ 2026

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/684148
- topic id: 684148
- votes/comments: 22/19
- 要点:
  - `hengck23` は 2026 の本質を「Perch などの強い pretrained model」と「annotated soundscapes」に置いている。
  - label が 10-40 秒の連続 block で現れること、相関した label 群があることを利用した後処理や prior が有効と示唆。
  - AUC の fold ごとの揺れと rare class scarcity を強く警告している。
- 重要コメント:
  - hengck23 (2026-03-31, comment 3432205): label count / auc / source 別集計 CSV を作って分析せよと提案。https://www.kaggle.com/competitions/birdclef-2026/discussion/684148#3432205
  - hengck23 (2026-04-01, comment 3433231): same fold でも hyperparameter で AUC が大きく揺れると説明。https://www.kaggle.com/competitions/birdclef-2026/discussion/684148#3433231
  - hengck23 (2026-04-09, comment 3438465): rare class 欠落 fold の bug から、少数 class が LB を大きく落とすと観測。https://www.kaggle.com/competitions/birdclef-2026/discussion/684148#3438465
  - hengck23 (2026-04-09, comment 3438482): missing class nulling bug を補足。https://www.kaggle.com/competitions/birdclef-2026/discussion/684148#3438482
- 信頼度: 中 - 強い洞察だが participant 仮説も混ざる

### warping perchv2 inside pytorch for training

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/685318
- topic id: 685318
- votes/comments: 58/16
- 要点:
  - Perch v2 ONNX を CUDA I/O binding で PyTorch pipeline に埋め込み、embedding/spatial_embedding を直接使う実装。
  - stop-gradient distillation が中心で、ONNX を分割して spect augmentation と両立させる案まで出ている。
- 重要コメント:
  - hengck23 (2026-03-28, comment 3430354): `35k clip + 66 soundscapes` を使った stop-gradient distill の意図を説明。https://www.kaggle.com/competitions/birdclef-2026/discussion/685318#3430354
  - hengck23 (2026-03-28, comment 3430592): stop-gradient を外すと 0.889、spatial embed 直結 MLP は 0.885。https://www.kaggle.com/competitions/birdclef-2026/discussion/685318#3430592
  - Lixin73 (2026-04-15, comment 3442180): ONNX と PyTorch 変換後 embedding の cosine/MAE 差がほぼゼロ。https://www.kaggle.com/competitions/birdclef-2026/discussion/685318#3442180
- 信頼度: 高 - 実装断片と追試コメントが具体的

### Sharing baseline LB.928. Aiming to achieve both reproducibility and inference speed

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/686457
- topic id: 686457
- votes/comments: 35/8
- 要点:
  - yukiZ が reproducibility と inference timeout を同時に潰す baseline を継続更新。
  - seed 管理、Dropout、MixUp/CutMix の RNG fix、training notebook の分離、TTA batching、vectorized probe、audio prefetch が主題。
  - 4月6日時点では ONNX 化と async audio loading で scoring time 23分まで短縮。
- 重要コメント:
  - yukiZ (2026-04-04, comment 3435716): GKF から SGKF + rare class binning に変更して LB .926 -> .928。https://www.kaggle.com/competitions/birdclef-2026/discussion/686457#3435716
  - yukiZ (2026-04-06, comment 3436508): ONNX + `ThreadPoolExecutor(max_workers=4)` + `intra_op_num_threads=4` で 23分。https://www.kaggle.com/competitions/birdclef-2026/discussion/686457#3436508
  - yukiZ (2026-04-12, comment 3440510): ONNX は許容範囲の誤差で、時間制約上はこちらを推奨。https://www.kaggle.com/competitions/birdclef-2026/discussion/686457#3440510
- 信頼度: 中 - participant 実装だが具体性が高い

### Compare Inference Speed of Torch, Torch-jit-trace, OpenVINO

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/689012
- topic id: 689012
- votes/comments: 28/4
- 要点:
  - Torch / TorchScript / OpenVINO の速度比較。
  - OpenVINO は最速だが Torch と出力差があるため、そのまま採用は危険。
- 重要コメント:
  - Ali Ozan Memetoglu (2026-04-15, comment 3442571): ONNX でも十分動くと補足。https://www.kaggle.com/competitions/birdclef-2026/discussion/689012#3442571
- 信頼度: 中 - ベンチ条件依存が強い

### Generalization Issues

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/690556
- topic id: 690556
- votes/comments: 2/3
- 要点:
  - local soundscape CV 0.9 でも LB 0.7 になる例。
  - held-out soundscape windows は same site / same hour 由来で楽観的になりうる、という指摘が重要。
  - 20秒窓 + 一部 labeled soundscapes 混入で改善した報告もあるが、これは participant 観測に留まる。
- 重要コメント:
  - OpPrime (2026-04-12, comment 3440499): held-out soundscape windows は optimistic、held-out clips の方が honest と指摘。https://www.kaggle.com/competitions/birdclef-2026/discussion/690556#3440499
  - alex142857 (2026-04-12, comment 3440519): train soundscapes は全種をカバーしないのではと補足。https://www.kaggle.com/competitions/birdclef-2026/discussion/690556#3440519
- 信頼度: 低 - participant 議論のみ

### LB stuck at 0.865, any improvement makes LB drop drastically

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/691539
- topic id: 691539
- votes/comments: 1/12
- 要点:
  - 典型的な failure mode 集。
  - waveform MixUp、longer input、pseudo-labeling、different backbones、site/hour prior が public LB を落とした例が並ぶ。
  - コメント側では、raw waveform / Perch embedding 側が incremental に効いた、MixUp では normalization をミスると壊れる、という具体的な失敗知見が出ている。
- 重要コメント:
  - OpPrime (2026-04-15, comment 3442332): mel image path ではなく raw/perch embedding の方が上がった経験。https://www.kaggle.com/competitions/birdclef-2026/discussion/691539#3442332
  - Alexander Gremyakov (2026-04-15, comment 3442389): waveform MixUp では equal normalization を崩すと quiet sample が消える。https://www.kaggle.com/competitions/birdclef-2026/discussion/691539#3442389
  - Alexander Gremyakov (2026-04-15, comment 3442402): waveform mix の EDA 画像を共有。https://www.kaggle.com/competitions/birdclef-2026/discussion/691539#3442402
- 信頼度: 低 - 失敗談として有用だが確定情報ではない

### Distilled SED Baseline (0.912 LB)

- URL: https://www.kaggle.com/competitions/birdclef-2026/discussion/694479
- topic id: 694479
- votes/comments: 19/5
- 要点:
  - Tucker Arrants が `hengck23` 由来の stop-gradient distillation を SED pipeline に移植。
  - smoothing と temporal shift TTA を重ね、public LB 0.920 まで持っていったと報告。
  - waveform / embedding cache による学習高速化も明示。
- 重要コメント:
  - Tucker Arrants (2026-04-25, comment 3448423): ProtoSSM trend より distilled CNN の方が BirdCLEF tricks を載せやすい middle ground と説明。https://www.kaggle.com/competitions/birdclef-2026/discussion/694479#3448423
  - Tucker Arrants (2026-04-25, comment 3448482): `.pt` waveform cache を作る前処理コードを共有。https://www.kaggle.com/competitions/birdclef-2026/discussion/694479#3448482
- 信頼度: 中 - 派生実装だが改善幅と実務ノウハウが具体的

## 未確認・リスク

- `681146` と `683791` はコメント量が多く、まだ深掘りしきれていない。上位参加者の断片知見が埋もれている可能性はある。
- `684148` の continuous block / ecological prior の一部は participant 仮説であり、private LB での有効性は未確定。
- `690556` と `691539` の generalization 話は participant 経験談なので、そのまま普遍化しない方がいい。
- ONNX/OpenVINO の速度改善は魅力だが、出力差と Kaggle 混雑依存がある。再現性 fix より前に最適化へ寄ると切り分け不能になる。
- external data、site/time prior、pseudo-labeling は discussion 上では触れられているが、最終実装前に official rules の再確認が必要。

## Source Index

| 種別 | id | title/comment | URL | メモ |
| --- | --- | --- | --- | --- |
| competition | 129329 | BirdCLEF+ 2026 | https://www.kaggle.com/competitions/birdclef-2026 | `search_competitions` で解決 |
| topic | 680383 | Welcome to BirdCLEF+ 2026 - Meet the hosts | https://www.kaggle.com/competitions/birdclef-2026/discussion/680383 | host thread |
| comment | 3423969 | around 600 hidden test | https://www.kaggle.com/competitions/birdclef-2026/discussion/680383#3423969 | host |
| comment | 3426468 | sample submission / 12 windows | https://www.kaggle.com/competitions/birdclef-2026/discussion/680383#3426468 | host |
| comment | 3434385 | unseen test locations | https://www.kaggle.com/competitions/birdclef-2026/discussion/680383#3434385 | host |
| comment | 3440961 | site coordinates hidden | https://www.kaggle.com/competitions/birdclef-2026/discussion/680383#3440961 | host |
| topic | 680906 | Direct Validation? | https://www.kaggle.com/competitions/birdclef-2026/discussion/680906 | validation |
| comment | 3419807 | first validation data | https://www.kaggle.com/competitions/birdclef-2026/discussion/680906#3419807 | host |
| comment | 3419827 | bbox labels were used internally | https://www.kaggle.com/competitions/birdclef-2026/discussion/680906#3419827 | host |
| comment | 3421327 | some classes only in soundscapes | https://www.kaggle.com/competitions/birdclef-2026/discussion/680906#3421327 | host |
| topic | 681000 | Google Perch model is quite good as a baseline | https://www.kaggle.com/competitions/birdclef-2026/discussion/681000 | Perch baseline |
| comment | 3420750 | custom head / TFLite mention | https://www.kaggle.com/competitions/birdclef-2026/discussion/681000#3420750 | participant |
| comment | 3422238 | distill instead of head | https://www.kaggle.com/competitions/birdclef-2026/discussion/681000#3422238 | participant |
| comment | 3428731 | precached embedding caution | https://www.kaggle.com/competitions/birdclef-2026/discussion/681000#3428731 | participant |
| topic | 681297 | duplicated records | https://www.kaggle.com/competitions/birdclef-2026/discussion/681297 | data cleaning |
| comment | 3422218 | duplicate removal only | https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3422218 | host |
| comment | 3423971 | every entry duplicated | https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3423971 | host |
| comment | 3424366 | contradictory labels | https://www.kaggle.com/competitions/birdclef-2026/discussion/681297#3424366 | participant |
| topic | 683822 | HGNetV2-B0 Baseline | https://www.kaggle.com/competitions/birdclef-2026/discussion/683822 | baseline |
| comment | 3426626 | clip + soundscape improves baseline | https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3426626 | participant |
| comment | 3429672 | LSE head advantage | https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3429672 | participant |
| comment | 3430379 | LSE + postprocess + distill | https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3430379 | participant |
| comment | 3434544 | smoothing kernel | https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3434544 | participant |
| comment | 3438256 | 10-second segment | https://www.kaggle.com/competitions/birdclef-2026/discussion/683822#3438256 | participant |
| topic | 684148 | tricks in BirdCLEF+ 2026 | https://www.kaggle.com/competitions/birdclef-2026/discussion/684148 | heuristic |
| comment | 3432205 | label count / auc analysis | https://www.kaggle.com/competitions/birdclef-2026/discussion/684148#3432205 | participant |
| comment | 3433231 | AUC swings by hyperparameter | https://www.kaggle.com/competitions/birdclef-2026/discussion/684148#3433231 | participant |
| comment | 3438465 | rare classes hurt LB | https://www.kaggle.com/competitions/birdclef-2026/discussion/684148#3438465 | participant |
| comment | 3438482 | nulling bug | https://www.kaggle.com/competitions/birdclef-2026/discussion/684148#3438482 | participant |
| topic | 685318 | warping perchv2 inside pytorch for training | https://www.kaggle.com/competitions/birdclef-2026/discussion/685318 | distillation |
| comment | 3430354 | stop-gradient distill setup | https://www.kaggle.com/competitions/birdclef-2026/discussion/685318#3430354 | participant |
| comment | 3430592 | no-stop-grad vs stop-grad | https://www.kaggle.com/competitions/birdclef-2026/discussion/685318#3430592 | participant |
| comment | 3442180 | ONNX/PyTorch embedding match | https://www.kaggle.com/competitions/birdclef-2026/discussion/685318#3442180 | participant |
| topic | 686457 | reproducibility and inference speed | https://www.kaggle.com/competitions/birdclef-2026/discussion/686457 | baseline |
| comment | 3435716 | SGKF + rare class binning | https://www.kaggle.com/competitions/birdclef-2026/discussion/686457#3435716 | participant |
| comment | 3436508 | ONNX 23 min | https://www.kaggle.com/competitions/birdclef-2026/discussion/686457#3436508 | participant |
| comment | 3440510 | ONNX accuracy drift explanation | https://www.kaggle.com/competitions/birdclef-2026/discussion/686457#3440510 | participant |
| topic | 689012 | Torch vs TorchScript vs OpenVINO | https://www.kaggle.com/competitions/birdclef-2026/discussion/689012 | speed |
| comment | 3442571 | ONNX also works | https://www.kaggle.com/competitions/birdclef-2026/discussion/689012#3442571 | participant |
| topic | 690556 | Generalization Issues | https://www.kaggle.com/competitions/birdclef-2026/discussion/690556 | validation gap |
| comment | 3440499 | optimistic soundscape holdout | https://www.kaggle.com/competitions/birdclef-2026/discussion/690556#3440499 | participant |
| comment | 3440519 | train soundscapes coverage concern | https://www.kaggle.com/competitions/birdclef-2026/discussion/690556#3440519 | participant |
| topic | 691539 | LB stuck at 0.865 | https://www.kaggle.com/competitions/birdclef-2026/discussion/691539 | failure modes |
| comment | 3442332 | raw/perch helped more | https://www.kaggle.com/competitions/birdclef-2026/discussion/691539#3442332 | participant |
| comment | 3442389 | waveform MixUp normalization | https://www.kaggle.com/competitions/birdclef-2026/discussion/691539#3442389 | participant |
| comment | 3442402 | waveform mix EDA | https://www.kaggle.com/competitions/birdclef-2026/discussion/691539#3442402 | participant |
| topic | 694479 | Distilled SED Baseline | https://www.kaggle.com/competitions/birdclef-2026/discussion/694479 | distillation |
| comment | 3448423 | distilled CNN vs ProtoSSM | https://www.kaggle.com/competitions/birdclef-2026/discussion/694479#3448423 | participant |
| comment | 3448482 | waveform cache preprocessing | https://www.kaggle.com/competitions/birdclef-2026/discussion/694479#3448482 | participant |
