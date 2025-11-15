"""
UI Logger Utility
Tiện ích ghi log cho UI components theo System Instruction

Mục tiêu:
- Cung cấp logging utilities cho UI components
- Format log theo System Instruction: [timestamp] [LEVEL] [Function] Message
- Hỗ trợ UI-specific context (screen name, component ID)

Input/Output:
- Input: Log level, function name, message, UI context (optional)
- Output: Formatted log message written to logger
"""

import logging
from typing import Optional
from utils.log_helper import write_log, get_logger


def get_ui_logger(name: str, screen_name: Optional[str] = None) -> logging.Logger:
    """
    Lấy logger cho UI component với context
    
    Args:
        name: Tên logger (thường là component name)
        screen_name: Tên screen (optional, để thêm context)
        
    Returns:
        Logger instance với context
    """
    logger_name = f"{screen_name}.{name}" if screen_name else name
    return get_logger(logger_name)


def log_ui_action(logger: logging.Logger, function: str, action: str, 
                  component_id: Optional[str] = None, level: str = "INFO", 
                  details: Optional[str] = None):
    """
    Ghi log cho UI action theo System Instruction
    
    Args:
        logger: Logger instance
        function: Tên function đang ghi log
        action: Hành động (click, hover, resize, etc.)
        component_id: ID của component (optional)
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        details: Chi tiết thêm (optional)
    
    Examples:
        log_ui_action(logger, "MainDashboard.on_download_click", "click", "btnDownloadDouyin")
        log_ui_action(logger, "MainDashboard.on_button_hover", "hover", "btnDownloadDouyin", "DEBUG")
    """
    message = f"UI Action: {action}"
    if component_id:
        message += f" - Component ID: {component_id}"
    if details:
        message += f" - {details}"
    
    write_log(level, function, message, logger)


def log_screen_navigation(logger: logging.Logger, function: str, 
                         from_screen: str, to_screen: str, 
                         success: bool = True, error: Optional[str] = None):
    """
    Ghi log cho screen navigation theo System Instruction
    
    Args:
        logger: Logger instance
        function: Tên function đang ghi log
        from_screen: Tên screen hiện tại
        to_screen: Tên screen đích
        success: Thành công hay không
        error: Error message nếu có (optional)
    
    Examples:
        log_screen_navigation(logger, "NavigationController.open_screen", 
                            "MainDashboard", "DownloadDouyinScreen", True)
    """
    level = "INFO" if success else "WARNING" if error else "ERROR"
    message = f"Screen Navigation: {from_screen} -> {to_screen}"
    if error:
        message += f" - Error: {error}"
    
    write_log(level, function, message, logger, exc_info=bool(error))


def log_ui_event(logger: logging.Logger, function: str, event_type: str,
                event_data: Optional[dict] = None, level: str = "DEBUG"):
    """
    Ghi log cho UI event theo System Instruction
    
    Args:
        logger: Logger instance
        function: Tên function đang ghi log
        event_type: Loại event (hover, resize, focus, etc.)
        event_data: Dữ liệu event (optional)
        level: Log level (default: DEBUG cho UI interactions)
    
    Examples:
        log_ui_event(logger, "MainDashboard.on_window_resize", "resize", 
                    {"width": 800, "height": 600})
    """
    message = f"UI Event: {event_type}"
    if event_data:
        data_str = ", ".join([f"{k}={v}" for k, v in event_data.items()])
        message += f" - {data_str}"
    
    write_log(level, function, message, logger)

