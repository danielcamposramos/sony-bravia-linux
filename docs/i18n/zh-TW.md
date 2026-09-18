# Sony BRAVIA 3D 電視（2011–2012 年機種）重新播放 3D 影片與 3D 照片：由機主自行維護的開源修復專案

<!-- lang: zh-TW · canonical source: ../../README.md (English) · translated 2026-09-18 -->

這個專案讓 Sony 已停止網路服務的非 Android 版 BRAVIA（KDL 系列，2010–2012 年）在機主自己的家用網路上重新復活。完全不修改韌體，也不觸碰任何 DRM（版權保護）。這是**維修權（Right to Repair）**的實踐。

## 為什麼 3D 影片播放時沒有立體效果

- 這些電視只有在**影像串流本身**帶有 H.264「畫格封裝」（frame packing）SEI 資訊時，才會**自動切換到 3D**。
- 一般的 3D 影片檔（MKV 左右並排 SBS／上下 TAB）只在容器層帶有標籤，經由 DLNA 伺服器傳送時這個標籤會遺失。結果畫面維持左右並排，不會變成 3D。
- **解決方法（無損、不需重新編碼）**：用 `tools/bravia_sei3d.py` 為檔案寫入一次 SEI，之後透過 DLNA 播放時電視就會自動切換到 3D。HandBrake 也已合併此功能（PR #8100，將於下一版提供）。附帶的 Serviio 設定檔會在轉檔時自動加入 SEI。
- 左右眼顛倒？電視本身無法交換左右畫面，但 ffmpeg 濾鏡可以（`stereo3d=sbsl:sbsr`）。

## 3D 照片（左右並排／JPS／MPO）

- 實測（KDL-46EX725、KDL-46HX855）：在 DLNA 或 USB 的照片瀏覽中按下 3D 鍵，只會出現**「2D 轉 3D」**，沒有照片用的左右並排選項。
- 3D 相機的標準格式 **MPO** 從 USB 隨身碟播放：Sony 2011 年機種相容表中有列出，也有機主回報可用，目前正在驗證。
- 紅藍（互補色）立體照片與影片可轉換為左右並排：`tools/bravia_anaglyph.py`。

## 適用機種

- 已驗證：**KDL-46EX725**（2011）、**KDL-46HX855**（2012）
- 同一主機板系列：KDL-46EX724、KDL-40HX853、KDL-55HX753
- 3D 信號（SEI）的問題適用於所有從串流自動判斷 3D 的電視與投影機（Samsung 也有相同症狀的回報）。

## 相關文件（英文）

- [專案總覽](../../README.md)
- [3D 信號說明](../3d-signalling-explainer.md)
- [BRAVIA 3D 照片調查](../3d-photos-on-bravia.md)
- [在自己的 BRAVIA 上重現的步驟](../build-your-own-bravia-portal.md)
- [舊式 3D 格式（紅藍、交錯）](../legacy-3d-formats.md)

---

*2026 年 9 月 18 日由英文翻譯。歡迎母語人士指正，請開 Issue 告訴我們。*
