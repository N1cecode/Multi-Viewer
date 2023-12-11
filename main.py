from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import numpy as np
import os, sys, cv2

from src.draw_label import DrawLabel


class MainUI(QMainWindow):
    # ------------------------ Init ------------------------- #
    def __init__(self):
        super().__init__()

        # 绘图背景
        pg.setConfigOption('background', '#FFFFFF')
        # pg.setConfigOption('foreground', 'd')
        pg.setConfigOptions(antialias = True)

        self.num_of_folder = None
        self.raw_col_dict = {'2':(1, 2), '3':(1, 3), '4':(2, 2),
                             '5':(2, 3), '6':(2, 3)
                             }
        self.num_of_raw = None
        self.num_of_col = None
        self.compare_window = None
        self.init_ui()

        # 状态栏
        self.status = self.statusBar()
        self.status.showMessage('主界面')

        # 标题栏
        self.setWindowTitle('Multi-Viewer')

    def init_ui(self):
        self.get_num_folder()
        (self.num_of_raw, self.num_of_col) = self.raw_col_dict[str(self.num_of_folder)]
        
        # 窗口主部件
        self.main_widget = QWidget()
        # 主部件的网格布局
        self.main_layout = QGridLayout()
        # 设置主部件布局为网格布局
        self.main_widget.setLayout(self.main_layout)

        # 创建左侧部件
        self.left_widget = QWidget()
        self.left_widget.setObjectName('left_widget')
        # 创建左侧部件的网格布局层
        self.left_layout = QGridLayout()
        # 设置左侧部件布局为网格
        self.left_widget.setLayout(self.left_layout)

        # 创建右侧部件
        self.right_widget = QWidget()
        self.right_widget.setObjectName('right_widget')
        self.right_layout = QGridLayout()
        self.right_widget.setLayout(self.right_layout)
        
        # 创建分隔器
        splitter = QSplitter(Qt.Horizontal)
       
        # 将左侧和右侧的部件添加到分隔器中
        splitter.addWidget(self.left_widget)
        splitter.addWidget(self.right_widget)
        splitter.setSizes([200, 1700])

        self.main_layout.addWidget(splitter, 0, 0, 1, 1)
        
        # # 左侧部件在第0行第0列，占12行5列
        # self.main_layout.addWidget(self.left_widget, 0, 0, 12, 1)
        # # 右侧部件在第0行第6列，占12行7列
        # self.main_layout.addWidget(self.right_widget, 0, 2, 12, 8)
        # 设置窗口主部件
        self.setCentralWidget(self.main_widget)

        self.init_left()
        self.init_right()
        
        # 外观美化
        # self.setWindowOpacity(0.9)
        # self.main_layout.setSpacing(0)
        # self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # 最大化窗口
        self.showMaximized()

    def init_left(self):
        # 根据需要对比的文件夹数量定义button
        self.btn_label_list = []
        for i in range(self.num_of_folder):
            self.btn_label_list.append(QPushButton(f"Dir {i+1}"))
            # self.btn_label_list[i].setEnabled(False)
            self.btn_label_list[i].directory = None
            self.btn_label_list[i].clicked.connect(self.select_dir)

        for i in range(self.num_of_folder):
            self.left_layout.addWidget(self.btn_label_list[i])
            
        # 图片列表
        self.list_img = QListWidget()
        self.list_img.itemSelectionChanged.connect(self.show_selected_img)
        self.left_layout.addWidget(self.list_img)
        
        # 创建分割线1
        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        h_line.setFrameShadow(QFrame.Sunken)
        
        self.left_layout.addWidget(h_line)
        
        # 放大区域选项
        self.label_zoom_area = QLabel("放大区域选项")
        self.label_zoom_area.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.label_zoom_area)
        
        ## 选择是否插值
        self.radio_interpolation = QRadioButton('插值', self)
        self.radio_interpolation.setChecked(False)
        self.radio_interpolation.toggled.connect(self.set_zoom_interpolation)
        self.left_layout.addWidget(self.radio_interpolation)
        
        ## 控件显示放大倍数
        ### 创建水平布局
        enlarge_layout = QHBoxLayout()
        enlarge_container = QWidget()
        enlarge_container.setLayout(enlarge_layout)
        
        label_enlarge = QLabel("Enlarge Ratio:")
        enlarge_layout.addWidget(label_enlarge)
        
        self.text_enlarge = QLineEdit()
        self.text_enlarge.setText(f"{2.0:2}")
        self.text_enlarge.setReadOnly(True)  # 设置为只读
        enlarge_layout.addWidget(self.text_enlarge)
        
        self.left_layout.addWidget(enlarge_container)
        
        self.slider_enlarge = QSlider(Qt.Horizontal, self)
        self.slider_enlarge.setMinimum(10)
        self.slider_enlarge.setMaximum(30)
        self.slider_enlarge.setValue(20)
        self.left_layout.addWidget(self.slider_enlarge)
        self.slider_enlarge.valueChanged.connect(self.change_enlarge_ratio)

        # 创建水平布局
        input_layout = QHBoxLayout()
        input_container = QWidget()
        input_container.setLayout(input_layout)
        
        # lineEdit to input width
        self.input_width = QLineEdit()
        self.input_width.setPlaceholderText("Width")
        self.input_width.setValidator(QIntValidator())
        # self.input_width.returnPressed.connect(self.match_city)
        input_layout.addWidget(self.input_width)
        
        # lineEdit to input height
        self.input_height = QLineEdit()
        self.input_height.setPlaceholderText("Height")
        self.input_height.setValidator(QIntValidator())
        # self.input_height.returnPressed.connect(self.match_city)
        input_layout.addWidget(self.input_height)
        
        self.left_layout.addWidget(input_container)
        
        # 创建Button，改变Box大小
        self.btn_box = QPushButton("设置Box")
        # self.btn_box.setEnabled(False)
        self.btn_box.clicked.connect(self.change_box)
        self.left_layout.addWidget(self.btn_box)
        
        # 创建分割线2
        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        h_line.setFrameShadow(QFrame.Sunken)
        self.left_layout.addWidget(h_line)

        # save figure and quit window
        self.btn_fig = QPushButton("对比图")
        self.btn_fig.setEnabled(False)
        self.btn_fig.clicked.connect(self.compare_select_area)
        self.left_layout.addWidget(self.btn_fig)

        self.btn_reset = QPushButton("重置")
        self.btn_reset.clicked.connect(self.reset)
        self.left_layout.addWidget(self.btn_reset)
        
        self.btn_quit = QPushButton("退出")
        self.btn_quit.clicked.connect(self.quit_act)
        self.left_layout.addWidget(self.btn_quit)

        # tablewidgt to view data
        # self.query_result = QTableWidget()
        # self.left_layout.addWidget(self.query_result, self.num_of_folder + 4, 0, 2, 1)
        # self.query_result.verticalHeader().setVisible(False)

    def init_right(self):
        self.label = QLabel()
        self.right_layout.addWidget(self.label, 0, 0, self.num_of_raw, self.num_of_col)

        self.plot_list = []
        for i in range(self.num_of_folder):
            img_label = DrawLabel()
            # img_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            # img_label.setFixedSize(img_label.width(), img_label.height())
            img_label.setFrameStyle(QFrame.StyledPanel)
            img_label.setAlignment(Qt.AlignCenter)
            # img_label.setScaledContents(True)
            self.plot_list.append(img_label)
            # self.plot_list[i].setMinimumSize(400, 400)
            row = i // self.num_of_col  # 整除得到行号
            col = i % self.num_of_col   # 取余得到列号
            self.right_layout.addWidget(self.plot_list[i], row, col, 1, 1)

        for i in range(self.num_of_folder):
            # 连接信号
            self.plot_list[i].zoom_rect_moved_signal.connect(self.sync_zoom_rect)
            self.plot_list[i].mouse_tracking_signal.connect(self.sync_mouse_tracking)
            self.plot_list[i].comparison_ready_signal.connect(self.comparison_ready)

    # ----------------------- Function ---------------------- #
    def change_box(self):
        for draw_label in self.plot_list:
            draw_label.select_rect_width = int(self.input_width.text())
            draw_label.select_rect_height = int(self.input_height.text())
            draw_label.update_box()
    
    def change_enlarge_ratio(self, value):
        self.text_enlarge.setText(f"{(value/10):2}")
        for draw_label in self.plot_list:
            draw_label.enlarge_ratio = value / 10
            draw_label.update_box()
            
    def comparison_ready(self, flag):
        self.btn_fig.setEnabled(flag)
            
    def get_num_folder(self):
        num_str, ok = QInputDialog.getText(self, '对比个数', '输入需要对比的文件夹个数：')
        if ok:
            if num_str.isdigit() and int(num_str) <= 6 and int(num_str) >= 2:
                self.num_of_folder = int(num_str)
            elif int(num_str) > 6 or int(num_str) < 2:
                print("对比文件夹数需在2-6个，请重新输入。")
                self.get_num_folder()
            else:
                print("输入的不是数字，请重新输入。")
                self.get_num_folder()
                
    def sync_zoom_rect(self, x, y):
        # 更新所有DrawLabel的视图
        for img_label in self.plot_list:
            img_label.update_zoom_rect(x, y)
    
    def sync_mouse_tracking(self, flag):
        # 更新所有mouse tracking flag
        for img_label in self.plot_list:
            img_label.update_tracking_flag(flag)
            
    def select_dir(self):
        button = self.sender()

        directory = QFileDialog.getExistingDirectory(self, "选择文件夹")

        if directory:
            button.directory = directory
            button.setText('.../'+directory.split('/')[-2]+'/'+directory.split('/')[-1])
        
        self.read_list_img()

    def read_list_img(self):
        self.list_img.clear()
        files = set(os.listdir(self.btn_label_list[0].directory))
        for filename in files:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    self.list_img.addItem(filename)

    def show_selected_img(self):
        selected_img = self.list_img.selectedItems()
        if selected_img:
            filename = selected_img[0].text()
            for i, btn in enumerate(self.btn_label_list):
                # 清空QLabel
                self.plot_list[i].setPixmap(QPixmap())
                if btn.directory:
                    print(btn.directory)
                    img_path = os.path.join(btn.directory, filename)
                    pixmap = QPixmap(img_path)
                    self.plot_list[i].origin_image = pixmap
                    self.plot_list[i].setFixedSize(self.plot_list[i].width(), self.plot_list[i].height())
                    self.plot_list[i].setPixmap(pixmap.scaled(self.plot_list[i].width(), self.plot_list[i].height(), 
                                                              Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    self.plot_list[i].scale_ratio = self.plot_list[i].origin_image.height() / self.plot_list[i].pixmap().height()
                    # self.plot_list[i].show()
    
    def compare_select_area(self):
        # 创建子窗口来展示选中区域
        self.compare_window = QWidget()
        self.compare_window.setWindowTitle('对比图')
        main_layout = QGridLayout(self.compare_window)
        main_layout.setSpacing(0)
        
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        

        # 遍历所有 DrawLabel 实例并获取 zoomed_area_pixmap
        for i, draw_label in enumerate(self.plot_list):
            if draw_label.zoomed_area_pixmap:
                # 创建垂直布局
                vertical_layout = QVBoxLayout()
                vertical_layout.setSpacing(0)
                vertical_container = QWidget()
                vertical_container.setLayout(vertical_layout)
                
                # 图像标签
                img_label = QLabel()
                img_label.setPixmap(draw_label.zoomed_area_pixmap)
                
                # 文字标签
                text_label = QLabel(f"{self.btn_label_list[i].text()}")
                text_label.setAlignment(Qt.AlignCenter)
                
                vertical_layout.addWidget(img_label)
                vertical_layout.addWidget(text_label)
                
                row = i // self.num_of_col  # 例如，每行显示2个区域
                col = i % self.num_of_col
                
                grid_layout.addWidget(vertical_container, row, col)

        main_layout.addWidget(grid_widget)

        # 保存按钮
        save_button = QPushButton("保存对比图")
        save_button.clicked.connect(self.save_comparison)
        main_layout.addWidget(save_button)
        
        self.compare_window.setLayout(main_layout)
        self.set_window_center(self.compare_window)
        self.compare_window.show()
        
    def get_screen_size(self, screen_num):
        # 获取当前屏幕的尺寸
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry(screen_num)
        return screen_geometry
    
    def get_num_folder(self):
        num_str, ok = QInputDialog.getText(self, '对比个数', '输入需要对比的文件夹个数：')
        
        desktop = QDesktopWidget()
        screen_num = desktop.screenNumber(self.frameGeometry().topLeft())
        self.set_font(screen_num)
        
        if ok:
            if num_str.isdigit() and int(num_str) <= 6 and int(num_str) >= 2:
                self.num_of_folder = int(num_str)
            elif int(num_str) > 6 or int(num_str) < 2:
                print("对比文件夹数需在2-6个，请重新输入。")
                self.get_num_folder()
            else:
                print("输入的不是数字，请重新输入。")
                self.get_num_folder()
                
    def read_list_img(self):
        self.list_img.clear()
        files = set(os.listdir(self.btn_label_list[0].directory))
        
        image_files = [filename for filename in files if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        sorted_image_files = sorted(image_files)

        # 将排序后的文件添加到列表中
        for filename in sorted_image_files:
            self.list_img.addItem(filename)
    
    def sync_zoom_rect(self, x, y):
        # 更新所有DrawLabel的视图
        for img_label in self.plot_list:
            img_label.update_zoom_rect(x, y)
    
    def sync_mouse_tracking(self, flag):
        # 更新所有mouse tracking flag
        for img_label in self.plot_list:
            img_label.update_tracking_flag(flag)
            
    def select_dir(self):
        button = self.sender()

        directory = QFileDialog.getExistingDirectory(self, "选择文件夹")

        if directory:
            button.directory = directory
            button.setText('.../'+directory.split('/')[-2]+'/'+directory.split('/')[-1])
        
        self.read_list_img()

    def set_font(self, screen_num):
        # ratio = 140
        self.screen_size = self.get_screen_size(screen_num)
        print('Screen num:', screen_num, 'Screen size:', self.screen_size.width(), self.screen_size.height())
        resolution = min(self.screen_size.width(), self.screen_size.height())
        if resolution == 1080:
            font_size = 10
        elif resolution == 2160:
            font_size = 16
        # font_size = min(self.screen_size.width(), self.screen_size.height()) // ratio
        font = QFont()
        font.setPointSize(font_size)
        QApplication.setFont(font)
    
    def set_zoom_interpolation(self):
        for img_label in self.plot_list:
            img_label.set_zoom_interpolation(self.radio_interpolation.isChecked())
            img_label.update_status()
        
    # 令窗口位于中心位置
    def set_window_center(self, window):
        # 获取屏幕尺寸
        screen_geometry = QDesktopWidget().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # 计算窗口位置
        window_size = window.geometry()
        window_x = int((screen_width - window_size.width()) / 2)
        window_y = int((screen_height - window_size.height()) / 2)

        # 移动窗口
        window.move(window_x, window_y)
    
    def save_comparison(self):
        # 保存逻辑
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self.compare_window, 
                                                  "Save File", "", 
                                                  "Images (*.png *.xpm *.jpg);;All Files (*)", 
                                                  options=options)
        # TODO 保存对比图的逻辑
        if filename:
            pass
    
    # TODO
    def calculate_patch_psnr(self):
        pass
    
    def quit_act(self):
        # sender 发送信号的对象
        sender = self.sender()
        qApp = QApplication.instance()
        qApp.quit()
    
    def reset(self):
        self.close()
        self.__init__()
    # ------------------------ Event ------------------------ #
    


def main():
    app = QApplication(sys.argv)
    gui = MainUI()
    # gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
