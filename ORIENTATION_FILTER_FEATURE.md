# 向きフィルタ機能（Landscape / Portrait）の使用方法

## 概要

この機能は、動画の向き（横向き/縦向き）でフィルタリングしてダウンロードする機能を提供します。ユーザーは横向き（Landscape）または縦向き（Portrait）の動画のみをダウンロードし、条件に合わない動画を自動的にスキップできます。

## 機能一覧

### 1. 向きフィルタリング（Orientation Filtering）
- **説明**: 動画の向きに基づいてフィルタリング
- **動作**: width/height比から向きを判定し、選択されたフィルタと比較
- **判定基準**:
  - `width > height` → Landscape (横向き)
  - `height > width` → Portrait (縦向き)
  - `width == height` → Square (正方形)

### 2. 詳細なログ記録
- **説明**: フィルタリングされた動画の詳細情報をログに記録
- **記録内容**:
  - Video ID
  - Author（作成者）
  - Orientation（向き）
  - Size（幅x高さ）
  - Aspect Ratio（アスペクト比）
  - URL

### 3. 統計情報の収集
- **説明**: フィルタリング統計情報を収集・表示
- **統計内容**:
  - フィルタリングされた動画数
  - スキップされた動画のリスト
  - ダウンロード成功率

### 4. UI通知
- **説明**: スキップされた動画のリストをUIで表示
- **機能**: ダウンロード完了時に、スキップされた動画の詳細リストを表示するウィンドウを開く

## 使用方法

### UIでの設定

1. **アプリケーションを起動**
2. **「Lọc theo hướng (Landscape/Portrait)」ドロップダウンを選択**
   - `Tất cả`（すべて）: すべての動画をダウンロード
   - `Portrait (Video dọc)`（縦向き）: 縦向きの動画のみダウンロード
   - `Landscape (Video ngang)`（横向き）: 横向きの動画のみダウンロード
3. **動画リンクを入力またはインポート**
4. **「Bắt đầu tải」ボタンをクリック**

### 設定の保存

選択したフィルタは自動的に`config.json`に保存され、次回起動時も維持されます。

## 動作フロー

### 1. 動画情報の取得時（APIから向きを取得できる場合）

```
1. process_video()呼び出し
   ↓
2. get_video_info()で動画情報を取得
   ↓
3. width/heightから向きを判定
   ↓
4. orientation_filter != "all" の場合
   ├─ orientationがフィルタと一致 → ダウンロード続行
   └─ orientationがフィルタと不一致 → スキップ（ログ記録）
   ↓
5. ダウンロード実行
```

### 2. 直接ビデオURLの場合（ダウンロード後に判定）

```
1. process_video()呼び出し
   ↓
2. 直接ビデオURLを検出
   ↓
3. ダウンロード実行
   ↓
4. ダウンロード完了後、ファイルメタデータから向きを判定
   ↓
5. orientation_filter != "all" の場合
   ├─ orientationがフィルタと一致 → ファイルを保持
   └─ orientationがフィルタと不一致 → ファイルを削除（ログ記録）
```

## ログ出力例

### フィルタリング前（動画情報取得時）

```
[2025-11-15 16:03:17] [INFO] [VideoDownloader.process_video] Video info retrieved - video_id=xxx, author=user123, orientation=vertical (portrait), size=720x1280, aspect_ratio=0.56, title=Video Title
[2025-11-15 16:03:17] [INFO] [VideoDownloader.process_video] Đang áp dụng orientation filter: Landscape (ngang)
[2025-11-15 16:03:17] [INFO] [VideoDownloader.process_video] Bỏ qua video xxx - Lý do: orientation không khớp
[2025-11-15 16:03:17] [INFO] [VideoDownloader.process_video]   - Video orientation: vertical (portrait)
[2025-11-15 16:03:17] [INFO] [VideoDownloader.process_video]   - Video size: 720x1280 (aspect ratio: 0.56)
[2025-11-15 16:03:17] [INFO] [VideoDownloader.process_video]   - Filter yêu cầu: horizontal (Landscape (ngang))
[2025-11-15 16:03:17] [INFO] [VideoDownloader.process_video]   - Video ID: xxx
[2025-11-15 16:03:17] [INFO] [VideoDownloader.process_video]   - Author: user123
[2025-11-15 16:03:17] [INFO] [VideoDownloader.process_video]   - Title: Video Title
```

### フィルタリング後（ダウンロード後に判定）

```
[2025-11-15 16:03:17] [INFO] [VideoDownloader.process_video] Video xxx là direct video URL, sẽ kiểm tra orientation sau khi tải (filter: Landscape (ngang))
[2025-11-15 16:03:47] [INFO] [VideoDownloader._get_video_orientation_from_file] Video file C:\...\video.mp4: width=1280, height=720, ratio=1.78
[2025-11-15 16:03:47] [INFO] [VideoDownloader.process_video] Video C:\...\video.mp4 - actual_orientation=horizontal, filter=horizontal
[2025-11-15 16:03:47] [INFO] [VideoDownloader.process_video] Video C:\...\video.mp4 có orientation: horizontal (Landscape (ngang)) - phù hợp với filter (horizontal)
```

### フィルタリング統計（ダウンロード完了時）

```
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker] DownloadService._download_worker - Hoàn thành
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Tổng số video: 11
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Thành công: 8
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Thất bại: 3
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Tỷ lệ thành công: 72.7%
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Video bị bỏ qua do orientation filter (horizontal): 3
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Danh sách video bị bỏ qua:
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]     1. Video ID: video123
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]        - Author: user123
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]        - Orientation: vertical
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]        - Size: 720x1280 (aspect ratio: 0.56)
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]        - URL: https://www.douyin.com/video/...
```

## UI通知

### ダウンロード完了時の通知

ダウンロードが完了すると、以下のメッセージが表示されます：

```
Hoàn tất!

Tổng số: 11
Thành công: 8
Thất bại: 3

Video bị bỏ qua do orientation filter (Landscape (Video ngang)): 3

Bạn có muốn xem danh sách video bị bỏ qua không?
```

「はい」を選択すると、スキップされた動画の詳細リストを表示するウィンドウが開きます。

### スキップされた動画リストウィンドウ

このウィンドウには以下の情報が表示されます：

- **STT（順番）**: 動画の順番
- **Video ID**: 動画ID
- **Author**: 作成者名
- **Orientation**: 動画の向き
- **Size (WxH)**: 幅x高さとアスペクト比
- **URL**: 動画URL

## コード構造

### 主要な変更点

#### 1. `services/video_downloader.py`
- `process_video()`: 向きフィルタリングロジックを強化
- `result`辞書に`filtered_by_orientation`、`orientation`、`width`、`height`を追加
- width/height比の詳細ログ記録
- フィルタリング理由の明確化

#### 2. `services/download_service.py`
- `_download_worker()`: フィルタリング統計情報の収集
- `filtered_by_orientation_count`: フィルタリングされた動画数
- `filtered_videos_info`: フィルタリングされた動画の詳細情報リスト

#### 3. `ui/main_window.py`
- `filtered_videos`: フィルタリングされた動画リスト（UI用）
- `_on_download_result()`: フィルタリングされた動画の収集
- `_download_complete()`: フィルタリング統計の表示とユーザー通知
- `_show_filtered_videos_list()`: スキップされた動画リストウィンドウ
- UIラベルの明確化（「Landscape/Portrait」を追加）

## 設定方法

### config.jsonでの設定

```json
{
  "settings": {
    "orientation_filter": "all"  // "all", "vertical", "horizontal"
  }
}
```

### UIからの設定

1. 「Lọc theo hướng (Landscape/Portrait)」ドロップダウンから選択
2. 選択は自動的に`config.json`に保存されます

## 使用例

### 例1: 縦向きの動画のみダウンロード

1. UIで「Portrait (Video dọc)」を選択
2. 動画リンクを入力
3. 「Bắt đầu tải」をクリック
4. 横向きの動画は自動的にスキップされます

### 例2: 横向きの動画のみダウンロード

1. UIで「Landscape (Video ngang)」を選択
2. 動画リンクを入力
3. 「Bắt đầu tải」をクリック
4. 縦向きの動画は自動的にスキップされます

## トラブルシューティング

### 問題1: フィルタリングが動作しない

**症状**: すべての動画がダウンロードされる

**解決策**:
1. UIでフィルタが正しく選択されているか確認
2. `config.json`の`orientation_filter`設定を確認
3. ログでフィルタが適用されているか確認（`Đang áp dụng orientation filter`が表示されるか）

### 問題2: 正常な動画がスキップされる

**症状**: 向きが正しいはずの動画がスキップされる

**解決策**:
1. ログで実際の`width`と`height`を確認
2. アスペクト比を確認（`aspect_ratio`）
3. 向きの判定ロジック（`width > height`でLandscape）を確認

### 問題3: 向きが判定できない

**症状**: ログに「orientation=unknown」が表示される

**解決策**:
1. APIから動画情報が正しく取得できているか確認
2. 直接ビデオURLの場合は、ダウンロード後にメタデータから判定される
3. `opencv-python`がインストールされているか確認（メタデータ読み取り用）

## 注意事項

1. **直接ビデオURL**: 直接ビデオURLの場合は、ダウンロード完了後にファイルメタデータから向きを判定します。フィルタに合わない場合、ファイルは削除されます。

2. **正方形動画**: 正方形（`width == height`）の動画は、フィルタが設定されている場合でもスキップされる可能性があります（`orientation="square"`は`"horizontal"`や`"vertical"`と一致しないため）。

3. **ログファイル**: 詳細なログは`logs/`ディレクトリに保存されます。フィルタリングの問題を調査する際は、ログファイルを確認してください。

4. **パフォーマンス**: フィルタリングは動画情報の取得時に実行されるため、パフォーマンスへの影響は最小限です。

## まとめ

この機能により、以下が実現されました：

✅ 向きに基づく動画フィルタリング  
✅ 詳細なログ記録（width/height比、アスペクト比）  
✅ 統計情報の収集と表示  
✅ UIでのスキップされた動画リスト表示  
✅ ユーザーフレンドリーな通知  
✅ System Instructionに準拠したログ記録  

すべての機能は既存機能への影響なく動作し、詳細なコメントとドキュメントが含まれています。

