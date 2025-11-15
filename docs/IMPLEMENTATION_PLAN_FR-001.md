# Implementation Plan for FR-001: Main Dashboard
# FR-001 メインダッシュボード実装計画

## Overview / 概要

This document outlines the implementation plan for FR-001: Main Dashboard according to System Instruction requirements.
この文書は、System Instruction要件に従ったFR-001: メインダッシュボードの実装計画を概説します。

## Phase 1: Project Structure Setup / フェーズ1: プロジェクト構造のセットアップ

### 1.1 Create Directory Structure / ディレクトリ構造の作成
```
gui/
├── __init__.py
├── main_dashboard.py          # Main Dashboard screen
├── download_douyin_screen.py  # Download Douyin screen (placeholder)
├── edit_video_screen.py       # Edit Video screen (placeholder)
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

### 1.2 Files to Create / 作成するファイル
1. `gui/__init__.py` - GUI package initialization
2. `gui/main_dashboard.py` - Main Dashboard implementation
3. `gui/components/icon_button.py` - Reusable icon button
4. `gui/controllers/dashboard_controller.py` - Dashboard controller
5. `gui/controllers/navigation_controller.py` - Navigation controller
6. `gui/utils/ui_logger.py` - UI-specific logging
7. `app_main.py` - Main application entry point

## Phase 2: Core Components / フェーズ2: コアコンポーネント

### 2.1 UI Logger / UIロガー
**File**: `gui/utils/ui_logger.py`

**Purpose / 目的**: UI-specific logging utilities following System Instruction format
**目的**: System Instructionフォーマットに従ったUI固有のロギングユーティリティ

**Key Features / 主要機能**:
- Format: `[timestamp] [LEVEL] [Function] Message`
- Log levels: INFO, DEBUG, WARNING, ERROR
- UI-specific context (screen name, component ID)

### 2.2 Icon Button Component / アイコンボタンコンポーネント
**File**: `gui/components/icon_button.py`

**Purpose / 目的**: Reusable icon button with label and hover effect
**目的**: ラベルとホバー効果を持つ再利用可能なアイコンボタン

**Key Features / 主要機能**:
- Icon display
- Label text below icon
- Hover effect (highlight)
- Click event handling
- Logging integration (theo System Instruction)

### 2.3 Responsive Layout / レスポンシブレイアウト
**File**: `gui/components/responsive_layout.py`

**Purpose / 目的**: Utilities for responsive layout management
**目的**: レスポンシブレイアウト管理のユーティリティ

**Key Features / 主要機能**:
- Grid-based layout
- Auto-resize on window resize
- Icon and label scaling

## Phase 3: Controllers / フェーズ3: コントローラー

### 3.1 Navigation Controller / ナビゲーションコントローラー
**File**: `gui/controllers/navigation_controller.py`

**Purpose / 目的**: Manage screen navigation and multi-screen support
**目的**: 画面ナビゲーションとマルチスクリーンサポートを管理

**Key Features / 主要機能**:
- Open screens (DownloadDouyinScreen, EditVideoScreen)
- Maintain screen instances
- Handle screen closing
- Log navigation events (theo System Instruction)

### 3.2 Dashboard Controller / ダッシュボードコントローラー
**File**: `gui/controllers/dashboard_controller.py`

**Purpose / 目的**: Handle Main Dashboard business logic
**目的**: メインダッシュボードのビジネスロジックを処理

**Key Features / 主要機能**:
- Initialize dashboard
- Handle button clicks
- Coordinate with navigation controller
- Log events (theo System Instruction)

## Phase 4: Main Dashboard Implementation / フェーズ4: メインダッシュボード実装

### 4.1 Main Dashboard Class / メインダッシュボードクラス
**File**: `gui/main_dashboard.py`

**Purpose / 目的**: Main Dashboard screen implementation
**目的**: メインダッシュボード画面の実装

**Components / コンポーネント**:
1. `btnDownloadDouyin` - Download Douyin button
2. `lblDownloadDouyin` - Download label
3. `btnEditVideo` - Edit Video button
4. `lblEditVideo` - Edit label
5. `mainBackground` - Background view

**Key Methods / 主要メソッド**:
- `__init__()` - Initialize dashboard
- `on_download_click()` - Handle download button click
- `on_edit_click()` - Handle edit button click
- `on_button_hover()` - Handle hover effect
- `on_window_resize()` - Handle window resize
- All methods log events (theo System Instruction)

## Phase 5: Integration / フェーズ5: 統合

### 5.1 Main Application Entry Point / メインアプリケーションエントリーポイント
**File**: `app_main.py`

**Purpose / 目的**: Application entry point, initialize and run GUI
**目的**: アプリケーションエントリーポイント、GUIを初期化して実行

**Key Features / 主要機能**:
- Initialize logging system
- Create main window
- Initialize Main Dashboard
- Start event loop

### 5.2 Screen Placeholders / 画面プレースホルダー
**Files**: 
- `gui/download_douyin_screen.py`
- `gui/edit_video_screen.py`

**Purpose / 目的**: Placeholder screens for navigation testing
**目的**: ナビゲーションテスト用のプレースホルダー画面

**Key Features / 主要機能**:
- Basic screen structure
- Navigation back to Main Dashboard
- Logging integration (theo System Instruction)

## Phase 6: Testing / フェーズ6: テスト

### 6.1 Unit Tests / ユニットテスト
**Files**:
- `tests/test_main_dashboard.py`
- `tests/test_icon_button.py`
- `tests/test_navigation_controller.py`

**Test Cases / テストケース**:
1. Icon button click events
2. Screen navigation
3. Responsive layout
4. Logging functionality
5. Hover effects

### 6.2 Integration Tests / 統合テスト
**Files**:
- `tests/test_dashboard_integration.py`

**Test Cases / テストケース**:
1. Complete user flow: click icon -> open screen
2. Multi-screen support
3. Error handling

## Implementation Order / 実装順序

1. **Phase 1**: Project structure setup
2. **Phase 2**: Core components (UI Logger, Icon Button, Responsive Layout)
3. **Phase 3**: Controllers (Navigation, Dashboard)
4. **Phase 4**: Main Dashboard implementation
5. **Phase 5**: Integration (app_main.py, screen placeholders)
6. **Phase 6**: Testing (unit tests, integration tests)

## System Instruction Compliance / System Instruction準拠

### Logging Requirements / ロギング要件
- ✅ All behaviors logged with format: `[timestamp] [LEVEL] [Function] Message`
- ✅ INFO level for normal actions (click, open screen)
- ✅ DEBUG level for UI interactions (hover, resize)
- ✅ WARNING level for abnormal behaviors
- ✅ ERROR level for exceptions

### Code Quality Requirements / コード品質要件
- ✅ Clear comments for all functions and classes
- ✅ Modularized code: UI logic, business logic, logging separated
- ✅ Easy to maintain and extend

### Extensibility / 拡張性
- ✅ Factory pattern or plugin pattern for adding new icons
- ✅ Main layout can be extended without major changes

## Notes / 注意事項

1. **Framework Choice**: 
   - Start with Tkinter (built-in, lightweight)
   - Can migrate to PyQt5/PyQt6 later if needed

2. **Logging Integration**:
   - Use existing `utils.log_helper` module
   - Extend with `gui/utils/ui_logger.py` for UI-specific logging

3. **Screen Management**:
   - Main Dashboard should always be accessible
   - Child screens can be opened/closed independently
   - Use singleton pattern for Main Dashboard if needed

4. **Error Handling**:
   - All errors should be logged (theo System Instruction)
   - User-friendly error messages
   - Graceful degradation

