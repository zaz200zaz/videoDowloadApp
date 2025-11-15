"""
Responsive Layout Utilities
Tiện ích cho responsive layout management

Mục tiêu:
- Quản lý layout responsive khi resize window
- Auto-resize icons và labels
- Grid-based layout system

Input/Output:
- Input: Window size, number of items, layout configuration
- Output: Grid positions và sizes cho items
"""

import tkinter as tk
from typing import List, Tuple, Dict, Optional
import logging
from utils.log_helper import get_logger
from gui.utils.ui_logger import log_ui_event


class ResponsiveGridLayout:
    """
    Responsive Grid Layout Manager
    
    Attributes:
        parent: Parent container
        columns: Số cột (default: 2)
        spacing: Khoảng cách giữa các items (default: 20)
        padding: Padding xung quanh (default: 20)
        logger: Logger instance (theo System Instruction)
    """
    
    def __init__(self, parent, columns: int = 2, spacing: int = 20, 
                 padding: int = 20, logger: Optional[logging.Logger] = None):
        """
        Khởi tạo ResponsiveGridLayout
        
        Args:
            parent: Parent container
            columns: Số cột trong grid (default: 2)
            spacing: Khoảng cách giữa các items (default: 20)
            padding: Padding xung quanh (default: 20)
            logger: Logger instance (theo System Instruction)
        """
        function_name = "ResponsiveGridLayout.__init__"
        self.logger = logger or get_logger('ResponsiveGridLayout')
        self.parent = parent
        self.columns = columns
        self.spacing = spacing
        self.padding = padding
        
        # Bind resize event (theo FR-001: layout responsive khi resize window)
        self.parent.bind("<Configure>", self._on_resize)
        self._last_size = None
        
        # Log initialization theo System Instruction
        from utils.log_helper import write_log
        write_log('INFO', function_name, f"ResponsiveGridLayout initialized with {columns} columns", self.logger)
    
    def _on_resize(self, event):
        """
        Event handler khi resize window (theo FR-001: responsive layout)
        
        Flow:
        1. Kiểm tra xem size có thay đổi không
        2. Ghi log resize event (theo System Instruction - DEBUG level)
        3. Cập nhật layout nếu cần
        """
        function_name = "ResponsiveGridLayout._on_resize"
        
        # Chỉ xử lý khi là main window resize (không phải child widgets)
        if event.widget != self.parent:
            return
        
        current_size = (event.width, event.height)
        
        # Chỉ log khi size thực sự thay đổi (tránh log spam)
        if current_size != self._last_size:
            # Log resize event (theo System Instruction - DEBUG level cho UI interactions)
            log_ui_event(self.logger, function_name, "window_resize", 
                        {"width": event.width, "height": event.height}, "DEBUG")
            self._last_size = current_size
    
    def calculate_grid_positions(self, num_items: int) -> List[Tuple[int, int]]:
        """
        Tính toán vị trí grid cho các items
        
        Args:
            num_items: Số lượng items cần layout
        
        Returns:
            List of (row, column) tuples
        """
        positions = []
        for i in range(num_items):
            row = i // self.columns
            col = i % self.columns
            positions.append((row, col))
        
        return positions
    
    def calculate_item_size(self, available_width: int, available_height: int, 
                           num_items: int) -> Tuple[int, int]:
        """
        Tính toán kích thước cho mỗi item dựa trên available space
        
        Args:
            available_width: Chiều rộng available
            available_height: Chiều cao available
            num_items: Số lượng items
        
        Returns:
            Tuple (item_width, item_height)
        """
        # Tính số hàng
        rows = (num_items + self.columns - 1) // self.columns
        
        # Tính kích thước item (trừ spacing và padding)
        item_width = (available_width - (self.columns + 1) * self.spacing - 2 * self.padding) // self.columns
        item_height = (available_height - (rows + 1) * self.spacing - 2 * self.padding) // rows
        
        # Đảm bảo minimum size
        item_width = max(item_width, 80)
        item_height = max(item_height, 100)
        
        return (item_width, item_height)

