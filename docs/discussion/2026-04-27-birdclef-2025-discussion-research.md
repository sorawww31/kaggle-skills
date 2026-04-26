<!--
2026-04-27-birdclef-2025-discussion-research.md
Where: docs/discussion.
What: Kaggle discussion research summary for BirdCLEF+ 2025 gold-medal methods.
Why: Preserve actionable ideas and source links from top writeups, comments, and supporting discussions.
-->

# BirdCLEF+ 2025 Gold Medal Methods Research

- 取得日: 2026-04-27
- 対象: BirdCLEF+ 2025 (`birdclef-2025`)
- 依頼: birdclef2025のgold メダル手法の調査
- 調査範囲: `list_forum_topics` の `CompetitionWriteUps` Top/Recent page 1、`Competitions` Top/Recent page 1、`get_forum_topic(includeComments=true)`、`get_writeup_by_topic`
- 候補数: 19 collected / 5 read / 8 skim-or-skip noted / 6 unreviewed
- 注意: `context()` MCP は利用不可。`search_content(documentTypes=["Competition"])` は Competition ではなく Kernel を返し、`search_competitions("birdclef-2025")` も空だったため、`list_forum_topics` の `parent_name` と `topic_url` から対象コンペを確定した。`BirdClef+ 2025 Learnings and Trends` は `birdclef-2026` 配下だったため除外した。

## 結論

- gold 帯で共通していたのは、`SED head + mel spectrogram + unlabeled soundscapes/self-distillation + overlap inference + smoothing` という骨格だった。
- 1位は `Multi-Iterative Noisy Student` を最も深く回し、疑似ラベルへ power transform を掛けて 4 iteration まで伸ばした。5位は `train_audio` の unlabeled secondary label を self-distillation で埋め、3段目で `train_soundscapes` を 1:1 混合した。13位も簡潔ながら同じ方向で、pseudo data と rare-species model を主因に挙げている。
- `human voice` 対策と `rare class` 補強は上位解法の共通要素だった。ただし 1位は「human voice removal は悪化した」と明記しており、ここは単純な前処理でなく、データのどの群に効くかを切り分ける必要がある。
- 外部データは rare class に効くが、BirdCLEF 2025 では host が `CC-BY` 系だけでなく `NC/ND` も許容した一方、`Macaulay` は不可と明言している。追加データを使うなら source 公開と再配布性の確認が前提。

## 実装ヒント

- モデル:
  - 1位は 20 秒入力の SED、`tf_efficientnet_b0/b3/b4`, `regnety_008/016`, `eca_nfnet_l0` を段階的に投入した。
  - 5位は 10 秒入力の SED、`tf_efficientnetv2_s`, `tf_efficientnetv2_b3`, `tf_efficient_b3_ns`, `tf_efficient_b0_ns` を多本数 ensemble した。
  - 13位は `v2s` を主力にしつつ `v2_b3` と `seresnext26t` を追加した。
- 特徴量:
  - 1位は `sr=32000`, `mel_bins=224`, `n_fft=4096`, `hop_size=1252`, `fmax=16000`, 20 秒 `(3, 224, 512)` を採用した。
  - 5位は `sr=32000`, `mel_bins=192`, `fmin=20`, `fmax=15000`, `window_size=2048`, `hop_size=768` の 10 秒 log-mel を採用した。
  - 高 vote の early baseline でも「melspec 調整だけで 0.810 -> 0.859」とされており、BirdCLEF 2025 では mel 設計の寄与が大きい。
- 学習:
  - 1位は supervised で `CrossEntropy + AdamW + CosineAnnealingWarmRestarts`、raw audio MixUp、以降は pseudo-labeled soundscapes を 20 秒 chunk で混ぜる noisy-student へ移行した。
  - 5位は `FocalLoss(gamma=2)` と mel-domain `Sumix` を使い、`train_audio only` の self-distillation を 4-5 回、その後 `train_soundscapes` も入れて 2 回追加した。
  - 13位も 2023 2nd solution 系の SED を起点に、5 秒 pseudo clip を `train_audio` に random sample して大きく伸ばした。
- データ:
  - 5位は `Silero VAD + 手動試聴` で human voice を除去し、underrepresented class では手動で bird-call 区間を拾っている。
  - 1位は target species 追加 Xeno-Canto と、Amphibia/Insecta 専用の extra species データを使い分けた。
  - rare class 補強 discussion では、external data を Kaggle dataset として再配布し、ライセンス不適合ファイルを除去する運用が共有されている。
- 推論:
  - 1位と 5位の両方で `overlap inference + neighboring chunk average + smoothing` が効いている。
  - 1位は `delta shift TTA`、5位は `2.5-second overlap` と `[0.1, 0.8, 0.1]` smoothing を使った。
  - 1位と 5位の両方が `OpenVINO` を採用している。
- 検証:
  - 1位は `CV/LB correlation` を見いだせず public LB 中心で評価した。
  - 5位も段階ごとの public LB 推移を指標に self-distillation 回数を決めている。
  - したがって、再現時も local CV を過信せず、LB でしか見えない domain gap を別扱いにしたほうがよい。

## 候補一覧

| 判定 | 優先 | topic id | title | 発見元 | votes | comments | last activity | 理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| read | high | 583577 | 1st Place Solution: Multi-Iterative Noisy Student Is All You Need | WriteUps Top, Recent | 216 | 38 | 2025-08-13 | 1位 writeup。疑似ラベル設計が最も具体的 |
| read | high | 583312 | 5th place solution: Self-Distillation is All You Need | WriteUps Top, Recent | 68 | 23 | 2025-07-04 | gold 帯 writeup。手動 cleaning と 3-stage distillation が具体的 |
| read | high | 583457 | 13rd solution for BirdCLEF+ 2025 | WriteUps Top, Recent | 14 | 1 | 2025-06-07 | gold 帯 writeup。簡潔だが winner 共通骨格の確認に使える |
| read | medium | 573066 | Recipe to Public LB 0.872 | Competitions Top, Recent | 119 | 88 | 2025-05-30 | writeup 前の高 vote baseline。mel 設計と human voice 対策の補完 |
| read | medium | 570760 | Additional dataset for rare classes | Competitions Top, Recent | 72 | 21 | 2025-06-05 | rare class 外部データとライセンス運用、host rule 補完 |
| skim | medium | 567499 | BirdCLEF back again - 2025 - 2024 - 2023 - 2022 - 2021 - 2020 + Top Solutions | WriteUps Top, Recent | 55 | 7 | 2025-05-31 | 過去解法の案内。今回の具体実装は薄い |
| skim | medium | 568886 | Human voice in the recordings | Competitions Top, Recent | 107 | 37 | 2025-05-25 | human voice 議論は濃いが、今回は writeup 側の記述を優先 |
| skim | medium | 570402 | Unstable Experiments and Key Early Takeaways | Competitions Top, Recent | 55 | 20 | 2025-05-17 | early idea 集。最終 gold 解法より粒度が粗い |
| skip | low | 567503 | Welcome to BirdCLEF+ 2025 - Meet the hosts | WriteUps Top, Recent | 15 | 4 | 2025-05-13 | host 紹介中心 |
| skip | low | 569610 | BirdCLEF 2020–2025: Trends and Insights from Five Years of Competition | Competitions Top, Recent | 12 | 4 | 2025-03-29 | 俯瞰記事で、2025 gold 実装の直接 source ではない |
| skip | low | 582805 | Demystifying Torchaudio’s MelSpectrogram Parameters for BirdCLEF 2025 | Competitions Top, Recent | 5 | 0 | 2025-06-02 | 単独 topic としては有用だが、gold 解法 source より優先度が低い |

## Topic別メモ

### 1st Place Solution: Multi-Iterative Noisy Student Is All You Need

- URL: https://www.kaggle.com/competitions/birdclef-2025/writeups/nikita-babych-1st-place-solution-multi-iterative-n
- topic id: 583577
- votes/comments: 216/38
- 要点:
  - 20 秒入力の SED を基礎に、`train_soundscapes` を疑似ラベル化して `MixUp + Noisy Student` として自己学習した。
  - supervised だけで `0.872`、pseudo-label MixUp 比率を 1.0 まで上げると `0.898`、4 回目の multi-iterative pseudo-labeling で `0.930 public` まで到達した。
  - pseudo-label に power transform を掛けて label noise を削るのが中核で、iteration 5 では伸びが止まった。
  - Amphibia/Insecta 専用モデルを別に立て、target species 用 ensemble に差し込んで `+0.002~0.003` を得ている。
- 重要コメント:
  - Nikita Babych (2025-06-11, comment 3222108): Stage 1 では gradient clipping を使わず、MixUp 前の left padding 実装を共有。https://www.kaggle.com/competitions/birdclef-2025/writeups/nikita-babych-1st-place-solution-multi-iterative-n#3222108
  - Nikita Babych (2025-06-22, comment 3229978): human voice removal は悪化、MixUp target は `max` で統合したと補足。https://www.kaggle.com/competitions/birdclef-2025/writeups/nikita-babych-1st-place-solution-multi-iterative-n#3229978
- 信頼度: 高 - 1位本人の詳細 writeup と follow-up コメントが具体的

### 5th place solution: Self-Distillation is All You Need

- URL: https://www.kaggle.com/competitions/birdclef-2025/writeups/noir-5th-place-solution-self-distillation-is-all-y
- topic id: 583312
- votes/comments: 68/23
- 要点:
  - `Silero VAD + 手動確認` で human voice 区間を落とし、underrepresented class は手で bird-call 区間を切り出した。
  - 学習は 3 段構成で、`train_audio` だけの self-distillation を 4-5 回、その後 `train_soundscapes` を 1:1 で混ぜて 2 回追加した。
  - 10 秒 log-mel、`FocalLoss(gamma=2)`、`Sumix on mel domain`、2.5 秒 overlap inference、`[0.1, 0.8, 0.1]` smoothing が柱だった。
  - public notebook にあった low-ranked class の power adjustment は overfit リスクで本番不採用としている。
- 重要コメント:
  - MYSO (2025-06-07, comment 3219124): 手動 cleaning は約 2,000 音声。効果の厳密測定はないが重要と判断。https://www.kaggle.com/competitions/birdclef-2025/writeups/noir-5th-place-solution-self-distillation-is-all-y#3219124
  - MYSO (2025-06-08, comment 3219870): Stage 2 は 5-fold、Stage 3 は no-fold + different seeds。pseudo label 混合例 `alpha=0.7` を共有。https://www.kaggle.com/competitions/birdclef-2025/writeups/noir-5th-place-solution-self-distillation-is-all-y#3219870
  - MYSO (2025-06-07, comment 3219128): 使用 GPU は RTX 3090、stage ごとの epoch 時間感も共有。https://www.kaggle.com/competitions/birdclef-2025/writeups/noir-5th-place-solution-self-distillation-is-all-y#3219128
  - MYSO (2025-07-04, comment 3240607): EcaNet を含む full training code を GitHub で公開。https://www.kaggle.com/competitions/birdclef-2025/writeups/noir-5th-place-solution-self-distillation-is-all-y#3240607
- 信頼度: 高 - 5位 writeup 本文が具体的で、コメントで不足点も補完されている

### 13rd solution for BirdCLEF+ 2025

- URL: https://www.kaggle.com/competitions/birdclef-2025/writeups/h-k-z-13rd-solution-for-birdclef-2025
- topic id: 583457
- votes/comments: 14/1
- 要点:
  - 2023 2nd solution 系の `v2s` SED をベースに、human voice 除去、`sumix`、train-data cleaning を積み上げて base を `0.865 public` まで上げた。
  - 5 秒 pseudo clip を `train_audio` に random sample する段で `+0.03 ~ 0.04` を得たとしており、soundscape を target-domain 補強に使う方向は 1位/5位と一致している。
  - rare species model を最後に足して大きく伸ばしたと主張しており、2024 上位解法の rare-species 専用モデルの流れを継承している。
  - backbone は `v2s` 主体で `v2_b3` と `seresnext26t` を追加した。
- 重要コメント:
  - shanzhong8 (2025-06-07, comment 3219250): rare species model の gain は `+0.1` ではなく `+0.01` の typo ではと指摘。https://www.kaggle.com/competitions/birdclef-2025/writeups/h-k-z-13rd-solution-for-birdclef-2025#3219250
- 信頼度: 中 - gold 帯 source だが本文が短く、設定の細部は不足

### Recipe to Public LB 0.872

- URL: https://www.kaggle.com/competitions/birdclef-2025/discussion/573066
- topic id: 573066
- votes/comments: 119/88
- 要点:
  - final writeup ではないが、2025 序盤の高 vote baseline として `melspec tuning`, `FocalBCE`, `Random 5 sec`, `middle feature pooling`, `human sound filtering`, `post process` を整理している。
  - 「raw wave augmentation は悪化」「melspec を画像として扱う」「K-Fold は当てにならず public LB が validation」という観測は、後の 1位/5位 writeup とも整合的。
  - single model `0.854, 0.856, 0.858, 0.859` の ensemble で `0.872` という early signal を出している。
- 重要コメント:
  - Salman Ahmed (2025-04-16, comment 3180629): human voice を残すと CAM が人声へ寄るので対処が必要と説明。https://www.kaggle.com/competitions/birdclef-2025/discussion/573066#3180629
  - Salman Ahmed (2025-04-14, comment 3179014): inference も train と同じ melspec を使うと回答。https://www.kaggle.com/competitions/birdclef-2025/discussion/573066#3179014
- 信頼度: 中 - final gold writeup ではないが、後続 gold 手法の先行仮説として価値が高い

### Additional dataset for rare classes

- URL: https://www.kaggle.com/competitions/birdclef-2025/discussion/570760
- topic id: 570760
- votes/comments: 72/21
- 要点:
  - 5 サンプル未満の rare class 向けに外部音源を収集した dataset を公開している。
  - rare class 補強は 1位/13位の writeup とも方向が一致しており、実際の source 公開形として参考になる。
  - 同時に external data のライセンス確認と host 合意を取りながら進めており、BirdCLEF 2025 の rule 解釈 source として重要。
- 重要コメント:
  - Quan Vu (2025-03-30, comment 3163460): 非準拠ファイルを除去すると返答。https://www.kaggle.com/competitions/birdclef-2025/discussion/570760#3163460
  - Tom Denton (2025-04-08, comment 3174229): `CC-BY` に加え `NC/ND` も可、ただし公開 forum / Kaggle dataset 化を推奨と明言。https://www.kaggle.com/competitions/birdclef-2025/discussion/570760#3174229
  - Stefan Kahl (2025-04-13, comment 3177740): `Macaulay` は不可と明言。https://www.kaggle.com/competitions/birdclef-2025/discussion/570760#3177740
- 信頼度: 高 - host コメントで rule が確定している

## 未確認・リスク

- `search_content(documentTypes=["Competition"])` と `search_competitions("birdclef-2025")` がそのままでは使えず、competition 解決は forum 側からの逆引きになった。
- 13位 writeup は terse で、gain や細かな設定値に曖昧さが残る。実装へ直写しするより、1位/5位の補助証拠として扱うほうが安全。
- 1位と 5位はいずれも public LB 依存の探索を強く使っている。再現時に local CV のみで同じ判断をすると外しやすい。
- human voice 対策は一貫して効くとは限らない。1位は悪化、5位は有効としており、対象クラス群や前処理粒度で逆符号になりうる。
- external data は score に効くが、Macaulay 禁止、再配布性、license source の公開が前提。ルール確認抜きで流用しないほうがよい。

## Source Index

| 種別 | id | title/comment | URL | メモ |
| --- | --- | --- | --- | --- |
| writeup | 12619 | 1st Place Solution: Multi-Iterative Noisy Student Is All You Need | https://www.kaggle.com/competitions/birdclef-2025/writeups/nikita-babych-1st-place-solution-multi-iterative-n | 1位本体 |
| comment | 3222108 | no grad clipping, left padding | https://www.kaggle.com/competitions/birdclef-2025/writeups/nikita-babych-1st-place-solution-multi-iterative-n#3222108 | 1位の追加実装 |
| comment | 3229978 | human voice removal hurt, target max mix | https://www.kaggle.com/competitions/birdclef-2025/writeups/nikita-babych-1st-place-solution-multi-iterative-n#3229978 | 1位の補足 |
| writeup | 13002 | 5th place solution: Self-Distillation is All You Need | https://www.kaggle.com/competitions/birdclef-2025/writeups/noir-5th-place-solution-self-distillation-is-all-y | 5位本体 |
| comment | 3219124 | manually cleaned about 2,000 files | https://www.kaggle.com/competitions/birdclef-2025/writeups/noir-5th-place-solution-self-distillation-is-all-y#3219124 | 5位の data cleaning |
| comment | 3219870 | stage2 folds, stage3 no folds, alpha=0.7 | https://www.kaggle.com/competitions/birdclef-2025/writeups/noir-5th-place-solution-self-distillation-is-all-y#3219870 | 5位の pseudo-label 混合 |
| comment | 3219128 | RTX 3090 and epoch times | https://www.kaggle.com/competitions/birdclef-2025/writeups/noir-5th-place-solution-self-distillation-is-all-y#3219128 | 5位の計算量感 |
| comment | 3240607 | full training code on GitHub | https://www.kaggle.com/competitions/birdclef-2025/writeups/noir-5th-place-solution-self-distillation-is-all-y#3240607 | 5位のコード公開 |
| writeup | 12421 | 13rd solution for BirdCLEF+ 2025 | https://www.kaggle.com/competitions/birdclef-2025/writeups/h-k-z-13rd-solution-for-birdclef-2025 | 13位本体 |
| comment | 3219250 | typo suspicion on rare-species gain | https://www.kaggle.com/competitions/birdclef-2025/writeups/h-k-z-13rd-solution-for-birdclef-2025#3219250 | 13位の補足 |
| topic | 573066 | Recipe to Public LB 0.872 | https://www.kaggle.com/competitions/birdclef-2025/discussion/573066 | 高 vote early baseline |
| comment | 3180629 | CAM attends to human voice | https://www.kaggle.com/competitions/birdclef-2025/discussion/573066#3180629 | human sound の根拠 |
| comment | 3179014 | inference uses same melspec as train | https://www.kaggle.com/competitions/birdclef-2025/discussion/573066#3179014 | feature consistency |
| topic | 570760 | Additional dataset for rare classes | https://www.kaggle.com/competitions/birdclef-2025/discussion/570760 | rare class external data |
| comment | 3174229 | CC-BY including NC/ND is allowed | https://www.kaggle.com/competitions/birdclef-2025/discussion/570760#3174229 | host rule |
| comment | 3177740 | Macaulay is not allowed | https://www.kaggle.com/competitions/birdclef-2025/discussion/570760#3177740 | host rule |
| comment | 3163460 | remove non-compliant files | https://www.kaggle.com/competitions/birdclef-2025/discussion/570760#3163460 | dataset cleanup |
