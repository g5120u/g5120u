# GitHub 個人首頁自動化（你只要寫程式，履歷自己長出來）

這是一套「**GitHub 個人首頁自動化**」：把你的 GitHub Profile 變成能自動長出 **履歷 / 能力證明 / 專案說故事 / 技能雷達 / 實戰證據庫** 的首頁系統（中英文可雙語）。

## 三層架構（你要的那三層）

- **GitHub Repo**：原始碼（每個專案本身）
- **GitHub Profile**：你是誰（`<username>/<username>` 的 `README.md`）
- **GitHub Engine**：你會什麼 / 你做過什麼 / 你強在哪（由資料與證據自動生成）

重點是：**你不用本機跑任何東西**。你只要更新 `data/*.yml` 並 push，GitHub Actions 會自動生成首頁與資產。

## 你會得到的 Profile 首頁區塊

- 👑 你是誰
- 🚀 你在打造什麼引擎
- 🧠 你會的技能雷達（自動生成 SVG）
- 📦 你做過的專案模組（從 `data/projects.yml` 生成）
- 📈 真實開發證據（Readme Stats / Streak / Activity Graph / Trophy）
- ⏳ 專案進化史（Timeline / Mermaid）

## 快速開始（套到你的 GitHub Profile）

1. 在 GitHub 建立一個特殊 repo：`<你的帳號>/<你的帳號>`（名稱必須等於 username）。
2. 把這個模板的內容放進那個 repo（根目錄要有 `README.md`、`.github/workflows/update-readme.yml`、`scripts/`、`data/`、`evidence/`）。
3. 修改：
   - `data/profile.yml`（最重要：把 `username: "g5120u"` 改成你的 GitHub 帳號）
   - `data/skills.yml`（你的技能雷達軸與分數）
   - `data/projects.yml`（你的專案模組與時間線）
   - 在 `evidence/` 新增你的實戰證據 markdown（有 front matter）
4. Push 之後，GitHub Actions 會自動生成：
   - `README.md`
   - `assets/skill-radar.zh.svg`、`assets/skill-radar.en.svg`
   - `generated/evidence-index.md`

> 你不需要手動改 README；你只要寫程式、寫證據、填資料，首頁會自己長出來。

## 檔案結構

```
.github/workflows/update-readme.yml   # 自動更新
data/profile.yml                      # 你是誰 + 你在打造什麼
data/skills.yml                       # 技能雷達資料
data/projects.yml                     # 專案模組 + 時間線資料
evidence/                             # 實戰證據庫（你新增檔案）
scripts/build_readme.py               # 生成 README
scripts/generate_skill_radar.py       # 生成 Radar SVG
scripts/index_evidence.py             # 生成證據索引
templates/profile_readme.md.j2        # README 模板（中英文）
assets/                               # 生成後資產（SVG）
generated/                            # 生成後 markdown（索引/片段）
```

## 建議的「證據」長相（企業最吃）

- **性能**：前後數據（P50/P95、成本、吞吐）、方法、回滾策略
- **可靠性**：事故復盤、監控告警、SLO/SLI、復發預防（回歸測試）
- **工程化**：CI/CD、lint/test、release、版本治理、可觀測性
- **架構決策**：ADR（為何選 A 不選 B）、風險、折衷

## 常見客製（讓企業真的「嚇到」）

- **把專案變成故事**：每個專案都要有「一行總結 + 3 個亮點 + 1 個 proof 連結」
- **把持續性變成訊號**：週更（小也沒關係）+ releases，活動圖/連續開發自然會強

## FAQ

- **Q：那些圖（Stats/Streak/Trophy/Activity Graph）需要 token 嗎？**  
  A：它們是第三方服務渲染的公開圖片；你只要把 `username` 設對即可顯示。若企業合規要求嚴格，也可改成自建或移除。


