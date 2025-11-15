"""
Test Cases cho NavigationController
NavigationControllerのテストケース

Mục đích:
- Test tất cả các chức năng quan trọng của NavigationController
- Test screen registration và navigation
- Test multi-screen support
- Đảm bảo logging đầy đủ theo System Instruction

Test Cases:
1. Test __init__: NavigationController初期化のテスト
2. Test register_screen: スクリーン登録のテスト
3. Test open_screen: スクリーンを開くテスト
4. Test open_screen_existing: 既存スクリーンを開くテスト
5. Test close_screen: スクリーンを閉じるテスト
6. Test close_screen_not_found: 存在しないスクリーンを閉じるテスト
"""

import unittest
import os
import sys
import tempfile
import shutil
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import logging
from datetime import datetime

# Thêm project root vào path để import modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from gui.controllers.navigation_controller import NavigationController
from utils.log_helper import write_log, get_logger


class TestNavigationController(unittest.TestCase):
    """Test class cho NavigationController"""
    
    def setUp(self):
        """
        Setup cho mỗi test case
        各テストケースのセットアップ
        
        Mục đích:
        - Tạo Tkinter root window cho test
        - Khởi tạo NavigationController instance
        - Thiết lập logging cho test (theo System Instruction)
        """
        function_name = "TestNavigationController.setUp"
        self.test_logger = get_logger('TestNavigationController')
        
        # Tạo Tkinter root window cho test (theo System Instruction - test isolation)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window để không hiển thị trong test
        
        # Khởi tạo NavigationController (theo System Instruction - test setup)
        self.navigation_controller = NavigationController(self.root, self.test_logger)
        
        # Log test setup (theo System Instruction - logging đầy đủ)
        write_log('INFO', function_name, "Test setup completed", self.test_logger)
    
    def tearDown(self):
        """
        Cleanup sau mỗi test case
        各テストケース後のクリーンアップ
        
        Mục đích:
        - Destroy all screens
        - Destroy root window
        - Log test cleanup (theo System Instruction)
        """
        function_name = "TestNavigationController.tearDown"
        
        # Cleanup: Destroy all screens (theo System Instruction - cleanup)
        for screen_name in list(self.navigation_controller.screens.keys()):
            try:
                self.navigation_controller.close_screen(screen_name)
            except Exception as e:
                write_log('WARNING', function_name, f"Error closing screen {screen_name}: {e}", self.test_logger)
        
        # Destroy root window (theo System Instruction - cleanup)
        try:
            self.root.destroy()
        except:
            pass
        
        # Log cleanup (theo System Instruction - logging đầy đủ)
        write_log('INFO', function_name, "Test cleanup completed", self.test_logger)
    
    def test_init(self):
        """
        Test NavigationController.__init__
        NavigationController初期化のテスト
        
        Mục đích:
        - NavigationControllerが正しく初期化されることを確認
        - Root window参照が正しく設定されることを確認
        - Loggerが正しく設定されることを確認
        
        Expected:
        - NavigationControllerインスタンスが作成される
        - root属性が設定される
        - logger属性が設定される
        - screensとscreen_classesが空の辞書で初期化される
        """
        function_name = "TestNavigationController.test_init"
        write_log('INFO', function_name, "Bắt đầu test", self.test_logger)
        
        # Test: NavigationController初期化 (theo System Instruction - test logic)
        nav_controller = NavigationController(self.root, self.test_logger)
        
        # Assert: Root window参照が正しく設定される (theo System Instruction - assertions)
        self.assertIsNotNone(nav_controller.root)
        self.assertEqual(nav_controller.root, self.root)
        
        # Assert: Loggerが設定される (theo System Instruction - logging check)
        self.assertIsNotNone(nav_controller.logger)
        
        # Assert: Screens registryが空で初期化される (theo System Instruction - initialization)
        self.assertIsInstance(nav_controller.screens, dict)
        self.assertEqual(len(nav_controller.screens), 0)
        
        # Assert: Screen classes registryが空で初期化される (theo System Instruction - initialization)
        self.assertIsInstance(nav_controller.screen_classes, dict)
        self.assertEqual(len(nav_controller.screen_classes), 0)
        
        write_log('INFO', function_name, "Test completed successfully", self.test_logger)
    
    def test_register_screen(self):
        """
        Test NavigationController.register_screen
        スクリーン登録のテスト
        
        Mục đích:
        - スクリーンクラスが正しく登録されることを確認
        - screen_classes辞書に追加されることを確認
        
        Expected:
        - screen_classesにスクリーンクラスが追加される
        """
        function_name = "TestNavigationController.test_register_screen"
        write_log('INFO', function_name, "Bắt đầu test", self.test_logger)
        
        # Test data: Mock screen class (theo System Instruction - test data)
        class MockScreen:
            def __init__(self, root, logger=None, **kwargs):
                """
                Mock Screen class cho testing
                NavigationControllerはloggerパラメータを渡すため、それを受け入れる必要がある
                """
                self.root = root
                self.logger = logger
        
        screen_name = "MockScreen"
        write_log('DEBUG', function_name, f"Test screen: {screen_name}", self.test_logger)
        
        # Test: スクリーン登録 (theo System Instruction - test logic)
        self.navigation_controller.register_screen(screen_name, MockScreen)
        
        # Assert: スクリーンクラスが登録される (theo System Instruction - assertions)
        self.assertIn(screen_name, self.navigation_controller.screen_classes)
        self.assertEqual(self.navigation_controller.screen_classes[screen_name], MockScreen)
        write_log('INFO', function_name, f"Screen registered: {screen_name}", self.test_logger)
        
        write_log('INFO', function_name, "Test completed successfully", self.test_logger)
    
    def test_open_screen(self):
        """
        Test NavigationController.open_screen
        スクリーンを開くテスト
        
        Mục đích:
        - 登録されたスクリーンが正しく開かれることを確認
        - screenインスタンスが作成されることを確認
        
        Expected:
        - screenインスタンスが作成される
        - screens辞書に追加される
        """
        function_name = "TestNavigationController.test_open_screen"
        write_log('INFO', function_name, "Bắt đầu test", self.test_logger)
        
        # Setup: スクリーンクラスを登録 (theo System Instruction - test setup)
        class MockScreen:
            def __init__(self, root, logger=None, **kwargs):
                """
                Mock Screen class cho testing
                NavigationControllerはloggerパラメータを渡すため、それを受け入れる必要がある
                """
                self.root = root
                self.logger = logger
                self.window = tk.Toplevel(root)
                self.window.withdraw()
        
        screen_name = "MockScreen"
        self.navigation_controller.register_screen(screen_name, MockScreen)
        write_log('DEBUG', function_name, f"Screen registered: {screen_name}", self.test_logger)
        
        # Test: スクリーンを開く (theo System Instruction - test logic)
        screen_instance = self.navigation_controller.open_screen(screen_name)
        
        # Assert: スクリーンインスタンスが作成される (theo System Instruction - assertions)
        self.assertIsNotNone(screen_instance)
        self.assertIn(screen_name, self.navigation_controller.screens)
        write_log('INFO', function_name, f"Screen opened: {screen_name}", self.test_logger)
        
        write_log('INFO', function_name, "Test completed successfully", self.test_logger)
    
    def test_close_screen(self):
        """
        Test NavigationController.close_screen
        スクリーンを閉じるテスト
        
        Mục đích:
        - 開かれているスクリーンが正しく閉じられることを確認
        - screens辞書から削除されることを確認
        
        Expected:
        - スクリーンが閉じられる
        - screens辞書から削除される
        """
        function_name = "TestNavigationController.test_close_screen"
        write_log('INFO', function_name, "Bắt đầu test", self.test_logger)
        
        # Setup: スクリーンを開く (theo System Instruction - test setup)
        class MockScreen:
            def __init__(self, root, logger=None, **kwargs):
                """
                Mock Screen class cho testing
                NavigationControllerはloggerパラメータを渡すため、それを受け入れる必要がある
                """
                self.root = root
                self.logger = logger
                self.window = tk.Toplevel(root)
                self.window.withdraw()
        
        screen_name = "MockScreen"
        self.navigation_controller.register_screen(screen_name, MockScreen)
        self.navigation_controller.open_screen(screen_name)
        write_log('DEBUG', function_name, f"Screen opened: {screen_name}", self.test_logger)
        
        # Assert: スクリーンが開かれている (theo System Instruction - pre-condition)
        self.assertIn(screen_name, self.navigation_controller.screens)
        
        # Test: スクリーンを閉じる (theo System Instruction - test logic)
        self.navigation_controller.close_screen(screen_name)
        
        # Assert: スクリーンが閉じられる (theo System Instruction - assertions)
        self.assertNotIn(screen_name, self.navigation_controller.screens)
        write_log('INFO', function_name, f"Screen closed: {screen_name}", self.test_logger)
        
        write_log('INFO', function_name, "Test completed successfully", self.test_logger)
    
    def test_close_screen_not_found(self):
        """
        Test NavigationController.close_screen - screen not found
        存在しないスクリーンを閉じるテスト
        
        Mục đích:
        - 存在しないスクリーンを閉じようとした場合のエラーハンドリングを確認
        - エラーが発生しないことを確認
        
        Expected:
        - エラーが発生しない
        - ログに警告が記録される
        """
        function_name = "TestNavigationController.test_close_screen_not_found"
        write_log('INFO', function_name, "Bắt đầu test", self.test_logger)
        
        # Test data: 存在しないスクリーン名 (theo System Instruction - error case test)
        non_existent_screen = "NonExistentScreen"
        write_log('DEBUG', function_name, f"Test screen: {non_existent_screen}", self.test_logger)
        
        # Test: 存在しないスクリーンを閉じる (theo System Instruction - test logic)
        # Should not raise exception (theo System Instruction - error handling)
        try:
            self.navigation_controller.close_screen(non_existent_screen)
            write_log('INFO', function_name, "Close screen completed without error", self.test_logger)
        except Exception as e:
            self.fail(f"close_screen should not raise exception: {e}")
        
        write_log('INFO', function_name, "Test completed successfully", self.test_logger)


if __name__ == '__main__':
    """
    Test runner
    テストランナー
    
    Mục đích:
    - テストスイートを実行
    - 詳細なログ出力を有効化 (theo System Instruction - logging đầy đủ)
    """
    # Setup logging cho test runner (theo System Instruction - logging setup)
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Run tests với verbosity (theo System Instruction - test execution)
    unittest.main(verbosity=2)

