import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QMenu, QAction,
    QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage
from PyQt5.QtCore import Qt, QRect, QPoint


class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.setMouseTracking(True)

        self.original_image = None
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selection_rect = QRect()
        self.cropping = False

        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(False)

        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                background-color: #f0f0f0;
                color: #555;
            }
        """)

        self.setText("Drag and drop an image here")

    # ----------------------------------------------------
    # DRAG & DROP
    # ----------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toLocalFile().lower()
            if url.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                event.accept()
                self.setStyleSheet(
                    "QLabel { border: 2px dashed #00bfff; background-color: #e6f7ff; color:#555; }"
                )
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(
            "QLabel { border: 2px dashed #aaa; background-color: #f0f0f0; color:#555; }"
        )
        event.accept()

    def dropEvent(self, event):
        self.setStyleSheet(
            "QLabel { border: 2px dashed #aaa; background-color:#f0f0f0; color:#555; }"
        )
        path = event.mimeData().urls()[0].toLocalFile()
        self.load_image(path)

    # ----------------------------------------------------
    # LOAD IMAGE - WITHOUT WINDOW RESIZE
    # ----------------------------------------------------
    def load_image(self, path):
        image = QImage(path)

        if image.isNull():
            QMessageBox.warning(self, "Error", "This is not a valid image.")
            return

        self.original_image = image

        # Scale ONLY inside current label
        scaled = image.scaled(
            self.width(),
            self.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(QPixmap.fromImage(scaled))
        self.selection_rect = QRect()
        self.setText("")
        self.update()

    # ----------------------------------------------------
    # CROPPING MOUSE EVENTS
    # ----------------------------------------------------
    def mousePressEvent(self, event):
        if self.original_image is None:
            return

        if event.button() == Qt.LeftButton:
            self.cropping = True
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.selection_rect = QRect()
            self.update()

        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        if self.cropping:
            self.end_point = event.pos()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.cropping = False
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    # ----------------------------------------------------
    # DRAW SELECTION RECT
    # ----------------------------------------------------
    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.selection_rect.isNull():
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine))
            painter.drawRect(self.selection_rect)

    # ----------------------------------------------------
    # CONTEXT MENU
    # ----------------------------------------------------
    def show_context_menu(self, pos):
        menu = QMenu(self)

        crop_action = QAction("✔ Crop", self)
        crop_action.setEnabled(not self.selection_rect.isNull())
        crop_action.triggered.connect(self.crop_image)
        menu.addAction(crop_action)

        save_action = QAction("💾 Save Image", self)
        save_action.triggered.connect(self.save_image)
        menu.addAction(save_action)

        menu.exec_(pos)

    # ----------------------------------------------------
    # CROP LOGIC
    # ----------------------------------------------------
    def crop_image(self):
        if self.original_image is None or self.selection_rect.isNull():
            return

        displayed = self.pixmap()
        scaled_w = displayed.width()
        scaled_h = displayed.height()

        x_offset = (self.width() - scaled_w) // 2
        y_offset = (self.height() - scaled_h) // 2

        sx = max(0, self.selection_rect.x() - x_offset)
        sy = max(0, self.selection_rect.y() - y_offset)
        sw = min(self.selection_rect.width(), scaled_w - sx)
        sh = min(self.selection_rect.height(), scaled_h - sy)

        scale_factor = self.original_image.width() / scaled_w

        real_rect = QRect(
            int(sx * scale_factor),
            int(sy * scale_factor),
            int(sw * scale_factor),
            int(sh * scale_factor)
        )

        cropped = self.original_image.copy(real_rect)
        self.original_image = cropped

        scaled = cropped.scaled(
            self.width(),
            self.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(QPixmap.fromImage(scaled))
        self.selection_rect = QRect()
        self.update()

    # ----------------------------------------------------
    # SAVE IMAGE WITH RESIZE PERCENTAGE
    # ----------------------------------------------------
    def save_image(self):
        if self.original_image is None:
            return

        percent, ok = QInputDialog.getInt(
            self, "Resize Percentage",
            "Choose resize percentage (10–100):",
            100, 10, 100, 10
        )

        if not ok:
            return

        new_img = self.original_image.scaled(
            int(self.original_image.width() * percent / 100),
            int(self.original_image.height() * percent / 100),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        now = datetime.now()
        default_name = f"Image_{now:%Y-%m-%d_%H-%M-%S}.png"
        default_path = os.path.join(desktop, default_name)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image",
            default_path,
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;All Files (*)"
        )

        if file_path:
            if new_img.save(file_path):
                QMessageBox.information(self, "Success", "Image saved successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to save image.")


class ImageCropperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fast Image Crop & Resize -  https://github.com/alizangeneh")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.label = ImageLabel(self)
        layout.addWidget(self.label)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ImageCropperApp()
    win.show()
    sys.exit(app.exec_())
