# タイムアウト検出・リトライ・長時間動画スキップ機能

## 概要

この機能は、ダウンロード中の動画がハングアップした場合を自動検出し、自動リトライまたは長時間動画をスキップする機能を提供します。System Instructionに準拠した完全なログ記録を含みます。

## 機能一覧

### 1. タイムアウト検出 (Timeout Detection)
- **説明**: ダウンロード中に進行状況が止まった場合を自動検出
- **動作**: 各chunk（デフォルト8KB）の処理ごとに進行状況をチェックし、設定時間（デフォルト30秒）内に進行がなければタイムアウトと判定
- **設定**: `chunk_timeout_seconds`（デフォルト: 30秒）

### 2. 自動リトライ (Auto Retry)
- **説明**: タイムアウトやエラーが発生した場合、自動的にリトライ
- **動作**: 最大リトライ回数（デフォルト3回）まで、設定された遅延時間（デフォルト5秒）を置いて再試行
- **設定**: `max_retries`（デフォルト: 3）、`retry_delay_seconds`（デフォルト: 5秒）

### 3. 長時間動画のスキップ (Skip Slow Videos)
- **説明**: ダウンロードに時間がかかりすぎる動画を自動的にスキップ
- **動作**: 設定時間（デフォルト30分）を超えた場合、自動的にスキップして次の動画に進む
- **設定**: `max_download_time_seconds`（デフォルト: 1800秒 = 30分）

## 設定方法

すべての設定は`config.json`ファイルで管理されます。アプリケーション起動時に自動的に作成され、既存の設定が保存されます。

### config.jsonの構造

```json
{
  "cookie": "...",
  "download_folder": "./downloads",
  "settings": {
    "naming_mode": "video_id",
    "max_concurrent": 3,
    "video_format": "auto",
    "orientation_filter": "all",
    "orientation_swap": false,
    
    // タイムアウトとリトライ設定（新機能）
    "download_timeout_seconds": 300,        // 各動画の総タイムアウト（秒）デフォルト: 300秒（5分）
    "chunk_timeout_seconds": 30,            // chunkタイムアウト（秒）デフォルト: 30秒
    "max_retries": 3,                       // 最大リトライ回数 デフォルト: 3
    "retry_delay_seconds": 5,               // リトライ間の待機時間（秒）デフォルト: 5秒
    "max_download_time_seconds": 1800,      // 最大ダウンロード時間（秒）デフォルト: 1800秒（30分）
    "enable_timeout_detection": true,       // タイムアウト検出を有効化 デフォルト: true
    "enable_auto_retry": true,              // 自動リトライを有効化 デフォルト: true
    "enable_skip_slow_videos": true,        // 長時間動画のスキップを有効化 デフォルト: true
    "chunk_size": 8192                      // chunkサイズ（バイト）デフォルト: 8192（8KB）
  }
}
```

### 設定の変更方法

#### 方法1: config.jsonを直接編集

1. プロジェクトルートの`config.json`ファイルを開く
2. `settings`セクション内の該当パラメータを変更
3. アプリケーションを再起動

#### 方法2: コードから変更（今後の拡張）

`CookieManager.set_setting(key, value)`メソッドを使用してプログラムから変更可能（現在は未実装）

例:
```python
cookie_manager.set_setting("chunk_timeout_seconds", 60)  # 60秒に変更
cookie_manager.set_setting("max_retries", 5)  # 最大5回リトライ
```

## 動作フロー

### 正常なダウンロードフロー

```
1. download_video()呼び出し
   ↓
2. ダウンロード開始（chunkごとに処理）
   ↓
3. 各chunk処理時に進行状況チェック
   ↓
4. 進行があれば → タイマーリセット
   ↓
5. ダウンロード完了 → 成功
```

### タイムアウト検出フロー

```
1. download_video()呼び出し
   ↓
2. ダウンロード開始
   ↓
3. chunk処理中に進行状況チェック
   ↓
4. 30秒間（デフォルト）進行なし
   ↓
5. タイムアウト検出 → ログ記録
   ↓
6. 自動リトライが有効？
   ├─ Yes → リトライ（最大3回まで）
   │         ↓
   │        成功 → 完了
   │        失敗 → エラー
   └─ No  → 即座にエラー
```

### 長時間動画スキップフロー

```
1. download_video()呼び出し
   ↓
2. ダウンロード開始
   ↓
3. 経過時間をチェック（各chunk処理時）
   ↓
4. 30分（デフォルト）経過？
   ├─ Yes → スキップ → ログ記録 → 次の動画へ
   └─ No  → 続行
```

## ログ出力例

### 正常なダウンロード

```
[2025-11-15 16:03:17] [INFO] [VideoDownloader.download_video] ============================================================
[2025-11-15 16:03:17] [INFO] [VideoDownloader.download_video] VideoDownloader.download_video - Bắt đầu
[2025-11-15 16:03:17] [INFO] [VideoDownloader.download_video]   - Video URL: https://...
[2025-11-15 16:03:17] [INFO] [VideoDownloader.download_video]   - Save path: C:\...\video_xxx.mp4
[2025-11-15 16:03:17] [INFO] [VideoDownloader.download_video] File size: 3705284 bytes (3.53 MB)
[2025-11-15 16:03:17] [INFO] [VideoDownloader.download_video] Đang tải file...
[2025-11-15 16:03:21] [INFO] [VideoDownloader.download_video] Đã tải thành công - File size: 3705284 bytes (3.53 MB)
[2025-11-15 16:03:21] [INFO] [VideoDownloader.download_video] Thời gian tải: 3.14 giây (0.05 phút)
[2025-11-15 16:03:21] [INFO] [VideoDownloader.download_video] Tốc độ tải: 1.13 MB/s (1152.05 KB/s)
```

### タイムアウト検出とリトライ

```
[2025-11-15 16:03:17] [INFO] [VideoDownloader.download_video] VideoDownloader.download_video - Bắt đầu
[2025-11-15 16:03:17] [INFO] [VideoDownloader.download_video] File size: 19166564 bytes (18.28 MB)
[2025-11-15 16:03:47] [WARNING] [VideoDownloader.download_video_with_retry] Phát hiện timeout: Không có progress trong 30.5s (timeout: 30s)
[2025-11-15 16:03:47] [WARNING] [VideoDownloader.download_video_with_retry] Downloaded size: 4096000 bytes, không thay đổi trong 30.5s
[2025-11-15 16:03:47] [INFO] [VideoDownloader.download_video_with_retry] Sẽ retry download sau 5 giây...
[2025-11-15 16:03:52] [INFO] [VideoDownloader.download_video_with_retry] Retry lần 1/3 sau 5 giây...
[2025-11-15 16:04:22] [INFO] [VideoDownloader.download_video_with_retry] Đã tải thành công - File size: 19166564 bytes (18.28 MB)
[2025-11-15 16:04:22] [DEBUG] [VideoDownloader.download_video_with_retry] Retry count: 1
```

### 長時間動画のスキップ

```
[2025-11-15 16:03:17] [INFO] [VideoDownloader.download_video] VideoDownloader.download_video - Bắt đầu
[2025-11-15 16:03:17] [INFO] [VideoDownloader.download_video] File size: 50000000 bytes (47.68 MB)
[2025-11-15 16:33:17] [WARNING] [VideoDownloader.download_video_with_retry] Video quá lâu (1800.2s > 1800s), bỏ qua...
[2025-11-15 16:33:17] [WARNING] [VideoDownloader.process_video] Video bị skip do quá lâu (> 1800s)
[2025-11-15 16:33:17] [WARNING] [DownloadService._download_worker]   ✗ Video 5 failed
[2025-11-15 16:33:17] [WARNING] [DownloadService._download_worker]     - Error: Video quá lâu (>1800s)
[2025-11-15 16:33:17] [WARNING] [DownloadService._download_worker]     - Skipped: True (video quá lâu)
```

### 統計情報レポート（ダウンロード完了時）

```
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker] ============================================================
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker] DownloadService._download_worker - Hoàn thành
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Tổng số video: 11
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Thành công: 10
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Thất bại: 1
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Tỷ lệ thành công: 90.9%
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Video bị timeout: 2
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Video bị skip (quá lâu): 1
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Tổng số lần retry: 5
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Tổng thời gian: 25.28 giây (0.42 phút)
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Tổng dung lượng đã tải: 33.44 MB
[2025-11-15 16:43:17] [INFO] [DownloadService._download_worker]   - Tốc độ trung bình: 1.32 MB/s (1354.60 KB/s)
```

## 推奨設定値

### 高速なネットワーク環境

```json
{
  "chunk_timeout_seconds": 20,          // 短めに設定（20秒）
  "max_retries": 2,                     // リトライ回数を減らす
  "max_download_time_seconds": 900,     // 15分でタイムアウト
  "chunk_size": 16384                   // 大きめのchunkサイズ（16KB）
}
```

### 低速なネットワーク環境

```json
{
  "chunk_timeout_seconds": 60,          // 長めに設定（60秒）
  "max_retries": 5,                     // リトライ回数を増やす
  "max_download_time_seconds": 3600,    // 60分でタイムアウト
  "chunk_size": 4096                    // 小さめのchunkサイズ（4KB）
}
```

### タイムアウト検出を無効化

```json
{
  "enable_timeout_detection": false,    // タイムアウト検出を無効化
  "enable_auto_retry": false,           // 自動リトライも無効化
  "enable_skip_slow_videos": true       // 長時間動画のスキップのみ有効
}
```

## コード構造

### 主要な変更点

#### 1. `models/cookie_manager.py`
- `default_config`にタイムアウト・リトライ設定を追加
- デフォルト値の設定

#### 2. `services/video_downloader.py`
- `download_video()`: タイムアウト設定を受け取る新しいインターフェース
- `download_video_with_retry()`: リトライロジックを含む内部メソッド
- `_cleanup_partial_file()`: 部分ダウンロードファイルのクリーンアップ（リトライ付き）
- `process_video()`: タイムアウト設定を`download_video()`に渡す

#### 3. `services/download_service.py`
- `start_download()`: タイムアウト設定を受け取るパラメータを追加
- `_download_worker()`: 統計情報の収集（timeout数、retry数、スキップ数）

#### 4. `controllers/download_controller.py`
- `start_download()`: CookieManagerからタイムアウト設定を取得してDownloadServiceに渡す

## トラブルシューティング

### 問題1: リトライが多すぎる

**症状**: ログに「Retry lần X/3」が頻繁に表示される

**解決策**:
1. `chunk_timeout_seconds`を長めに設定（例: 60秒）
2. ネットワーク接続を確認
3. `enable_timeout_detection`を一時的に無効化してテスト

### 問題2: 正常な動画がスキップされる

**症状**: ログに「Video quá lâu (>1800s), bỏ qua...」が表示されるが、実際は正常にダウンロードできそう

**解決策**:
1. `max_download_time_seconds`を長めに設定（例: 3600秒 = 60分）
2. 大きな動画の場合はさらに長めに設定
3. `enable_skip_slow_videos`を一時的に無効化してテスト

### 問題3: タイムアウト検出が動作しない

**症状**: 動画がハングアップしてもタイムアウトが検出されない

**解決策**:
1. `enable_timeout_detection`が`true`になっているか確認
2. `chunk_timeout_seconds`が適切に設定されているか確認
3. ログレベルを`DEBUG`に設定して詳細ログを確認

## 拡張性

この実装はモジュラー設計になっており、以下の拡張が容易です：

1. **UIからの設定変更**: `CookieManager.set_setting()`を使用してGUIから設定を変更
2. **動的な設定変更**: ダウンロード中でも設定を変更可能にする
3. **詳細な統計情報**: 各動画ごとの詳細統計を収集・表示
4. **通知機能**: タイムアウトやスキップ時にユーザーに通知

## 使用例

### 基本的な使用（デフォルト設定）

```python
# コードは自動的にconfig.jsonから設定を読み込む
# 特に何もする必要はない
download_controller.start_download(links)
```

### カスタムタイムアウト設定を使用（将来的な拡張）

```python
# カスタム設定を適用
timeout_settings = {
    'chunk_timeout_seconds': 60,
    'max_retries': 5,
    'enable_timeout_detection': True
}

# この機能は将来的に実装可能
# download_controller.start_download(links, timeout_settings=timeout_settings)
```

## ログ分析

ログファイル（`logs/app_*.log`、`logs/douyin_downloader_*.log`）を確認することで、以下の情報を得られます：

1. **タイムアウト発生の頻度**: `timeout_detected: True`の出現回数
2. **リトライの効果**: `Retry count: X`で成功した動画の数
3. **スキップされた動画**: `Skipped: True`の動画
4. **パフォーマンス**: ダウンロード時間、速度、成功率

## 注意事項

1. **Windows環境でのファイル削除**: Windowsではファイルが使用中の場合、削除に時間がかかることがあります。リトライロジック（最大3回）で対応していますが、場合によっては手動削除が必要な場合があります。

2. **ネットワーク状況**: タイムアウト設定はネットワーク環境に応じて調整してください。高速ネットワークでは短め、低速ネットワークでは長めに設定することを推奨します。

3. **メモリ使用量**: 大きな動画をダウンロードする場合、`chunk_size`を大きくするとメモリ使用量が増加します。デフォルトの8KBで十分です。

4. **ログファイルサイズ**: 詳細なログが出力されるため、定期的にログファイルを削除することを推奨します（現在は最新10ファイルのみ保持）。

## まとめ

この機能により、以下が実現されました：

✅ ハングアップ動画の自動検出  
✅ 自動リトライによる成功率向上  
✅ 長時間動画の自動スキップによる効率化  
✅ 詳細なログ記録によるデバッグ容易性  
✅ 設定可能なパラメータによる柔軟性  
✅ 統計情報による動作状況の可視化  

すべての機能はSystem Instructionに準拠したログ記録を含み、既存機能への影響はありません。


