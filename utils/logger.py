"""
Logger Utility
ログ設定ユーティリティ
"""

import logging
import os
from datetime import datetime
from typing import Optional, Tuple


def setup_logger(name: str, log_dir: Optional[str] = None) -> Tuple[logging.Logger, Optional[str]]:
    """
    ロガーを設定する
    
    Args:
        name: ロガー名
        log_dir: ログディレクトリ（Noneの場合は自動生成）
        
    Returns:
        (logger, log_file_path) のタプル
    """
    try:
        if log_dir is None:
            # スクリプトのディレクトリを基準にlogs/を作成
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_dir = os.path.join(script_dir, "logs")
        
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
        
        # ロガーを作成
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # 既存のハンドラーをクリア
        logger.handlers = []
        
        # ファイルハンドラー
        file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        logger.info(f"Logger initialized. Log file: {log_file}")
        return logger, log_file
        
    except Exception as e:
        # フォールバック: コンソールのみのロガー
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.handlers = []
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        logger.warning(f"Could not create log file: {e}")
        return logger, None

