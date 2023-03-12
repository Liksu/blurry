import os
import sys

import cv2
from PyQt5.QtCore import Qt, QRectF, QSize, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QPen, QKeySequence, QImage, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, \
    QShortcut, QGraphicsRectItem, QStyle


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create graphics view and set scene
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)

        self.connect_shortcuts()

        # explicit define properties
        self.folder = None
        self.files = None
        self.image_position_in_folder = None
        self.image_path = None
        self.file_name = None
        self.image = None
        self.image_pos = None
        self.selection_rect = None
        self.selection_start = None
        self.modified = False

        # run before the main window is shown
        self.open_folder()

        # set up the window
        self.update_title()
        self.showMaximized()

        # get the available screen geometry
        screen_geometry = QApplication.desktop().availableGeometry(self)
        style = QApplication.style()

        # adjust the view size
        view_height = screen_geometry.height() - style.pixelMetric(QStyle.PM_TitleBarHeight, None, self)
        self.view_size = QSize(screen_geometry.width(), view_height)
        self.view.setFixedSize(self.view_size)
        self.scene.setSceneRect(0, 0, self.view_size.width(), self.view_size.height())

        # configure the view
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        # start the image processing
        self.scene.clear()
        self.next_image(direction=0)

    def shortcut(self, key, function):
        shortcut = QShortcut(QKeySequence(key), self)
        shortcut.activated.connect(function)
        return shortcut

    def connect_shortcuts(self):
        # Connect mouse events to methods
        self.view.mousePressEvent = self.mousePressEvent
        self.view.mouseMoveEvent = self.mouseMoveEvent
        self.view.mouseReleaseEvent = self.mouseReleaseEvent

        # Esc to quit
        self.shortcut_quit = self.shortcut(Qt.Key_Escape, self.close)

        # Space to save changes and move to the next image
        self.shortcut_done = self.shortcut(Qt.Key_Space, self.save_and_next)

        # S to save changes
        self.shortcut_save = self.shortcut(Qt.Key_S, self.save)

        # R to reset current image and start blurring again
        self.shortcut_reset = self.shortcut(Qt.Key_R, self.read_image)

        # N or → to skip current image and open the next one
        self.shortcut_next_n = self.shortcut(Qt.Key_N, self.next_image)
        self.shortcut_next_right = self.shortcut(Qt.Key_Right, self.next_image)

        # P or ← to skip current image and open the previous one
        self.shortcut_prev_p = self.shortcut(Qt.Key_P, self.prev_image)
        self.shortcut_prev_left = self.shortcut(Qt.Key_Left, self.prev_image)

    def set_selection(self):
        # Set up selection rectangle item
        self.selection_rect = QGraphicsRectItem()
        self.selection_rect.setPen(QPen(QColor("red"), 2, Qt.DashLine))
        self.selection_rect.hide()
        self.scene.addItem(self.selection_rect)

    def update_title(self):
        self.setWindowTitle("Blurry - "
                            + (self.file_name if self.file_name is not None else "No file selected")
                            + ('*' if self.modified else ''))

    def open_folder(self):
        # open a dialog to select a folder
        self.folder = QFileDialog.getExistingDirectory(self, "Select Directory")

        if self.folder == '':
            sys.exit()

        # get a list of all image files in the folder
        self.files = [f for f in os.listdir(self.folder) if f.endswith('.jpeg') or f.endswith('.jpg')]
        self.image_position_in_folder = 0

        if len(self.files) == 0:
            sys.exit()

    def get_next_image(self, direction=1):
        # check if the folder is set
        if self.folder is None or self.files is None:
            return

        # update the image position in folder
        self.image_position_in_folder += direction

        # loop the files into the folder
        if self.image_position_in_folder >= len(self.files):
            self.image_position_in_folder = 0
        elif self.image_position_in_folder <= -1:
            self.image_position_in_folder = len(self.files) - 1

        # update the image path
        self.file_name = self.files[self.image_position_in_folder]
        self.image_path = os.path.join(self.folder, self.file_name)

    def prev_image(self):
        self.next_image(direction=-1)

    def next_image(self, direction=1):
        self.get_next_image(direction)
        self.read_image()

    def read_image(self):
        if self.image_path is None:
            return

        self.selection_start = None
        self.modified = False

        # read image from file
        self.image = cv2.imread(self.image_path)

        self.place_image()

    def place_image(self):
        if self.image is None:
            return

        # create a QImage from the cv2 image
        height, width, channel = self.image.shape
        bytes_per_line = 3 * width
        q_img = QImage(self.image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        # place the image in the center of the view
        pixmap = QPixmap(q_img)
        pixmap_x = int((self.view_size.width() - pixmap.width()) / 2)
        pixmap_y = int((self.view_size.height() - pixmap.height()) / 2)
        self.image_pos = QPointF(pixmap_x, pixmap_y)
        item = QGraphicsPixmapItem(pixmap)
        item.setPos(pixmap_x, pixmap_y)

        # update the scene
        self.scene.clear()
        self.scene.addItem(item)
        self.set_selection()

        self.update_title()

    def blur_selection(self, rect):
        if not rect.isValid() or self.image is None or rect.width() == 0 or rect.height() == 0:
            return

        # Get the coordinates of the selection
        x1, y1, x2, y2 = int(rect.x()), int(rect.y()), int(rect.x() + rect.width()), int(rect.y() + rect.height())

        # Get the selected area from the original image
        selected_area = self.image[y1:y2, x1:x2]

        # Apply the blur effect
        # cv2.GaussianBlur(selected_area, (25, 25), 0)
        blurred_area = cv2.GaussianBlur(selected_area, (0, 0), 8)

        # Replace the selected area with the blurred area
        self.image[y1:y2, x1:x2] = blurred_area

        # Update the image
        self.modified = True
        self.place_image()

    def save(self):
        # Save the image
        if self.modified:
            cv2.imwrite(self.image_path, self.image)
            self.modified = False
            self.update_title()

    def save_and_next(self):
        self.save()
        self.next_image()

    def mousePressEvent(self, event):
        self.selection_rect.show()
        self.selection_start = event.pos()

    def mouseMoveEvent(self, event):
        if self.selection_start is not None:
            selection_rect = self.get_selection_rect(event.pos())
            self.selection_rect.setRect(selection_rect.x() + self.image_pos.x(),
                                        selection_rect.y() + self.image_pos.y(),
                                        selection_rect.width(), selection_rect.height())

    def mouseReleaseEvent(self, event):
        if self.selection_start is not None:
            selection_rect = self.get_selection_rect(event.pos())
            self.blur_selection(selection_rect)
            self.selection_start = None

    def get_selection_rect(self, current_pos):
        x1, y1 = self.bound(self.selection_start.x() - self.image_pos.x(),
                            self.selection_start.y() - self.image_pos.y())
        x2, y2 = self.bound(current_pos.x() - self.image_pos.x(), current_pos.y() - self.image_pos.y())

        # Swap coordinates if needed to ensure x1 <= x2 and y1 <= y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        return QRectF(QPointF(x1, y1), QPointF(x2, y2))

    def bound(self, x, y):
        height, width, channel = self.image.shape

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > width:
            x = width
        if y > height:
            y = height

        return x, y


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
