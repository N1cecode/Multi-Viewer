from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class DrawLabel(QLabel):
    zoom_rect_moved_signal = pyqtSignal(int, int)
    zoom_area_captured_signal = pyqtSignal(QPixmap)
    mouse_tracking_signal = pyqtSignal(bool)
    comparison_ready_signal = pyqtSignal(bool)

    # ------------------------ Init ------------------------- #
    def __init__(self, select_rect_width=100, select_rect_height=100, enlarge_ratio=2.0):
        super().__init__()
        # Flags
        self.mouse_tracking_flag = True
        self.zoom_interpolation_flag = False
        
        # Parameters
        self.select_rect_width = select_rect_width
        self.select_rect_height = select_rect_height
        self.enlarge_ratio = enlarge_ratio
        self.zoom_area_width = int(self.select_rect_width * self.enlarge_ratio)
        self.zoom_area_height = int(self.select_rect_height * self.enlarge_ratio)
        self.mouse_x = 0
        self.mouse_y = 0
        
        ## 原图与缩放图的比例
        self.scale_ratio = 1
        self.origin_image = None  # 用于存储原图
        self.zoomed_area_pixmap = None # 放大区域
        
        self.setMouseTracking(self.mouse_tracking_flag)
        
        # Instances
        self.colors = {'red': QColor(255, 0, 0),
                       'white': QColor(255, 255, 255),
                       'black': QColor(0, 0, 0)
                       }
        self.pen = QPen(self.colors['red'])  # 设置框的颜色为红色
        self.pen.setWidth(3)  # 设置线条宽度为3像素
    # ----------------------- Function ---------------------- #
    def get_image_offset(self):
        label_width = self.width()
        label_height = self.height()

        pixmap = self.pixmap()
        if pixmap:
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()
        else:
            return 0, 0  # 如果没有图片，则偏移量为0

        x_offset = (label_width - pixmap_width) // 2 if label_width > pixmap_width else 0
        y_offset = (label_height - pixmap_height) // 2 if label_height > pixmap_height else 0

        return x_offset, y_offset

    def capture_zoom_area(self):
        x_offset, y_offset = self.get_image_offset()

        adjusted_x = (self.mouse_x - x_offset) * self.scale_ratio
        adjusted_y = (self.mouse_y - y_offset) * self.scale_ratio
        
        zoom_scaled_rect_width = int(self.select_rect_width * self.scale_ratio)
        zoom_scaled_rect_height = int(self.select_rect_height * self.scale_ratio)

        
        if self.origin_image and self.origin_image.width() > adjusted_x > 0 and self.origin_image.height() > adjusted_y > 0:
            rect = QRect(adjusted_x - zoom_scaled_rect_width // 2, 
                         adjusted_y - zoom_scaled_rect_height // 2,
                         zoom_scaled_rect_width,
                         zoom_scaled_rect_height)
            zoom_area = self.origin_image.copy(rect)
            # self.zoom_area_captured_signal.emit(zoom_area)
            if self.zoom_interpolation_flag:
                # 设置插值
                self.zoomed_area_pixmap = zoom_area.scaled(self.zoom_area_width, self.zoom_area_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                self.zoomed_area_pixmap = zoom_area.scaled(self.zoom_area_width, self.zoom_area_height, Qt.KeepAspectRatio)  # 更新属性并缩放
            
            
    def set_zoom_interpolation(self, flag):
        self.zoom_interpolation_flag = flag

    def update_zoom_rect(self, x, y):
        self.mouse_x = x
        self.mouse_y = y
        self.update_status()
    
    def update_tracking_flag(self, flag):
        self.mouse_tracking_flag = flag
        self.setMouseTracking(self.mouse_tracking_flag)
        if self.mouse_tracking_flag:
            self.pen.setColor(self.colors['red'])  # 设置框的颜色为红色
        else:
            self.pen.setColor(self.colors['black'])  # 设置框的颜色为白色
        self.update_status()
        
    def update_box(self):
        self.zoom_area_width = int(self.select_rect_width * self.enlarge_ratio)
        self.zoom_area_height = int(self.select_rect_height * self.enlarge_ratio)
        
    def update_status(self):
        self.update_box()
        self.capture_zoom_area()
        self.repaint()
        
    # ------------------------ Event ------------------------ #
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(self.pen)
        rect = QRect(self.mouse_x - self.select_rect_width // 2, self.mouse_y - self.select_rect_height // 2,
                     self.select_rect_width, self.select_rect_height)
        painter.drawRect(rect)
        
        # 绘制放大区域的图像
        if self.zoomed_area_pixmap:
            # painter.drawPixmap(self.mouse_x - self.zoom_area_width // 2, self.mouse_y - self.zoom_area_height // 2, self.zoomed_area_pixmap)
            if (self.mouse_x - self.select_rect_width//2) > self.zoom_area_width or (self.mouse_y - self.select_rect_height//2) > self.zoom_area_height:
                painter.drawPixmap(0, 0, self.zoomed_area_pixmap)
            else:
                painter.drawPixmap(self.width() - self.zoom_area_width, self.height() - self.zoom_area_height, self.zoomed_area_pixmap)

    def mouseMoveEvent(self, event):
        # 鼠标移动事件
        self.mouse_x = event.x()
        self.mouse_y = event.y()
        self.zoom_rect_moved_signal.emit(self.mouse_x, self.mouse_y)  # 发出信号
        self.capture_zoom_area()
        # self.repaint()
        
    def mousePressEvent(self, event):
        # 鼠标左键点击事件
        if event.button() == Qt.LeftButton:
            self.mouse_tracking_flag = not self.mouse_tracking_flag
            self.setMouseTracking(self.mouse_tracking_flag)
            # 发出信号
            self.mouse_tracking_signal.emit(self.mouse_tracking_flag)
            self.comparison_ready_signal.emit(not self.mouse_tracking_flag)

