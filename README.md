# Claude Opus 4.6 vs 4.7 Benchmark

Claude Opus 4.6 と 4.7 を 5 カテゴリ・計 30 タスクで真っ向比較するためのベンチマークフレームワークです。

## 特徴

- **完全にローカルで完結** — Anthropic APIキーさえあれば誰でも再現可能
- **LLM-as-Judge** — 定性タスクは Claude Opus 4.7 自身に採点させる（bias検証あり）
- **並列実行** — 両モデルを同一プロンプトで同時コール
- **再現性** — temperature=0, seed固定、プロンプト・結果すべてJSONで保存

## セットアップ

```bash
pip install -r requirements.txt
cp .env.example .env
# .env に ANTHROPIC_API_KEY を記入
```

## 実行

```bash
# 全カテゴリ実行
python runner.py --all

# カテゴリ単位で実行
python runner.py --category coding
python runner.py --category reasoning
python runner.py --category long_context
python runner.py --category tool_use
python runner.py --category ja_nlp

# 結果集計
python aggregate.py
```

## カテゴリ

| # | カテゴリ | タスク数 | 評価方法 |
|---|---|---|---|
| 1 | coding | 5 | 単体テスト pass 率 |
| 2 | reasoning | 10 | 正解一致 |
| 3 | long_context | 5 | Needle-in-haystack 再現率 |
| 4 | tool_use | 5 | ステップ完遂率 |
| 5 | ja_nlp | 5 | LLM-as-Judge (1-5点) |

## コスト目安

全タスク実行時のAPIコスト概算：**$15〜30**（入出力トークン量による）

## ライセンス

MIT
