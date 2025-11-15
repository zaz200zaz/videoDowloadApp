"""
Test Runner - Chạy tất cả test cases
全テストケースを実行するテストランナー

Mục đích:
- Chạy tất cả test cases trong dự án
- Generate test report
- Đảm bảo logging đầy đủ theo System Instruction
"""

import unittest
import sys
import os
import logging
from datetime import datetime

# Thêm project root vào path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def setup_test_logging():
    """
    Setup logging cho test runner
    テストランナーのロギング設定
    
    Mục đích:
    - Thiết lập logging format theo System Instruction
    - Tạo log file cho test run
    """
    function_name = "setup_test_logging"
    
    # Tạo log directory
    log_dir = os.path.join(project_root, "logs", "tests")
    os.makedirs(log_dir, exist_ok=True)
    
    # Tạo log file với timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"test_run_{timestamp}.log")
    
    # Setup logger
    logger = logging.getLogger('TestRunner')
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '[%(levelname)s] [%(name)s] %(message)s'
    ))
    logger.addHandler(console_handler)
    
    logger.info(f"[{function_name}] Test logging initialized")
    logger.info(f"[{function_name}] Log file: {log_file}")
    
    return logger, log_file


def run_all_tests():
    """
    Chạy tất cả test cases
    すべてのテストケースを実行
    
    Mục đích:
    - Discover và load tất cả test cases
    - Run tests với detailed output
    - Generate test report
    """
    function_name = "run_all_tests"
    
    # Setup logging
    logger, log_file = setup_test_logging()
    
    logger.info(f"[{function_name}] ============================================================")
    logger.info(f"[{function_name}] Bắt đầu chạy tất cả test cases")
    logger.info(f"[{function_name}] Project root: {project_root}")
    logger.info(f"[{function_name}] ============================================================")
    
    try:
        # Discover test cases
        loader = unittest.TestLoader()
        test_suite = loader.discover(
            start_dir=os.path.dirname(os.path.abspath(__file__)),
            pattern='test_*.py',
            top_level_dir=project_root
        )
        
        # Count test cases
        test_count = test_suite.countTestCases()
        logger.info(f"[{function_name}] Tìm thấy {test_count} test cases")
        
        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=True
        )
        
        logger.info(f"[{function_name}] Bắt đầu chạy tests...")
        result = runner.run(test_suite)
        
        # Log results
        logger.info(f"[{function_name}] ============================================================")
        logger.info(f"[{function_name}] Test Results:")
        logger.info(f"[{function_name}]   - Tests run: {result.testsRun}")
        logger.info(f"[{function_name}]   - Failures: {len(result.failures)}")
        logger.info(f"[{function_name}]   - Errors: {len(result.errors)}")
        logger.info(f"[{function_name}]   - Skipped: {len(result.skipped)}")
        logger.info(f"[{function_name}]   - Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.2f}%")
        logger.info(f"[{function_name}] ============================================================")
        
        # Log failures và errors
        if result.failures:
            logger.warning(f"[{function_name}] Failures ({len(result.failures)}):")
            for test, traceback in result.failures:
                logger.warning(f"[{function_name}]   - {test}: {traceback}")
        
        if result.errors:
            logger.error(f"[{function_name}] Errors ({len(result.errors)}):")
            for test, traceback in result.errors:
                logger.error(f"[{function_name}]   - {test}: {traceback}")
        
        # Return exit code
        if result.wasSuccessful():
            logger.info(f"[{function_name}] Tất cả tests PASSED")
            return 0
        else:
            logger.error(f"[{function_name}] Một số tests FAILED hoặc ERROR")
            return 1
        
    except Exception as e:
        logger.error(f"[{function_name}] Lỗi khi chạy tests: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)

