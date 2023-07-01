import sys
import os
import clipboard
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QColorDialog, QHBoxLayout, QSlider, QSpacerItem, QSizePolicy, QFileDialog
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QPainterPath, QKeySequence
from PyQt5.QtCore import Qt, QRect, QSize, QMimeData, QIODevice


class PaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint Uygulaması")
        self.setGeometry(100, 100, 800, 600)
        self.canvas = CanvasWidget()
        self.setCentralWidget(self.canvas)

        self.toolbar = self.addToolBar("Araçlar")
        self.brush_button = QPushButton("Fırça", self)
        self.brush_button.clicked.connect(self.canvas.open_color_dialog)
        self.toolbar.addWidget(self.brush_button)

        self.eraser_button = QPushButton("Silgi", self)
        self.eraser_button.clicked.connect(self.canvas.set_eraser_mode)
        self.toolbar.addWidget(self.eraser_button)

        self.clear_button = QPushButton("Temizle", self)
        self.clear_button.clicked.connect(self.canvas.clear_canvas)
        self.toolbar.addWidget(self.clear_button)

        self.slider_button = QPushButton("Slider", self)
        self.slider_button.setCheckable(True)
        self.slider_button.toggled.connect(self.handle_slider_button_toggle)
        self.toolbar.addWidget(self.slider_button)

        self.import_button = QPushButton("Dışarıdan Aktar", self)
        self.import_button.clicked.connect(self.canvas.import_image)
        self.toolbar.addWidget(self.import_button)

        self.brush_size_slider = QSlider(Qt.Horizontal)
        self.brush_size_slider.setMinimum(1)
        self.brush_size_slider.setMaximum(10)
        self.brush_size_slider.setValue(self.canvas.brush_size)
        self.brush_size_slider.setTickInterval(1)
        self.brush_size_slider.setTickPosition(QSlider.TicksBelow)
        self.brush_size_slider.valueChanged.connect(self.canvas.set_brush_size)

        self.brush_size_slider.hide()

        spacer_item = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QHBoxLayout()
        layout.addWidget(self.brush_size_slider)
        layout.addItem(spacer_item)
        widget = QWidget()
        widget.setLayout(layout)
        self.toolbar.addWidget(widget)

        self.color_buttons = []
        self.create_color_buttons()

    def create_color_buttons(self):
        color_palette = [
            QColor(0, 0, 0), QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
            QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255), QColor(128, 128, 128)
        ]

        color_layout = QHBoxLayout()
        for color in color_palette:
            button = QPushButton(self)
            button.setMaximumSize(QSize(30, 30))
            button.setStyleSheet(f"background-color: {color.name()}")
            button.clicked.connect(lambda _, c=color: self.canvas.set_brush_color(c))
            color_layout.addWidget(button)
            self.color_buttons.append(button)

        color_widget = QWidget()
        color_widget.setLayout(color_layout)
        self.toolbar.addWidget(color_widget)

    def handle_slider_button_toggle(self, checked):
        if checked:
            self.brush_size_slider.show()
        else:
            self.brush_size_slider.hide()


class CanvasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.drawing = False
        self.brush_mode = True
        self.brush_size = 2
        self.brush_color = QColor(0, 0, 0)
        self.last_point = None
        self.image = QPixmap(self.size())
        self.image.fill(Qt.white)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image, self.image.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.image)
            painter.setRenderHint(QPainter.Antialiasing, True)
            pen = QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            if self.brush_mode:
                painter.setPen(pen)
            else:
                eraser_color = QColor(255, 255, 255)  # Beyaz renk silgi için kullanılır
                pen.setColor(eraser_color)
                painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False

    def resizeEvent(self, event):
        new_image = QPixmap(event.size())
        new_image.fill(Qt.white)
        painter = QPainter(new_image)
        painter.drawPixmap(self.rect(), self.image, self.image.rect())
        self.image = new_image

    def set_brush_color(self, color):
        self.brush_color = color

    def set_brush_size(self, size):
        self.brush_size = size

    def set_brush_mode(self):
        self.brush_mode = True

    def set_eraser_mode(self):
        self.brush_mode = False

    def clear_canvas(self):
        self.image.fill(Qt.white)
        self.update()

    def import_image(self):
        file_dialog = QFileDialog()
        image_file, _ = file_dialog.getOpenFileName(self, "Resim Seç", "", "Image Files (*.png *.jpg *.jpeg)")
        if image_file:
            image = QPixmap(image_file)
            if not image.isNull():
                self.image = image.scaled(self.size())
                self.update()

    def paste_image(self):
        clipboard_image = clipboard.image()
        if clipboard_image and not clipboard_image.isNull():
            self.image = clipboard_image.scaled(self.size())
            self.update()

    def open_color_dialog(self):
        color = QColorDialog.getColor(self.brush_color, self, "Fırça Rengini Seç")
        if color.isValid():
            self.brush_color = color

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            self.paste_image()

    def closeEvent(self, event):
        if not self.image.save("painting.png"):
            print("Resim kaydedilemedi!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintApp()
    window.show()
    sys.exit(app.exec_())
