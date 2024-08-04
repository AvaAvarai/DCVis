from PyQt6.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QCursor, QTransform
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QApplication, QGraphicsEllipseItem, QGraphicsLineItem

from typing import List
import numpy as np
import GCA, CLIPPING
from COLORS import getColors, shift_hue


class BezierCurve(QGraphicsItem):
    def __init__(self, start, control1, control2, end, color):
        super().__init__()
        self.start = QPointF(*start)
        self.control1 = QPointF(*control1)
        self.control2 = QPointF(*control2)
        self.end = QPointF(*end)
        self.color = QColor(*[int(c * 255) for c in color])

    def boundingRect(self):
        return QRectF(self.start, self.end).normalized().adjusted(-10, -10, 10, 10)

    def paint(self, painter, option, widget):
        path = QPainterPath()
        path.moveTo(self.start)
        path.cubicTo(self.control1, self.control2, self.end)
        pen = QPen(self.color, 1)
        painter.setPen(pen)
        painter.drawPath(path)


class AxisLine(QGraphicsLineItem):
    def __init__(self, start, end, color):
        super().__init__(QLineF(QPointF(*start), QPointF(*end)))
        self.setPen(QPen(QColor(*color), 1))


class DataPoint(QGraphicsEllipseItem):
    def __init__(self, position, size, color):
        super().__init__(QRectF(position[0] - size / 2, position[1] - size / 2, size, size))
        self.setBrush(QColor(*color))
        self.setPen(QPen(QColor(*color), 1))


def calculate_radius(data):
    circumference = data.attribute_count
    radius = circumference / ((2 + data.attribute_count / 100) * np.pi)
    return radius


def calculate_cubic_bezier_control_points(start, end, radius, attribute_count, is_inner, class_index):
    midX, midY = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
    if class_index < 2:
        radius_factor = 1
    else:
        radius_factor = class_index

    if is_inner:
        factor = 0.01
        distance = np.sqrt(midX ** 2 + midY ** 2)
        if distance == 0:
            control1 = (midX, midY)
            control2 = (midX, midY)
        else:
            scale = factor * radius * radius_factor / distance
            control1 = (midX * scale, midY * scale)
            control2 = (midX * scale, midY * scale)
        return control1, control2

    factor = 2
    new_radius = radius * factor * 1.2 * radius_factor
    angle = np.arctan2(midY, midX)
    angle_adjustment = np.pi / attribute_count / 3
    control1 = (new_radius * np.cos(angle + angle_adjustment), new_radius * np.sin(angle + angle_adjustment))
    control2 = (new_radius * np.cos(angle - angle_adjustment), new_radius * np.sin(angle - angle_adjustment))
    return control1, control2


class Plot(QGraphicsView):
    def __init__(self, dataset, replot_overlaps_box, overlaps_textbox, replot_overlaps_btn, parent=None, reset_zoom=None):
        super().__init__(parent)
        self.data = dataset
        self.vertex_info = GCA.GCA(self.data)
        self.line_vao = []
        self.marker_vao = []
        self.axis_vao = None

        self.sectors = []
        self.data.active_sectors = [True for _ in range(self.data.class_count)]
        self.replot_overlaps_btn = replot_overlaps_btn
        self.replot_overlaps_btn.setEnabled(False)

        self.all_rect = []
        self.rect = []
        self.attribute_inversions: List[bool] = []

        self.overlaps_textbox = overlaps_textbox
        self.overlaps_textbox.setText('Requires Circular Coordinates\n\nSelect SCC or DCC to view overlaps.')

        if not reset_zoom:
            self.reset_zoom()
        else:
            self.m_left, self.m_right, self.m_bottom, self.m_top = reset_zoom

        self.zoomed_width = 1.125
        self.zoomed_height = 1.125
        self.is_zooming = False
        self.is_panning = False

        self.has_dragged = False
        self.prev_horiz = None
        self.prev_vert = None

        self.background_color = QColor(239, 239, 239)
        self.axes_color = QColor(0, 0, 0)

        self.highlight_overlaps = self.data.plot_type in ['SCC', 'DCC']
        replot_overlaps_box.setChecked(self.highlight_overlaps)
        if self.highlight_overlaps:
            replot_overlaps_box.setEnabled(True)
        else:
            replot_overlaps_box.setEnabled(False)
            self.highlight_overlaps = True

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.update_transform()

    def reset_zoom(self):
        self.m_left = -1.125
        self.m_right = 1.125
        self.m_bottom = -1.125
        self.m_top = 1.125
        self.update_transform()

    def get_zoom(self):
        return self.m_left, self.m_right, self.m_bottom, self.m_top

    def set_zoom(self, m_left, m_right, m_bottom, m_top):
        self.m_left, self.m_right, self.m_bottom, self.m_top = m_left, m_right, m_bottom, m_top
        self.update_transform()

    def resize(self):
        if self.data.plot_type == 'PC':
            self.m_left = -0.05
            self.m_right = 1.05
            self.m_bottom = -0.05
            self.m_top = 1.05
        elif self.data.plot_type in ['SCC', 'DCC']:
            class_mult = self.data.class_count - 1 if self.data.class_count > 1 else 1
            self.m_left = -self.data.attribute_count * 0.35 * class_mult
            self.m_right = self.data.attribute_count * 0.35 * class_mult
            self.m_bottom = -self.data.attribute_count * 0.35 * class_mult
            self.m_top = self.data.attribute_count * 0.35 * class_mult
        self.update_transform()

    def update_transform(self):
        transform = QTransform()
        width = self.m_right - self.m_left
        height = self.m_top - self.m_bottom
        transform.scale(self.width() / width, -self.height() / height)
        transform.translate(-self.m_left, -self.m_top)
        self.setTransform(transform)

    def redraw_plot(self, background_color=None, axes_color=None):
        if background_color:
            self.background_color = QColor(*[int(c * 255) for c in background_color])
        if axes_color:
            self.axes_color = QColor(*[int(c * 255) for c in axes_color])
        self.update_scene()

    def update_scene(self):
        self.scene.clear()
        self.setSceneRect(self.m_left, self.m_bottom, self.m_right - self.m_left, self.m_top - self.m_bottom)
        if self.data.plot_type not in ['SCC', 'DCC']:
            self.draw_axes()
            self.draw_nd_points()
        else:
            self.draw_axes()
            self.draw_curves()
        self.draw_boxes()

    def draw_axes(self):
        if self.data.plot_type not in ['SCC', 'DCC']:
            for j in range(0, self.data.axis_count * 2, 2):
                start = self.data.axis_positions[j]
                end = self.data.axis_positions[j + 1]
                self.scene.addItem(AxisLine(start, end, [0, 0, 0]))
        else:
            lineSeg = 100
            angle_between_ticks = 2 * np.pi / self.data.attribute_count
            for class_index in range(self.data.class_count):
                base_radius = self.data.attribute_count / (2 * np.pi)
                radius_factor = 1 if class_index < 2 else 2.1 * (class_index - 1)
                radius = base_radius * radius_factor
                for i in range(lineSeg + 1):
                    start = (radius * np.cos(i * 2 * np.pi / lineSeg), radius * np.sin(i * 2 * np.pi / lineSeg))
                    if i > 0:
                        self.scene.addItem(AxisLine(prev, start, [0, 0, 0]))
                    prev = start
                if self.data.plot_type == 'SCC':
                    tick_length = radius * 2
                    for i in range(self.data.attribute_count):
                        angle_for_tick = (-i * angle_between_ticks + np.pi / 2) % (2 * np.pi)
                        inner_x = (radius - tick_length / 2) * np.cos(angle_for_tick)
                        inner_y = (radius - tick_length / 2) * np.sin(angle_for_tick)
                        outer_x = (radius + tick_length / 2) * np.cos(angle_for_tick)
                        outer_y = (radius + tick_length / 2) * np.sin(angle_for_tick)
                        self.scene.addItem(AxisLine((inner_x, inner_y), (outer_x, outer_y), [0, 0, 0]))

    def draw_nd_points(self):
        hue_shift_amount = 0.02
        for class_index in self.data.class_order[::-1]:
            if self.data.active_classes[class_index]:
                color = self.data.class_colors[class_index]
                for l in range(0, len(self.data.positions[class_index]), self.data.vertex_count):
                    for m in range(1, self.data.vertex_count):
                        color = shift_hue(color, hue_shift_amount)
                        hue_shift_amount += 0.02
                        start, end = self.data.positions[class_index][l + m - 1], self.data.positions[class_index][l + m]
                        self.scene.addItem(AxisLine(start, end, color))

    def draw_curves(self):
        radius = calculate_radius(self.data)
        for class_index in range(self.data.class_count):
            is_inner = class_index == self.data.class_order[0]
            if self.data.active_classes[class_index]:
                for l in range(0, len(self.data.positions[class_index]), self.data.vertex_count):
                    for m in range(1, self.data.vertex_count):
                        start, end = self.data.positions[class_index][l + m - 1], self.data.positions[class_index][l + m]
                        control1, control2 = calculate_cubic_bezier_control_points(start, end, radius, self.data.attribute_count, is_inner, class_index)
                        self.scene.addItem(BezierCurve(start, control1, control2, end, self.data.class_colors[class_index]))

    def draw_boxes(self):
        color = QColor(255, 0, 0, 128)
        for rect in self.all_rect:
            rect_item = self.scene.addRect(QRectF(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]), pen=QPen(color), brush=color)
            rect_item.setZValue(-1)

    def mousePressEvent(self, event):
        x = self.m_left + (event.position().x() * (self.m_right - self.m_left)) / self.width()
        y = self.m_bottom + ((self.height() - event.position().y()) * (self.m_top - self.m_bottom)) / self.height()
        if event.button() == Qt.MouseButton.LeftButton:
            precision_exp = -4
            tuning = 0.005
            precision = 10 ** precision_exp
            self.data.clipped_count = 0
            self.data.clipped_samples = [False for _ in range(self.data.sample_count)]
            while self.data.clipped_count == 0 and precision_exp < -3:
                self.left_rect = [x - precision, y - precision, x + precision, y + precision]
                CLIPPING.Clipping(self.left_rect, self.data)
                precision_exp += tuning
                precision = 10 ** precision_exp
            if self.data.clipped_count > 1:
                positions = self.data.positions[self.data.clipped_samples]
                distances = np.linalg.norm(positions - np.array([x, y]), axis=1)
                min_index = np.argmin(distances)
                closest_sample = np.where(self.data.clipped_samples)[0][min_index]
                self.data.clipped_samples[:] = False
                self.data.clipped_samples[closest_sample] = True
            self.update_scene()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.rect.append(x)
            self.rect.append(y)
            if len(self.rect) == 2:
                QApplication.instance().setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
            if len(self.rect) == 4:
                QApplication.instance().restoreOverrideCursor()
                CLIPPING.Clipping(self.rect, self.data)
                self.all_rect.append(self.rect)
                self.rect = []
                self.update_scene()
            event.accept()
        elif event.button() == Qt.MouseButton.MiddleButton:
            seen = False
            for rect in self.all_rect:
                if x > rect[0] and x < rect[2] and y > rect[1] and y < rect[3]:
                    self.rect = rect
                    self.all_rect.remove(rect)
                    seen = True
                    width = (rect[2] - rect[0]) / 2
                    break
            eps = 0.01
            if seen:
                eps += width
            self.rect = []
            self.rect.append(x - eps)
            self.rect.append(y - eps)
            self.rect.append(x + eps)
            self.rect.append(y + eps)
            CLIPPING.Clipping(self.rect, self.data)
            self.all_rect.append(self.rect)
            self.update_scene()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.has_dragged = False
            self.is_zooming = False
            self.is_panning = False

    def wheelEvent(self, event):
        if self.is_panning:
            return
        self.is_zooming = True
        zoom_factor = 1.2
        zoom_dir = 1
        if event.angleDelta().y() < 0:
            zoom_dir = zoom_factor
        elif event.angleDelta().y() > 0:
            zoom_dir = 1 / zoom_factor
        mouseX = event.position().x() / self.width()
        mouseY = (self.height() - event.position().y()) / self.height()
        new_zoomed_width = (self.m_right - self.m_left) * zoom_dir
        new_zoomed_height = (self.m_top - self.m_bottom) * zoom_dir
        mouseX_in_world = self.m_left + mouseX * (self.m_right - self.m_left)
        mouseY_in_world = self.m_bottom + mouseY * (self.m_top - self.m_bottom)
        self.m_left = mouseX_in_world - mouseX * new_zoomed_width
        self.m_right = mouseX_in_world + (1 - mouseX) * new_zoomed_width
        self.m_bottom = mouseY_in_world - mouseY * new_zoomed_height
        self.m_top = mouseY_in_world + (1 - mouseY) * new_zoomed_height
        self.prev_horiz = mouseX
        self.prev_vert = mouseY
        self.is_zooming = False
        self.update_transform()
        self.update_scene()
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.MouseButton.MiddleButton:
            return
        if self.is_zooming:
            return
        self.is_panning = True
        mouseX = event.position().x() / self.width()
        mouseY = (1 - event.position().y()) / self.height()
        if not self.has_dragged:
            self.prev_horiz = mouseX
            self.prev_vert = mouseY
            self.has_dragged = True
        else:
            dx = mouseX - self.prev_horiz
            dy = mouseY - self.prev_vert
            self.m_left -= dx * (self.m_right - self.m_left)
            self.m_right -= dx * (self.m_right - self.m_left)
            self.m_bottom -= dy * (self.m_top - self.m_bottom)
            self.m_top -= dy * (self.m_top - self.m_bottom)
            self.prev_horiz = mouseX
            self.prev_vert = mouseY
            self.update_transform()
            self.update_scene()
        self.is_panning = False
        event.accept()

    def replot_overlaps(self):
        filtered_df = self.data.dataframe.iloc[self.data.overlap_indices]
        self.data.load_frame(filtered_df)
        self.update_scene()
