# Claude Opus 4.6 vs 4.7 Benchmark

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Claude Opus 4.6 と 4.7 を **5カテゴリ・計30タスク** で真っ向比較するためのベンチマークフレームワーク。
自分のドメインのタスクを `tasks/*.json` に追加するだけで "俺ベンチ" として使えます。

> 📝 関連記事: [【検証フレームワーク公開】Claude Opus 4.7 は 4.6 から本当に進化したのか？](https://qiita.com/) *(Qiita 公開予定)*

---

## ✨ 特徴

- 🔁 **完全に再現可能** — `temperature=0` 固定、入出力すべて JSON 保存
- ⚖️ **公平な比較** — `ThreadPoolExecutor` で両モデルを同時コール
- 🧪 **実行ベース採点** — コーディング課題は LLM に採点させず、`python solution.py` の exit code で判定
- 🧑‍⚖️ **LLM-as-Judge** — 定性タスク（日本語NLP）は Claude にブラインドで採点させる
- 🔌 **拡張容易** — `tasks/*.json` を足すだけで新カテゴリ追加可能

---

## 📊 評価カテゴリ

| # | カテゴリ | タスク数 | 評価方法 | 狙い |
|---|---|---:|---|---|
| 1 | `coding` | 5 | 単体テスト `pass@1` | 実行可能性 |
| 2 | `reasoning` | 10 | 正解一致 | 引っかけ耐性 |
| 3 | `long_context` | 5 | Needle-in-Haystack (〜200K tok) | RAG実用性 |
| 4 | `tool_use` | 5 | 必要ツール呼び出しカバレッジ | Agent信頼性 |
| 5 | `ja_nlp` | 5 | LLM-as-Judge (1-5) | 実務和文処理 |

---

## 🚀 クイックスタート

```bash
git clone https://github.com/yukurash/claude-opus-4-benchmark.git
cd claude-opus-4-benchmark

pip install -r requirements.txt
cp .env.example .env
# .env に ANTHROPIC_API_KEY を記入
```

### 実行

```bash
# 全カテゴリ実行（所要 30〜60分 / APIコスト $15〜30 程度）
python runner.py --all

# カテゴリ単位
python runner.py --category coding
python runner.py --category reasoning
python runner.py --category long_context
python runner.py --category tool_use
python runner.py --category ja_nlp

# 結果集計（results/*.json を読んで表と CSV を出力）
python aggregate.py
```

---

## 🧱 リポジトリ構成

```
.
├── agents.py          # 5カテゴリのエージェント実装
├── client.py          # Anthropic SDK ラッパー
├── runner.py          # 両モデル並列実行エントリポイント
├── judge.py           # LLM-as-Judge
├── aggregate.py       # 集計 & CSV出力
├── config.py          # 設定 (モデルID / 温度)
├── tasks/
│   ├── coding.json
│   ├── reasoning.json
│   ├── long_context.json
│   ├── tool_use.json
│   └── ja_nlp.json
└── results/           # 実行結果（JSON, CSV）
```

---

## 🧩 自分のタスクを追加する

`tasks/<category>.json` に以下のフォーマットで追記するだけ。

### coding
```json
{
  "id": "cod-006",
  "buggy_code": "def my_func(x):\n    ...",
  "tests": "assert my_func(1) == 1\nprint('ok')\n"
}
```

### reasoning
```json
{ "id": "rea-011", "question": "...", "expected": "42" }
```

### ja_nlp
```json
{ "id": "ja-006", "prompt": "以下を...してください。\n元文: 「...」" }
```

---

## ⚙️ 設定

`.env` またはシェル環境変数で上書き可能：

```env
ANTHROPIC_API_KEY=sk-ant-...
MODEL_A=claude-opus-4-6-20260115       # 実際のモデルIDに合わせて変更
MODEL_B=claude-opus-4-7-20260401
```

> ⚠️ モデルIDは執筆時点の推測値を含みます。[Anthropic 公式ドキュメント](https://docs.anthropic.com/) で最新のIDを確認して置き換えてください。

---

## 🧑‍⚖️ Judge のバイアスについて

デフォルトでは **Opus 4.7 自身** を Judge に使用しています（自己採点バイアスに注意）。
より厳密な評価を行う場合は、`config.py` の `JUDGE` を別系統のモデル（例: GPT-4 系）に差し替えてください。

---

## 📈 想定結果サンプル

フレームワークが期待通りに動作した場合のサンプル結果は [`results/SAMPLE_SUMMARY.md`](results/SAMPLE_SUMMARY.md) を参照。
**実測値ではありません**。実測は各自の API キーでどうぞ。

---

## 🤝 Contributing

- 「俺のドメインではこうだった」系の追試・PR 大歓迎
- 新カテゴリ（SQL, 正規表現, マルチモーダル等）の追加も歓迎
- Issue で議論どうぞ

---

## 📄 License

MIT — 詳細は [LICENSE](LICENSE) を参照。
