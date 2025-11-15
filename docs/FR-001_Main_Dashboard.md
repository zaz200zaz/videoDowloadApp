# Functional Requirement FR-001: Main Dashboard
# 機能要件 FR-001: メインダッシュボード

## ID: FR-001

## Tên yêu cầu / 要件名: Màn hình chính – Main Dashboard

## Mục đích / 目的
Hiển thị các chức năng chính của ứng dụng để người dùng truy cập nhanh vào các màn hình con.
アプリケーションの主要機能を表示し、ユーザーがサブ画面にすばやくアクセスできるようにする。

## Thành phần giao diện / インターフェースコンポーネント

### 1. Icon Download Douyin
- **Kiểu / タイプ**: Button/Icon
- **ID**: `btnDownloadDouyin`
- **Mô tả / 説明**: Icon đại diện chức năng tải video Douyin
  - Douyin動画ダウンロード機能を表すアイコン
- **Hành vi / 動作**: 
  - Khi click, mở màn hình DownloadDouyinScreen
  - クリック時にDownloadDouyinScreenを開く
  - Ghi log hành vi click (theo System Instruction)
  - クリック動作をログに記録（System Instructionに従う）
  - Comment rõ ràng, module hóa chức năng
  - コメントを明確に、機能をモジュール化

### 2. Nhãn Download / ダウンロードラベル
- **Kiểu / タイプ**: Label
- **ID**: `lblDownloadDouyin`
- **Mô tả / 説明**: Văn bản hiển thị dưới icon
  - アイコンの下に表示するテキスト
- **Nội dung / 内容**: "Download Video Douyin"

### 3. Icon Edit Video
- **Kiểu / タイプ**: Button/Icon
- **ID**: `btnEditVideo`
- **Mô tả / 説明**: Icon đại diện chức năng chỉnh sửa video
  - 動画編集機能を表すアイコン
- **Hành vi / 動作**: 
  - Khi click, mở màn hình EditVideoScreen
  - クリック時にEditVideoScreenを開く
  - Có thể chọn video từ máy tính hoặc từ video đã tải
  - コンピューターからまたはダウンロード済み動画から選択可能
  - Ghi log hành vi click (theo System Instruction)
  - クリック動作をログに記録（System Instructionに従う）
  - Comment rõ ràng, module hóa chức năng
  - コメントを明確に、機能をモジュール化

### 4. Nhãn Edit / 編集ラベル
- **Kiểu / タイプ**: Label
- **ID**: `lblEditVideo`
- **Mô tả / 説明**: Văn bản hiển thị dưới icon
  - アイコンの下に表示するテキスト
- **Nội dung / 内容**: "Edit Video"

### 5. Background / 背景
- **Kiểu / タイプ**: View
- **ID**: `mainBackground`
- **Mô tả / 説明**: Nền màn hình chính, màu nền hoặc gradient
  - メイン画面の背景、背景色またはグラデーション

## Hành vi chức năng / 機能動作

### 1. Khi app mở / アプリ起動時
- Main Dashboard hiển thị đầy đủ các icon và nhãn
- メインダッシュボードにすべてのアイコンとラベルを表示
- Ghi log sự kiện khởi động (theo System Instruction)
- 起動イベントをログに記録（System Instructionに従う）

### 2. Layout và Responsive / レイアウトとレスポンシブ
- Icon và nhãn bố trí cân đối
- アイコンとラベルをバランスよく配置
- Responsive khi resize cửa sổ
- ウィンドウリサイズ時にレスポンシブに対応
- Icon và label tự co giãn khi resize window
- ウィンドウリサイズ時にアイコンとラベルが自動的に拡大縮小

### 3. Click btnDownloadDouyin / btnDownloadDouyinクリック時
- Mở màn hình DownloadDouyinScreen
- DownloadDouyinScreenを開く
- Giữ nguyên dữ liệu nếu cần
- 必要に応じてデータを保持
- Ghi log hành vi click với format: `[timestamp] [LEVEL] [Function] Message`
- クリック動作をログに記録（フォーマット: `[timestamp] [LEVEL] [Function] Message`）
- Log level: INFO cho hành vi bình thường, DEBUG cho chi tiết
- ログレベル: 通常動作はINFO、詳細はDEBUG

### 4. Click btnEditVideo / btnEditVideoクリック時
- Mở màn hình EditVideoScreen
- EditVideoScreenを開く
- Có thể chọn video từ máy tính hoặc từ video đã tải
- コンピューターからまたはダウンロード済み動画から選択可能
- Ghi log hành vi click với format: `[timestamp] [LEVEL] [Function] Message`
- クリック動作をログに記録（フォーマット: `[timestamp] [LEVEL] [Function] Message`）
- Log level: INFO cho hành vi bình thường, DEBUG cho chi tiết
- ログレベル: 通常動作はINFO、詳細はDEBUG

### 5. Hover Effect / ホバー効果
- Hỗ trợ hover effect: highlight icon khi rê chuột
- ホバー効果をサポート: マウスオーバー時にアイコンをハイライト
- Ghi log hover event ở level DEBUG (theo System Instruction - debug cho UI interactions)
- ホバーイベントをDEBUGレベルでログ記録（System Instruction - UI相互作用はDEBUG）

### 6. Multi-screen Support / マルチスクリーンサポート
- Cho phép mở nhiều màn hình con nhưng Main Dashboard luôn hiển thị
- 複数のサブ画面を開くことができ、メインダッシュボードは常に表示される
- Main Dashboard có thể minimize nhưng không thể đóng
- メインダッシュボードは最小化可能だが、閉じることはできない

## Yêu cầu bổ sung / 追加要件

### 1. UI/UX Requirements / UI/UX要件
- Icon có label text bên dưới, dễ đọc và dễ nhận diện
- アイコンの下にラベルテキストがあり、読みやすく識別しやすい
- Hỗ trợ hover effect: highlight icon khi rê chuột
- ホバー効果をサポート: マウスオーバー時にアイコンをハイライト
- Layout responsive: icon và label tự co giãn khi resize window
- レスポンシブレイアウト: ウィンドウリサイズ時にアイコンとラベルが自動的に拡大縮小

### 2. Extensibility / 拡張性
- Hệ thống dễ dàng mở rộng thêm chức năng mới mà không cần chỉnh layout chính
- メインレイアウトを変更せずに新しい機能を簡単に追加できるシステム
- Sử dụng factory pattern hoặc plugin pattern để thêm icon mới
- 新しいアイコンを追加するためにfactoryパターンまたはプラグインパターンを使用

### 3. Logging Requirements / ロギング要件 (theo System Instruction)
- Tất cả hành vi phải ghi log đầy đủ
- すべての動作をログに記録
- Format log: `[timestamp] [LEVEL] [Function] Message`
- ログフォーマット: `[timestamp] [LEVEL] [Function] Message`
- Log levels:
  - **INFO**: Hành vi bình thường (click, open screen)
  - **DEBUG**: Chi tiết UI interactions (hover, resize)
  - **WARNING**: Hành vi bất thường (screen not found, error opening)
  - **ERROR**: Lỗi nghiêm trọng (exception, crash)
- ログレベル:
  - **INFO**: 通常動作（クリック、画面を開く）
  - **DEBUG**: UI相互作用の詳細（ホバー、リサイズ）
  - **WARNING**: 異常動作（画面が見つからない、開く際のエラー）
  - **ERROR**: 深刻なエラー（例外、クラッシュ）

### 4. Code Quality / コード品質 (theo System Instruction)
- Comment rõ ràng cho tất cả functions và classes
- すべての関数とクラスに明確なコメント
- Module hóa chức năng: tách biệt UI logic, business logic, và logging
- 機能のモジュール化: UIロジック、ビジネスロジック、ロギングを分離
- Dễ bảo trì và mở rộng
- メンテナンスと拡張が容易

## Technical Specifications / 技術仕様

### 1. Framework / フレームワーク
- **Desktop GUI Framework**: Tkinter (Python built-in) hoặc PyQt5/PyQt6
- **推奨**: Tkinter (軽量、標準ライブラリ) または PyQt5/PyQt6 (高機能)

### 2. Architecture Pattern / アーキテクチャパターン
- **MVC Pattern**: Model-View-Controller
  - Model: Data và business logic
  - View: UI components
  - Controller: Event handlers và navigation
- **MVVM Pattern**: Model-View-ViewModel (nếu dùng PyQt)

### 3. Module Structure / モジュール構造
```
gui/
├── __init__.py
├── main_dashboard.py          # Main Dashboard screen
├── download_douyin_screen.py  # Download Douyin screen
├── edit_video_screen.py       # Edit Video screen
├── components/
│   ├── __init__.py
│   ├── icon_button.py         # Reusable icon button component
│   └── responsive_layout.py   # Responsive layout utilities
├── controllers/
│   ├── __init__.py
│   ├── dashboard_controller.py # Dashboard controller logic
│   └── navigation_controller.py # Navigation controller
└── utils/
    ├── __init__.py
    └── ui_logger.py           # UI-specific logging utilities
```

### 4. Logging Implementation / ロギング実装
- Sử dụng `utils.log_helper` module đã có sẵn
- 既存の`utils.log_helper`モジュールを使用
- Tạo `ui_logger.py` cho UI-specific logging
- UI固有のロギング用に`ui_logger.py`を作成
- Format log: `[timestamp] [LEVEL] [Function] Message`
- ログフォーマット: `[timestamp] [LEVEL] [Function] Message`

## Test Requirements / テスト要件

### 1. Unit Tests / ユニットテスト
- Test icon button click events
- アイコンボタンのクリックイベントをテスト
- Test screen navigation
- 画面ナビゲーションをテスト
- Test responsive layout
- レスポンシブレイアウトをテスト
- Test logging functionality
- ロギング機能をテスト

### 2. Integration Tests / 統合テスト
- Test complete user flow: click icon -> open screen
- 完全なユーザーフローをテスト: アイコンクリック -> 画面を開く
- Test multi-screen support
- マルチスクリーンサポートをテスト
- Test error handling
- エラーハンドリングをテスト

## Acceptance Criteria / 受け入れ基準

### 1. Functional Criteria / 機能基準
- ✅ Main Dashboard hiển thị đầy đủ các icon và nhãn khi app mở
- ✅ Main Dashboard displays all icons and labels when app opens
- ✅ Click btnDownloadDouyin mở DownloadDouyinScreen
- ✅ Click btnDownloadDouyin opens DownloadDouyinScreen
- ✅ Click btnEditVideo mở EditVideoScreen
- ✅ Click btnEditVideo opens EditVideoScreen
- ✅ Hover effect hoạt động trên tất cả icons
- ✅ Hover effect works on all icons
- ✅ Layout responsive khi resize window
- ✅ Layout is responsive when resizing window

### 2. Non-functional Criteria / 非機能基準
- ✅ Tất cả hành vi được ghi log đầy đủ theo System Instruction
- ✅ All behaviors are fully logged according to System Instruction
- ✅ Code có comment rõ ràng và module hóa
- ✅ Code has clear comments and is modularized
- ✅ Hệ thống dễ dàng mở rộng thêm chức năng mới
- ✅ System can easily be extended with new functions
- ✅ Performance: UI responsive trong < 100ms
- ✅ Performance: UI responds within < 100ms

## Implementation Notes / 実装注意事項

### 1. Logging Format / ロギングフォーマット
```python
# Example log format (theo System Instruction)
# [timestamp] [LEVEL] [Function] Message

[2025-11-15 18:30:45] [INFO] [MainDashboard.on_download_click] User clicked Download Douyin button
[2025-11-15 18:30:45] [INFO] [NavigationController.open_screen] Opening DownloadDouyinScreen
[2025-11-15 18:30:45] [DEBUG] [MainDashboard.on_button_hover] User hovered over btnDownloadDouyin
[2025-11-15 18:30:45] [WARNING] [NavigationController.open_screen] Screen DownloadDouyinScreen not found, creating new instance
[2025-11-15 18:30:45] [ERROR] [MainDashboard.on_download_click] Exception while opening screen: FileNotFoundError
```

### 2. Code Structure Example / コード構造例
```python
# gui/main_dashboard.py
class MainDashboard:
    """
    Main Dashboard Screen
    Hiển thị các chức năng chính của ứng dụng
    
    Args:
        parent: Parent window/container
        logger: Logger instance (theo System Instruction)
    
    Attributes:
        btnDownloadDouyin: Download Douyin button
        btnEditVideo: Edit Video button
        logger: Logger instance for logging (theo System Instruction)
    """
    
    def __init__(self, parent, logger=None):
        """
        Khởi tạo Main Dashboard
        
        Flow:
        1. Thiết lập logger (theo System Instruction)
        2. Tạo UI components
        3. Thiết lập event handlers
        4. Ghi log sự kiện khởi động (theo System Instruction)
        """
        function_name = "MainDashboard.__init__"
        self.logger = logger or get_logger('MainDashboard')
        self.log('info', f"{function_name} - Bắt đầu khởi tạo Main Dashboard", function_name)
        
        # ... initialization code ...
        
        self.log('info', f"{function_name} - Main Dashboard đã được khởi tạo thành công", function_name)
    
    def on_download_click(self, event):
        """
        Event handler khi click btnDownloadDouyin
        
        Flow:
        1. Ghi log hành vi click (theo System Instruction)
        2. Mở DownloadDouyinScreen
        3. Ghi log kết quả (theo System Instruction)
        
        Args:
            event: Click event
        """
        function_name = "MainDashboard.on_download_click"
        self.log('info', f"{function_name} - User clicked Download Douyin button", function_name)
        
        try:
            # ... open screen logic ...
            self.log('info', f"{function_name} - DownloadDouyinScreen đã được mở thành công", function_name)
        except Exception as e:
            self.log('error', f"{function_name} - Lỗi khi mở DownloadDouyinScreen: {e}", function_name, exc_info=True)
```

### 3. Module Structure / モジュール構造
- **Separation of Concerns**: UI logic, business logic, và logging được tách biệt
- **関心事の分離**: UIロジック、ビジネスロジック、ロギングを分離
- **Reusability**: Icon button component có thể tái sử dụng
- **再利用性**: アイコンボタンコンポーネントを再利用可能にする
- **Testability**: Mỗi module có thể test độc lập
- **テスト可能性**: 各モジュールを独立してテスト可能にする

## Dependencies / 依存関係

### 1. Internal Dependencies / 内部依存関係
- `utils.log_helper`: Logging utilities (theo System Instruction)
- `services.download_service`: Download service (cho DownloadDouyinScreen)
- `models.cookie_manager`: Cookie manager (cho DownloadDouyinScreen)

### 2. External Dependencies / 外部依存関係
- Python 3.8+
- Tkinter (built-in) hoặc PyQt5/PyQt6
- Pillow (PIL) cho icon/image handling (optional)

## Future Enhancements / 将来の拡張

1. **Theme Support**: Dark mode / Light mode
2. **Customization**: User có thể tùy chỉnh icon và layout
3. **Keyboard Shortcuts**: Shortcut keys cho các chức năng chính
4. **Recent Activity**: Hiển thị recent downloads và edits
5. **Notifications**: Toast notifications cho các sự kiện quan trọng

## References / 参照

- System Instruction document (for logging format và code quality requirements)
- Existing codebase structure (services/, models/, utils/)
- UI/UX best practices

