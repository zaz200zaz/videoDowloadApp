"""
Log Helper Utility
Hỗ trợ ghi log theo System Instruction format: [timestamp] [LEVEL] [Function] Message
"""

import logging
from typing import Optional
from functools import wraps
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    Lấy logger với tên cụ thể
    
    Args:
        name: Tên logger (thường là module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_function_call(logger: Optional[logging.Logger] = None, log_input: bool = True, log_output: bool = True):
    """
    Decorator để tự động log function call theo System Instruction
    
    Args:
        logger: Logger instance (None thì sử dụng function name)
        log_input: Có log input parameters không
        log_output: Có log output không
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Lấy logger
            func_logger = logger or get_logger(func.__module__)
            func_name = func.__name__
            
            # Log bắt đầu
            func_logger.info(f"[{func_name}] Bắt đầu")
            
            # Log input nếu cần
            if log_input and func_logger.isEnabledFor(logging.DEBUG):
                input_str = f"args={args}, kwargs={kwargs}" if args or kwargs else "không có parameters"
                func_logger.debug(f"[{func_name}] Input: {input_str}")
            
            try:
                # Gọi function
                result = func(*args, **kwargs)
                
                # Log output nếu cần
                if log_output and func_logger.isEnabledFor(logging.DEBUG):
                    func_logger.debug(f"[{func_name}] Output: {result}")
                
                # Log kết thúc thành công
                func_logger.info(f"[{func_name}] Hoàn thành thành công")
                
                return result
                
            except Exception as e:
                # Log lỗi với đầy đủ thông tin
                func_logger.error(
                    f"[{func_name}] Lỗi: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def write_log(level: str, function: str, message: str, logger: Optional[logging.Logger] = None, exc_info: Optional[bool] = None):
    """
    Ghi log theo format System Instruction: [timestamp] [LEVEL] [Function] Message
    
    Args:
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        function: Tên function đang ghi log
        message: Nội dung log
        logger: Logger instance (None thì sử dụng 'App')
        exc_info: Có log exception info không (chỉ dùng với ERROR/CRITICAL)
    """
    if logger is None:
        logger = get_logger('App')
    
    # Format message theo System Instruction
    formatted_message = f"[{function}] {message}"
    
    # Ghi log theo level
    level_upper = level.upper()
    if level_upper == 'DEBUG':
        logger.debug(formatted_message, exc_info=exc_info)
    elif level_upper == 'INFO':
        logger.info(formatted_message, exc_info=exc_info)
    elif level_upper == 'WARNING':
        logger.warning(formatted_message, exc_info=exc_info)
    elif level_upper == 'ERROR':
        logger.error(formatted_message, exc_info=exc_info if exc_info is not None else True)
    elif level_upper == 'CRITICAL':
        logger.critical(formatted_message, exc_info=exc_info if exc_info is not None else True)
    else:
        logger.info(formatted_message, exc_info=exc_info)


def log_api_call(logger: logging.Logger, function: str, url: str, method: str = "GET", 
                 status_code: Optional[int] = None, response_error: Optional[str] = None):
    """
    Log API call theo System Instruction
    
    Args:
        logger: Logger instance
        function: Tên function gọi API
        url: URL được gọi
        method: HTTP method
        status_code: HTTP status code (nếu có)
        response_error: Error message từ response (nếu có)
    """
    write_log('INFO', function, f"API Call: {method} {url[:100]}...", logger)
    
    if status_code:
        if status_code == 200:
            write_log('DEBUG', function, f"API Response: Status {status_code}", logger)
        else:
            write_log('WARNING', function, f"API Response: Status {status_code}", logger)
    
    if response_error:
        write_log('ERROR', function, f"API Error: {response_error}", logger)


def log_function_start(logger: logging.Logger, function: str, **kwargs):
    """
    Log khi function bắt đầu
    
    Args:
        logger: Logger instance
        function: Tên function
        **kwargs: Parameters để log
    """
    params_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()]) if kwargs else "không có parameters"
    write_log('INFO', function, f"Bắt đầu - {params_str}", logger)


def log_function_end(logger: logging.Logger, function: str, success: bool = True, result: Optional[str] = None):
    """
    Log khi function kết thúc
    
    Args:
        logger: Logger instance
        function: Tên function
        success: Thành công hay không
        result: Kết quả (optional)
    """
    status = "thành công" if success else "thất bại"
    message = f"Hoàn thành - {status}"
    if result:
        message += f" - {result}"
    
    level = 'INFO' if success else 'ERROR'
    write_log(level, function, message, logger)

