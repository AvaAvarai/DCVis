from OpenGL.GL import *
import OpenGL.arrays.vbo as glvbo
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from typing import List
import numpy as np
import GCA, CLIPPING
from COLORS import getColors, shift_hue
import CLASS_TABLE

def calculate_cubic_bezier_control_points(start, end, radius, attribute_count, is_inner, class_index):
    # Calculate midpoint between start and end points
    midX, midY = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2

    # Adjust the radius factor based on class index
    if class_index < 2:
        radius_factor = 1
    else:
        radius_factor = class_index

    if is_inner:  # first class always inside axis
        factor = 0.01
        distance = np.sqrt(midX ** 2 + midY ** 2)
        # Calculate scaled control points
        scale = factor * radius * radius_factor / distance

        control1 = (midX * scale, midY * scale)
        control2 = (midX * scale, midY * scale)

        return control1, control2

    factor = 2

    # Calculate the new radius for control points
    new_radius = radius * factor * 1.2 * radius_factor

    # Calculate the angle from the circle's center to the midpoint
    angle = np.arctan2(midY, midX)
    angle_adjustment = np.pi / attribute_count / 3
    
    # Calculate control points using circle formula
    control1 = (new_radius * np.cos(angle + angle_adjustment), new_radius * np.sin(angle + angle_adjustment))
    control2 = (new_radius * np.cos(angle - angle_adjustment), new_radius * np.sin(angle - angle_adjustment))

    return control1, control2

def adjust_point_towards_center(point, atts=1):
    # Calculate direction vector from point towards the center (assumed to be at (0, 0))
    direction = [-point[0], -point[1]]
    scale = 0.0025
    adjust = atts * scale
    # Normalize the direction vector
    norm = (direction[0]**2 + direction[1]**2)**0.5
    direction_normalized = [direction[0]/norm, direction[1]/norm]
    # Adjust point to move 0.025 units towards the center
    return [point[0] + adjust * direction_normalized[0], point[1] + adjust * direction_normalized[1]]

def draw_cubic_bezier_curve(start, control1, control2, end, inner, atts):
    # Draw a cubic Bezier curve using OpenGL's immediate mode.
    segments = 20  # The number of line segments to use

    if inner:
        # Adjust both start and end points for inner curves
        start_adjusted = adjust_point_towards_center(start, atts)
        end_adjusted = adjust_point_towards_center(end, atts)
    else:
        # Use original points if not inner
        start_adjusted = start
        end_adjusted = end

    glBegin(GL_LINE_STRIP)
    for t in np.linspace(0, 1, segments):
        # Cubic Bezier curve equation with adjusted start and end points
        x = (1 - t) ** 3 * start_adjusted[0] + 3 * (1 - t) ** 2 * t * control1[0] + 3 * (1 - t) * t ** 2 * control2[0] + t ** 3 * end_adjusted[0]
        y = (1 - t) ** 3 * start_adjusted[1] + 3 * (1 - t) ** 2 * t * control1[1] + 3 * (1 - t) * t ** 2 * control2[1] + t ** 3 * end_adjusted[1]
        glVertex2f(x, y)
    glEnd()

def calculate_angle(x, y):
    angle = np.arctan2(x, y)
    if angle < 0:
        angle += 2 * np.pi
    return angle

def is_point_in_sector(point, center, start_angle, end_angle, radius):
    # Calculate the angle and distance from the center to the point
    angle = np.arctan2(point[1] - center[1], point[0] - center[0])
    if angle < 0:
        angle += 2 * np.pi
    distance = np.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2)

    # Check if the point's angle and distance place it within the sector
    return distance <= radius and start_angle <= angle <= end_angle

def draw_filled_sector(center, start_angle, end_angle, radius, segments=100):
    """
    Draws a filled sector (part of a circle) between two angles with a specified radius.
    """
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(*center)  # Center point
    for segment in range(segments + 1):
        angle = start_angle + (end_angle - start_angle) * segment / segments
        glVertex2f(center[0] + np.cos(angle) * radius, center[1] + np.sin(angle) * radius)
    glEnd()

def draw_highlighted_curves(dataset, line_vao):
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glColor3ub(255, 255, 0)
    glLineWidth(2)
    radius = calculate_radius(dataset)
    
    class_count_one = dataset.class_count == 1

    for class_index in range(dataset.class_count):
        if dataset.active_classes[class_index]:
            glBindVertexArray(line_vao[class_index])
            datapoint_count = 0
            size_index = 0
            for j in range(dataset.class_count):
                if j < class_index:
                    size_index += dataset.count_per_class[j]

            is_inner = (class_index == dataset.class_order[0]) and not class_count_one
            for j in range(0, len(dataset.positions[class_index]), dataset.vertex_count):
                if dataset.vertex_in[size_index + datapoint_count]:
                    if dataset.clear_samples[size_index + datapoint_count]:
                        datapoint_count += 1
                        continue
                    for h in range(1, dataset.vertex_count):
                        if h > dataset.attribute_count:
                            continue

                        start = dataset.positions[class_index][j + h - 1]
                        end = dataset.positions[class_index][j + h]

                        # Adjust start and end for inner classes
                        if is_inner:
                            start = adjust_point_towards_center(start)
                            end = adjust_point_towards_center(end)

                        control1, control2 = calculate_cubic_bezier_control_points(start, end, radius, dataset.attribute_count, is_inner, class_index)
                        draw_cubic_bezier_curve(start, control1, control2, end, False, dataset.attribute_count)  # False to not pull inwards twice, hacky fix
                datapoint_count += 1
            
            glBindVertexArray(0)
    glLineWidth(1)
    glDisable(GL_BLEND)

def draw_radial_line(start, end):
    glBegin(GL_LINES)
    glVertex2f(*start)
    glVertex2f(*end)
    glEnd()

def calculate_radius(data):
    circumference = data.attribute_count
    # Calculate the radius from the circumference which is the number of attributes
    radius = circumference / ((2 + data.attribute_count / 100) * np.pi)
    return radius

def draw_unhighlighted_nd_points(dataset, class_vao):
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glLineWidth(1)

    hue_shift_amount = 0.02

    # Loop through classes in class order
    for i in dataset.class_order[::-1]:
        datapoint_cnt = 0
        size_index = 0

        # Draw polylines and markers
        if dataset.active_classes[i]:
            # Adjust color based on trace mode
            color = dataset.class_colors[i]
            glBindVertexArray(class_vao[i])

            for j in range(dataset.class_count):
                if j < i:
                    size_index += dataset.count_per_class[j]

            # Iterate over positions for polylines
            for l in range(0, len(dataset.positions[i]), dataset.vertex_count):
                
                if dataset.trace_mode:
                    color = shift_hue(color, hue_shift_amount)
                    hue_shift_amount += 0.02
                
                if dataset.clear_samples[size_index + datapoint_cnt]:
                    datapoint_cnt += 1
                    continue

                sub_alpha = 0
                if any(dataset.clipped_samples):
                    sub_alpha = 100  # TODO: Make this a scrollable option

                glBegin(GL_LINES)
                for m in range(1, dataset.vertex_count):
                    glColor4ub(color[0], color[1], color[2], dataset.attribute_alpha - sub_alpha if dataset.active_attributes[m - 1] else 255 - sub_alpha)
                    glVertex2f(dataset.positions[i][l + m - 1][0], dataset.positions[i][l + m - 1][1])
                    glVertex2f(dataset.positions[i][l + m][0], dataset.positions[i][l + m][1])
                glEnd()

                datapoint_cnt += 1
            glBindVertexArray(0)

    glDisable(GL_BLEND)

def draw_unhighlighted_nd_point_vertices(dataset, marker_vao):
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glLineWidth(1)
    
    # Loop through classes in class order
    for i in dataset.class_order[::-1]:
        size_index = 0

        # Draw polylines and markers
        if dataset.active_classes[i]:
            # Adjust color based on trace mode
            color = dataset.class_colors[i]
            class_color = color

            for j in range(dataset.class_count):
                if j < i:
                    size_index += dataset.count_per_class[j]
                    
            if dataset.active_markers[i]:
                # Draw markers
                for j in range(dataset.vertex_count):
                    glBindVertexArray(marker_vao[i * dataset.vertex_count + j])
                    glPointSize(5 if j < dataset.vertex_count - 1 else 7)  # Different size for the last marker

                    # Apply adjusted color for each marker
                    glColor4ub(class_color[0], class_color[1], class_color[2], dataset.attribute_alpha if dataset.active_attributes[j] else 255)
                    glDrawArrays(GL_POINTS, 0, int(len(dataset.positions[i]) / dataset.vertex_count))

                    glBindVertexArray(0)

    glDisable(GL_BLEND)

def draw_highlighted_nd_points(dataset, class_vao):
    # highlight color and width
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glColor3ub(255, 255, 0)
    glLineWidth(2)

    # loop through classes in class order
    for i in dataset.class_order[::-1]:
        datapoint_cnt = 0
        # check if active
        if dataset.active_classes[i]:
            # positions of the class
            glBindVertexArray(class_vao[i])
            size_index = 0
            for j in range(dataset.class_count):
                if j < i:
                    size_index += dataset.count_per_class[j]

            # draw polyline
            size = len(dataset.positions[i])
            for j in range(0, size, dataset.vertex_count):
                if dataset.clear_samples[size_index + datapoint_cnt]:
                    datapoint_cnt += 1
                    continue
                if dataset.clipped_samples[size_index + datapoint_cnt]:
                    glDrawArrays(GL_LINE_STRIP, j, dataset.vertex_count)
                datapoint_cnt += 1
            glBindVertexArray(0)

    glLineWidth(1)

def draw_axes(dataset, axis_vao, color):
    glBindVertexArray(axis_vao)
    glColor4f(*color)

    if dataset.plot_type not in ['SCC', 'DCC']:  # draw a line axis
        for j in range(0, dataset.axis_count * 2, 2):
            glDrawArrays(GL_LINES, j, dataset.vertex_count)
    else:  # draw a circle axis
        lineSeg = 100
        angle_between_ticks = 2 * np.pi / dataset.attribute_count

        for class_index in range(dataset.class_count):
            base_radius = (dataset.attribute_count / (2 * np.pi))

            if class_index < 2:
                # First two classes share the first axis
                radius_factor = 1
            else:
                scale_factor = 2.1
                radius_factor = scale_factor * (class_index - 1)

            radius = base_radius * radius_factor

            # Draw axis circle
            glBegin(GL_LINE_LOOP)
            for i in range(lineSeg + 1):
                glVertex2f(radius * np.cos(i * 2 * np.pi / lineSeg), radius * np.sin(i * 2 * np.pi / lineSeg))
            glEnd()

            if dataset.plot_type == 'SCC':
                # Draw tick marks
                tick_length = radius * 2  # Adjust the tick length as needed
                for i in range(dataset.attribute_count):
                    angle_for_tick = i * angle_between_ticks - np.pi / 2
                    inner_x = (radius - tick_length / 2) * np.cos(angle_for_tick)
                    inner_y = (radius - tick_length / 2) * np.sin(angle_for_tick)
                    outer_x = (radius + tick_length / 2) * np.cos(angle_for_tick)
                    outer_y = (radius + tick_length / 2) * np.sin(angle_for_tick)

                    glBegin(GL_LINES)
                    glVertex2f(inner_x, inner_y)
                    glVertex2f(outer_x, outer_y)
                    glEnd()

    glBindVertexArray(0)

def draw_box(all_rect, color):
    if all_rect:
        for r in all_rect:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(*color)
            glBegin(GL_QUADS)
            glVertex2f(r[0], r[1])
            glVertex2f(r[0], r[3])
            glVertex2f(r[2], r[3])
            glVertex2f(r[2], r[1])
            glEnd()
            glDisable(GL_BLEND)

def set_view_frustrum(m_left, m_right, m_bottom, m_top):
    if m_left == m_right or m_bottom == m_top:
        return  # Avoid invalid parameters
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(m_left, m_right, m_bottom, m_top, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


class MakePlot(QOpenGLWidget):
    def __init__(self, dataset, overlaps_textbox, parent=None):
        super(MakePlot, self).__init__(parent)

        self.data = dataset

        self.vertex_info = GCA.GCA(self.data)
        self.line_vao = []
        self.marker_vao = []
        self.axis_vao = None

        self.sectors = []
        self.data.active_sectors = [False for _ in range(self.data.class_count)]

        # for clipping
        self.all_rect = []  # holds all clip boxes
        self.rect = []  # working clip box
        self.attribute_inversions: List[bool] = []  # for attribute inversion option

        self.overlaps_textbox = overlaps_textbox
        
        self.overlaps_textbox.setText('Requires Circular Coordinates\n\nSelect SCC or DCC to view overlaps.')
        
        self.reset_zoom()
        self.resize()

        self.zoomed_width = 1.125
        self.zoomed_height = 1.125
        self.is_zooming = False
        self.is_panning = False

        # for dragging
        self.has_dragged = False  # bool to check for starting location
        self.prev_horiz = None  # need previous x location
        self.prev_vert = None  # need previous y location

        self.background_color = [125 / 255, 125 / 255, 125 / 255, 1]  # Default gray
        self.axes_color = [1, 1, 1, 1]  # Default white

        self.color_instance = getColors(self.data.class_count, self.background_color, self.axes_color)
        self.data.class_colors = self.color_instance.colors_array

    def reset_zoom(self):
        self.m_left = -1.125
        self.m_right = 1.125
        self.m_bottom = -1.125
        self.m_top = 1.125

    def resize(self):
        if self.data.plot_type == 'PC':  # fit PC to window
            self.m_left = -0.05
            self.m_right = 1.05
            self.m_bottom = -0.05
            self.m_top = 1.05

        elif self.data.plot_type in ['SCC', 'DCC']:  # fit CC to window
            class_mult = self.data.class_count - 1 if self.data.class_count > 1 else 1
            self.m_left = -self.data.attribute_count * 0.35 * class_mult
            self.m_right = self.data.attribute_count * 0.35 * class_mult
            self.m_bottom = -self.data.attribute_count * 0.35 * class_mult
            self.m_top = self.data.attribute_count * 0.35 * class_mult

    def redraw_plot(self, background_color=None, axes_color=None):
        if background_color:
            self.background_color = background_color
        if axes_color:
            self.axes_color = axes_color
        self.update()

    def initializeGL(self):
        glClearColor(*self.background_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        set_view_frustrum(self.m_left, self.m_right, self.m_bottom, self.m_top)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glPointSize(5)
        QApplication.instance().restoreOverrideCursor()
        # push dataset to GPU memory
        for i in range(self.data.class_count):
            positions = np.asarray(self.data.positions[i], dtype='float32')
            # put them into a VBO
            vbo = glvbo.VBO(positions)
            vbo.bind()
            # reference the VBO
            vao = glGenVertexArrays(1)
            self.line_vao.append(vao)
            # push class to GPU memory
            glBindVertexArray(self.line_vao[i])
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(2, GL_FLOAT, 0, None)
            glBindVertexArray(0)

            for j in range(self.data.vertex_count):
                m_vao = glGenVertexArrays(1)
                self.marker_vao.append(m_vao)
                glBindVertexArray(self.marker_vao[i * self.data.vertex_count + j])
                glEnableClientState(GL_VERTEX_ARRAY)
                offset = ctypes.c_void_p(j * 8)
                glVertexPointer(2, GL_FLOAT, self.data.vertex_count * 8, offset)
                # unbind
                glBindVertexArray(0)

        # push the axis vertices to GPU
        axis = np.asarray(self.data.axis_positions, dtype='float32')
        axis_vbo = glvbo.VBO(axis)
        axis_vbo.bind()
        # reference
        self.axis_vao = glGenVertexArrays(1)
        # push
        glBindVertexArray(self.axis_vao)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, None)

        glBindVertexArray(0)

    def resizeGL(self, width, height):
        self.width, self.height = width, height
        glViewport(0, 0, width, height)

    def paintGL(self):
        glClearColor(*self.background_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        set_view_frustrum(self.m_left, self.m_right, self.m_bottom, self.m_top)

        # draw axes
        if self.data.axis_on:
            draw_axes(self.data, self.axis_vao, self.axes_color)

        # draw n-D points
        if self.data.plot_type in ['SCC', 'DCC']:  # Bezier curves
            self.draw_unhighlighted_curves(self.data, self.line_vao)
            draw_highlighted_curves(self.data, self.line_vao)
            self.draw_unhighlighted_curves_vertices(self.data, self.marker_vao)
        else:  # Polylines
            draw_unhighlighted_nd_points(self.data, self.line_vao)
            draw_highlighted_nd_points(self.data, self.line_vao)
            draw_unhighlighted_nd_point_vertices(self.data, self.marker_vao)
        
        draw_box(self.all_rect, [1.0, 0.0, 0.0, 0.5])
        
        if self.data.rule_regions:
            for key, box in self.data.rule_regions.items():
                # draw box for each rule region pure class color
                if key:
                    if key.endswith('(pure)'):
                        class_name = key[:-7]
                        class_index = self.data.class_names.index(class_name)
                        c = self.data.class_colors[class_index].copy()
                        for i, _c in enumerate(c):
                            c[i] = _c / 255
                        if len(c) == 3:
                            c.append(1/3)
                        draw_box(box, c)
                    else:
                        draw_box(box, [1.0, 1.0, 1.0, 1/3])
                else:
                    draw_box(box, [1.0, 0.0, 0.0, 1/3])

    # === Mouse Events ===
    def mousePressEvent(self, event):
        x = self.m_left + (event.position().x() * (self.m_right - self.m_left)) / self.width
        y = self.m_bottom + ((self.height - event.position().y()) * (self.m_top - self.m_bottom)) / self.height

        # left mouse button single sample select
        if event.button() == Qt.MouseButton.LeftButton:
            precision_exp = -3
            precision = 10 ** precision_exp
            self.data.clipped_count = 0
            self.data.clipped_samples = [False for _ in range(self.data.sample_count)]

            # Expansive search outward for a sample
            while self.data.clipped_count == 0 and precision_exp < -2:
                self.left_rect = [x - precision, y - precision, x + precision, y + precision]
                CLIPPING.Clipping(self.left_rect, self.data)

                precision_exp += 0.05
                precision = 10 ** precision_exp

            # Cull selection to single closest sample
            if self.data.clipped_count > 1:
                closest_sample_index = None
                min_distance = float('inf')

                for index, sample in enumerate(self.data.clipped_samples):
                    if sample:
                        sample_x, sample_y = self.data.get_sample_position(index)
                        distance = ((sample_x - x) ** 2 + (sample_y - y) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            closest_sample_index = index

                # Reset all samples except the closest one
                for index in range(self.data.sample_count):
                    self.data.clipped_samples[index] = 1.0 if index == closest_sample_index else 0.0

                self.data.clipped_count = 1
            
            self.update()
            event.accept()
            
            return super().mousePressEvent(event)
        
        if event.button() == Qt.MouseButton.RightButton:
            self.rect.append(x)
            self.rect.append(y)

            if len(self.rect) == 2:
                QApplication.instance().setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))

            if len(self.rect) == 4:
                QApplication.instance().restoreOverrideCursor()
                CLIPPING.Clipping(self.rect, self.data)
                self.all_rect.append(self.rect)
                self.rect = []
                self.update()

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

        # Normalize mouse coordinates to [0,1] for both x and y.
        mouseX = event.position().x() / self.width
        mouseY = (self.height - event.position().y()) / self.height  # flipped y-axis

        # Compute new zoomed width and height.
        new_zoomed_width = (self.m_right - self.m_left) * zoom_dir
        new_zoomed_height = (self.m_top - self.m_bottom) * zoom_dir

        # Convert mouse coordinates to world coordinates.
        mouseX_in_world = self.m_left + mouseX * (self.m_right - self.m_left)
        mouseY_in_world = self.m_bottom + mouseY * (self.m_top - self.m_bottom)

        # Update the viewport boundaries.
        self.m_left = mouseX_in_world - mouseX * new_zoomed_width
        self.m_right = mouseX_in_world + (1 - mouseX) * new_zoomed_width
        self.m_bottom = mouseY_in_world - mouseY * new_zoomed_height
        self.m_top = mouseY_in_world + (1 - mouseY) * new_zoomed_height

        # Update previous mouse coordinates according to new zoom level
        self.prev_horiz = mouseX
        self.prev_vert = mouseY

        self.is_zooming = False
        self.update()
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.MouseButton.MiddleButton:
            return

        if self.is_zooming:
            return

        self.is_panning = True

        mouseX = event.position().x() / self.width
        mouseY = (1 - event.position().y()) / self.height

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

            # Update for the next iteration
            self.prev_horiz = mouseX
            self.prev_vert = mouseY

            self.update()

        self.is_panning = False

        event.accept()

    def draw_unhighlighted_curves_vertices(self, data, marker_vao):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        hue_shift = 0.08
        
        class_count_one = data.class_count == 1
        
        for class_index in range(data.class_count):
            data.overlap_points[class_index] = 0
            if data.active_markers[class_index]:
                for j in range(data.vertex_count):
                    glBindVertexArray(marker_vao[class_index * data.vertex_count + j])
                    color = data.class_colors[class_index]
                    # last marker hue shift
                    if j == data.vertex_count - 1:
                        color = shift_hue(color, hue_shift)

                    was_inner = False
                    is_inner = class_index == data.class_order[0] and not class_count_one
                    if len(data.class_order) > 1:
                        was_inner = (class_index == data.class_order[1])
                    for pos_index in range(0, len(data.positions[class_index]), data.vertex_count):
                        position = data.positions[class_index][pos_index + j]
                        
                        if is_inner:
                            position = adjust_point_towards_center(position, data.attribute_count)
                        if was_inner:
                            position = adjust_point_towards_center(position, -data.attribute_count)
                            
                        if sum(is_point_in_sector(position, (0, 0), sector['start_angle'], sector['end_angle'], sector['radius']) for sector in self.sectors) > 1:
                            data.overlap_points[class_index] += 1
                            
                            glPointSize(10)
                            glColor4ub(255, 0, 0, 255)  # Red color for highlighting
                            
                        glBegin(GL_POINTS)
                        glVertex2f(*position)
                        glEnd()
                        
                        glPointSize(5)
                        glColor4ub(color[0], color[1], color[2], data.attribute_alpha if data.active_attributes[j] else 255)  # Normal color
                        
                        glBegin(GL_POINTS)
                        glVertex2f(*position)
                        glEnd()

                    glBindVertexArray(0)
        
        # iterate and list class names with each overlap count
        overlap = ""
        for i in range(data.class_count):
            overlap += f"Class {data.class_names[i]}: {data.overlap_points[i]}\n"
        self.overlaps_textbox.setText(overlap)
        glDisable(GL_BLEND)

    def draw_unhighlighted_curves(self, data, line_vao):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        radius = calculate_radius(data)
        self.sectors = []
        hue_shift_amount = 0.02

        class_count_one = data.class_count == 1

        for class_index in range(data.class_count):
            min_angle = np.inf
            max_angle = -np.inf
            closest = furthest = None
            
            is_inner = (class_index == data.class_order[0]) and not class_count_one

            if data.active_classes[class_index]:
                glBindVertexArray(line_vao[class_index])

                datapoint_count = 0
                size_index = 0
                for j in range(data.class_count):
                    if j < class_index:
                        size_index += data.count_per_class[j]

                for j in range(0, len(data.positions[class_index]), data.vertex_count):
                    sub_alpha = 0
                    for h in range(1, data.vertex_count):
                        if h > data.attribute_count or data.clear_samples[size_index + datapoint_count]:
                            continue
                        
                        if data.trace_mode:
                            color = shift_hue(data.class_colors[class_index], hue_shift_amount)
                            hue_shift_amount += 0.02  # Increase hue shift for each attribute or sample
                        elif h == data.attribute_count - 1:
                            color = shift_hue(data.class_colors[class_index], 0.1)  # Apply a hue shift for the last attribute
                        else:
                            color = shift_hue(data.class_colors[class_index], 0)  # No hue shift if not the last attribute or not in trace mode
                            
                        glColor4ub(color[0], color[1], color[2], data.attribute_alpha - sub_alpha if data.active_attributes[h] else 255 - sub_alpha)

                        def rotate_point_around_center(point, center, coef):
                            ox, oy = center
                            px, py = point

                            # Calculate the angle from the center to the point
                            initial_angle = np.arctan2(py - oy, px - ox)

                            # Normalize angle to a positive range [0, 2π]
                            if initial_angle < 0:
                                initial_angle += 2 * np.pi

                            # Define the target angle as the top of the circle (12 o'clock position, which is π/2 radians in this context)
                            target_angle = np.pi / 2

                            # Calculate how much we need to adjust the angle based on the coef
                            # Coef of 1 means no adjustment; coef of 0 aims directly upwards
                            angle_adjustment = (initial_angle - target_angle) * (1 - coef)
                            
                            # Calculate the new angle
                            new_angle = initial_angle - angle_adjustment

                            # Calculate the distance from the center to the point
                            distance = np.sqrt((px - ox) ** 2 + (py - oy) ** 2)

                            # Apply the coefficient to the distance if needed to bring the point closer to the top
                            # This is only applied when the coef is towards 0 to simulate the movement towards the circle's top
                            adjusted_distance = distance * coef if coef < 1 else distance

                            # Calculate the new position using the adjusted angle and distance
                            qx = ox + adjusted_distance * np.cos(new_angle)
                            qy = oy + adjusted_distance * np.sin(new_angle)

                            return qx, qy

                        if data.plot_type == 'DCC':
                            start, end = data.positions[class_index][j + h - 1], data.positions[class_index][j + h]
                            # Rotate end point around the start point by attribute angle
                            end = rotate_point_around_center(end, (0, 0), data.coefs[h - 1])
                        else:
                            start, end = data.positions[class_index][j + h - 1], data.positions[class_index][j + h]

                        
                        control1, control2 = calculate_cubic_bezier_control_points(start, end, radius, data.attribute_count, is_inner, class_index)

                        draw_cubic_bezier_curve(start, control1, control2, end, is_inner, data.attribute_count)

                        angle = calculate_angle(end[0], end[1])
                        
                        if angle < min_angle and h == data.attribute_count - 1:
                            min_angle = angle
                            closest = end
                        if angle > max_angle:
                            max_angle = angle
                            furthest = end
                            
                    datapoint_count += 1

                glBindVertexArray(0)

                mult = 5
                if class_index == data.class_count-1:
                    mult = 2.5
                
                if closest is not None:
                    extended_closest = (closest[0] * mult, closest[1] * mult)
                    if self.data.active_sectors[class_index]:
                        draw_radial_line((0, 0), extended_closest)
                if furthest is not None:
                    extended_endest = (furthest[0] * mult, furthest[1] * mult)
                    if self.data.active_sectors[class_index]:
                        draw_radial_line((0, 0), extended_endest)
                
                if closest is not None and furthest is not None:
                    glColor4ub(color[0], color[1], color[2], 50)
                    closest_angle = np.arctan2(closest[1], closest[0])
                    furthest_angle = np.arctan2(furthest[1], furthest[0])

                    # Adjust angles to be positive
                    closest_angle = closest_angle if closest_angle >= 0 else closest_angle + 2 * np.pi
                    furthest_angle = furthest_angle if furthest_angle >= 0 else furthest_angle + 2 * np.pi

                    # Ensure start_angle < end_angle for drawing the sector correctly
                    if closest_angle > furthest_angle:
                        closest_angle, furthest_angle = furthest_angle, closest_angle
                    
                    # Define the outer radius of the sector. Adjust according to your needs.
                    sector_radius = radius * (data.class_count + 1)

                    # Draw the filled sector
                    if self.data.active_sectors[class_index]:
                        draw_filled_sector((0, 0), closest_angle, furthest_angle, sector_radius, segments=50)

                sector_info = {
                    'start_angle': closest_angle,
                    'end_angle': furthest_angle,
                    'radius': sector_radius
                }
                self.sectors.append(sector_info)

        glDisable(GL_BLEND)
