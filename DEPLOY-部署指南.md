# Clouding Media 網站 — 部署指南

完成檔案：

```
clouding-media-site/
├── index.html       首頁
├── about.html       關於我們
├── services.html    服務方案（step30/plan 風格核心）
├── contact.html     聯絡我們
├── styles.css       共用樣式
├── script.js        共用 JS（語言切換、選單、FAQ）
└── DEPLOY-部署指南.md  本文件
```

部署到 `www.clouding-media.com` 有以下幾種常見方式，依照你目前主機商選擇即可。

---

## 方式 A — 傳統虛擬主機（cPanel / Plesk / FTP）

如果 `www.clouding-media.com` 已經架在中華電信、Godaddy、Bluehost、Namecheap 等虛擬主機：

1. 登入主機商控制台 → 找到「檔案管理員」或「FTP 帳號」
2. 進入網站根目錄（通常是 `public_html/`、`www/` 或 `htdocs/`）
3. 把 `clouding-media-site/` 裡的**所有檔案**（注意：是檔案，不是資料夾本身）上傳到該根目錄
4. 上傳完成後直接打開 `https://www.clouding-media.com` 應該就能看到首頁

> 如果你有 FTP 工具（FileZilla / WinSCP），用拖曳上傳最快。

---

## 方式 B — Cloudflare Pages（推薦，免費 + 快速 + HTTPS 自動）

1. 註冊 / 登入 [Cloudflare](https://dash.cloudflare.com)
2. 左側選單 → **Workers & Pages** → **Create application** → **Pages** → **Upload assets**
3. 把 `clouding-media-site/` 整個資料夾拖進去上傳
4. 命名專案（例：`clouding-media`），完成後會得到一個 `clouding-media.pages.dev` 的網址
5. 在專案設定 → **Custom domains** → 新增 `www.clouding-media.com` 與 `clouding-media.com`
6. Cloudflare 會引導你把網域 DNS 改到 Cloudflare（如果還沒）；改完後 HTTPS 與 CDN 自動到位

優點：免費、全球 CDN、HTTPS 自動續、推送更新只要重新拖檔。

---

## 方式 C — GitHub Pages

1. 在 GitHub 開一個 repo（公開或私有都行，`Pro` 帳號才支援私有 + Pages）
2. 把 `clouding-media-site/` 內所有檔案 commit 到 `main` 分支
3. Repo 設定 → **Pages** → Source 選 `main` / root → 儲存
4. 設定 **Custom domain** 為 `www.clouding-media.com`
5. 在你的網域 DNS 加 CNAME 指到 `<your-username>.github.io`

---

## 方式 D — Netlify / Vercel

兩個都支援拖曳資料夾上傳即部署：

- **Netlify**：登入 → Sites → 把 `clouding-media-site/` 拖進「Deploy manually」
- **Vercel**：登入 → New Project → Import folder

部署完同樣去 Settings 加 custom domain `www.clouding-media.com`，並依指示設定 DNS。

---

## DNS 設定速查

不論你選方式 B/C/D，最後都需要把網域指過去。在你網域註冊商（如 Gandi、Cloudflare、Namecheap）的 DNS 面板：

| 類型  | 名稱 | 值（依平台不同） |
| ---- | ---- | ----------------- |
| A 或 CNAME | @ | （平台給你的 IP 或目標網址） |
| CNAME | www | （平台給你的 *.pages.dev / *.netlify.app / *.vercel.app） |

DNS 變更通常 5–30 分鐘生效，最久 24 小時。

---

## 後續想修改內容？

- **改文字**：直接用記事本 / VS Code 編輯對應 HTML 檔。每段文字都有 `data-lang="zh"` 與 `data-lang="en"` 兩個版本，要兩個都改。
- **改顏色**：開 `styles.css`，最上方 `:root { --color-primary: ... }` 區塊改 4 個主色變數即可。
- **加入真實 logo**：把 logo 圖片放進資料夾，把 `<span class="logo-mark"></span>` 換成 `<img src="logo.png" alt="Clouding Media" />`
- **接入聯絡表單**：目前 contact 頁的表單是純前端 alert。要實際收信可以接 [Formspree](https://formspree.io)、[Getform](https://getform.io) 或自己後端。

---

## 本機預覽

不需要任何工具，直接雙擊 `index.html` 在瀏覽器打開即可預覽全部頁面與語言切換。

如果想跑本地伺服器（避免某些瀏覽器對 file:// 的限制）：

```bash
# Python 3
cd clouding-media-site
python -m http.server 8000
# 然後開 http://localhost:8000
```

有任何問題隨時跟我說，我可以幫你客製內容、加新區塊、改設計。
