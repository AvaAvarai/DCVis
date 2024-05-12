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
import GCA, CLIPPING, COLORS


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

def adjust_point_towards_center(point, multiplier=1.0):
    # Calculate direction vector from point towards the center (0, 0)
    direction = [-point[0], -point[1]]
    # Define the scale factor
    scale = 0.0025 * multiplier  # Adjust this base scale factor as needed
    # Normalize the direction vector
    norm = (direction[0]**2 + direction[1]**2)**0.5
    if norm == 0:
        return point  # Return original if normalization fails
    direction_normalized = [direction[0]/norm, direction[1]/norm]
    # Adjust point by moving it towards the center by the scaled amount
    adjusted_point = [point[0] + scale * direction_normalized[0], point[1] + scale * direction_normalized[1]]
    return adjusted_point

def draw_cubic_bezier_curve(start, control1, control2, end, inner, atts):
    # Draw a cubic Bezier curve using OpenGL's immediate mode.
    segments = 11  # The number of line segments to use

    if inner:
        # Adjust both start and end points for inner curves
        start_adjusted = adjust_point_towards_center(start, 1)
        end_adjusted = adjust_point_towards_center(end, 1)
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
    angle = np.arctan2(y, x)  # Ensure y is first in arctan2
    if angle < 0:
        angle += 2 * np.pi  # Normalize to 0 to 2π if needed
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

def calculate_radius(data):
    circumference = data.attribute_count
    # Calculate the radius from the circumference which is the number of attributes
    radius = circumference / ((2 + data.attribute_count / 100) * np.pi)
    return radius

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
            was_inner = False
            is_inner = (class_index == dataset.class_order[0]) and not class_count_one
            if len(dataset.class_order) > 1:
                was_inner = (class_index == dataset.class_order[1])
            for j in range(0, len(dataset.positions[class_index]), dataset.vertex_count):
                if size_index + datapoint_count < len(dataset.vertex_in):
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
                            if was_inner:
                                start = adjust_point_towards_center(start, -dataset.attribute_count)
                                end = adjust_point_towards_center(end, -dataset.attribute_count)

                            control1, control2 = calculate_cubic_bezier_control_points(start, end, radius, dataset.attribute_count, is_inner, class_index)
                            draw_cubic_bezier_curve(start, control1, control2, end, is_inner, dataset.attribute_count)
                datapoint_count += 1
            
            glBindVertexArray(0)
    glLineWidth(1)
    glDisable(GL_BLEND)

def draw_unhighlighted_curves(data, line_vao):
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    
    radius = calculate_radius(data)
    class_count_one = data.class_count == 1
    
    end_hue_shift_amount = 0.1
    hue_shift_amount = 0.02 

    for class_index in range(data.class_count):
        if data.active_classes[class_index]:
            glBindVertexArray(line_vao[class_index])
            datapoint_count = 0
            size_index = 0
            smallest_vector = float('inf')
            largest_vector = 0

            # Initialize the radial bounds for this class if not already present
            if class_index not in data.radial_bounds:
                data.radial_bounds[class_index] = {'smallest': None, 'largest': None}

            for j in range(data.class_count):
                if j < class_index:
                    size_index += data.count_per_class[j]

            was_inner = False
            is_inner = (class_index == data.class_order[0]) and not class_count_one
            if len(data.class_order) > 1:
                was_inner = (class_index == data.class_order[1])
            
            curve_color = data.class_colors[class_index]
            for j in range(0, len(data.positions[class_index]), data.vertex_count):
                for h in range(1, data.vertex_count):
                    index = size_index + datapoint_count
                    if index < len(data.clear_samples) and (h > data.attribute_count or data.clear_samples[index]):
                        continue


                    # Adjust color based on trace mode
                    if data.trace_mode:
                        hue_shift_amount += 0.02
                        glColor4ub(*curve_color.__copy__().shift_hue(hue_shift_amount).to_rgb(), data.attribute_alpha if data.active_attributes[h - 1] else 255)
                    elif h == data.attribute_count - 1:
                        glColor4ub(*data.class_colors[class_index].__copy__().shift_hue(end_hue_shift_amount).to_rgb(), data.attribute_alpha if data.active_attributes[h - 1] else 255)
                    else:
                        hue_shift_amount = 0.
                        glColor4ub(*curve_color.to_rgb(), data.attribute_alpha if data.active_attributes[h - 1] else 255)

                    start, end = data.positions[class_index][j + h - 1], data.positions[class_index][j + h]
                    angle = np.arctan2(end[1], end[0])

                    if angle < smallest_vector:
                        smallest_vector = angle
                    if angle > largest_vector:
                        largest_vector = angle

                    # Adjust start and end for inner classes
                    if is_inner:
                        start = adjust_point_towards_center(start)
                        end = adjust_point_towards_center(end)
                    if was_inner:
                        start = adjust_point_towards_center(start, -data.attribute_count)
                        end = adjust_point_towards_center(end, -data.attribute_count)

                    # Draw the curve
                    control1, control2 = calculate_cubic_bezier_control_points(start, end, radius, data.attribute_count, is_inner, class_index)
                    draw_cubic_bezier_curve(start, control1, control2, end, is_inner, data.attribute_count)

                datapoint_count += 1

            # Update the radial bounds for this class
            data.radial_bounds[class_index]['smallest'] = smallest_vector
            data.radial_bounds[class_index]['largest'] = largest_vector

            glBindVertexArray(0)

    glDisable(GL_BLEND)

def draw_unhighlighted_curves_vertices(data, marker_vao):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glLineWidth(1)
    
    hue_shift = 0.1
    class_count_one = data.class_count == 1
    
    for class_index in range(data.class_count):
        data.overlap_points[class_index] = 0
        if data.active_markers[class_index]:
            for j in range(data.vertex_count):
                glBindVertexArray(marker_vao[class_index * data.vertex_count + j])
                curve_vertex_color = data.class_colors[class_index]
                # last marker hue shift
                if j == data.vertex_count - 1:
                    curve_vertex_color = curve_vertex_color.__copy__().shift_hue(hue_shift)
                glColor4ub(*curve_vertex_color.to_rgb(), data.attribute_alpha if data.active_attributes[j] else 255)
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

                    # if sum(is_point_in_sector(position, (0, 0), sector['start_angle'], sector['end_angle'], sector['radius']) for sector in sectors) > 1:
                    #     # append dataframe index to overlap indices
                    #     index = pos_index // data.vertex_count
                    #     if index not in data.overlap_indices:
                    #         data.overlap_points[class_index] += 1
                    #         data.overlap_indices.append(index)
                    #     glPointSize(10)
                    #     glColor4ub(255, 0, 0, 255)
                        
                    glBegin(GL_POINTS)
                    glVertex2f(*position)
                    glEnd()
                    
                    glPointSize(5)
                    
                    glBegin(GL_POINTS)
                    glVertex2f(*position)
                    glEnd()

                glBindVertexArray(0)

    # overlap = ""
    # for i in range(data.class_count):
    #     overlap += f"Class {i + 1} {data.class_names[i]}: {data.overlap_points[i]}\n"
    #     data.overlap_points[i] = 0
    # count = len(data.overlap_indices)
    # overlap += f"Total Overlaps: {count} / {data.sample_count} samples\n= {round(100 * (count / data.sample_count), 2)}% overlap for {round(100 * (1 - (count / data.sample_count)), 2)}% accuracy.\n"
    # self.overlaps_textbox.setText(overlap)
    # if count > 0:
    #     self.replot_overlaps_btn.setEnabled(True)
    glDisable(GL_BLEND)

def draw_unhighlighted_polylines(dataset, class_vao):
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
            glBindVertexArray(class_vao[i])

            for j in range(dataset.class_count):
                if j < i:
                    size_index += dataset.count_per_class[j] if j < len(dataset.count_per_class) else 0

            # Iterate over positions for polylines
            for l in range(0, len(dataset.positions[i]), dataset.vertex_count):
                # Adjust color based on trace mode
                if dataset.trace_mode:
                    hue_shift_amount += 0.02
        
                if size_index + datapoint_cnt < len(dataset.vertex_in):
                    if dataset.clear_samples[size_index + datapoint_cnt]:
                        datapoint_cnt += 1
                        continue

                sub_alpha = 0
                if any(dataset.clipped_samples):
                    sub_alpha = 0  # TODO: Make this a scrollable option
                
                glBegin(GL_LINES)
                for m in range(1, dataset.vertex_count):
                    if dataset.trace_mode:
                        shifted_color = dataset.class_colors[i].__copy__().shift_hue(hue_shift_amount).to_rgb()
                        glColor4ub(*shifted_color, dataset.attribute_alpha - sub_alpha if dataset.active_attributes[m - 1] else 255 - sub_alpha)
                    else:
                        glColor4ub(*dataset.class_colors[i].to_rgb(), dataset.attribute_alpha - sub_alpha if dataset.active_attributes[m - 1] else 255 - sub_alpha)
                    glVertex2f(dataset.positions[i][l + m - 1][0], dataset.positions[i][l + m - 1][1])
                    glVertex2f(dataset.positions[i][l + m][0], dataset.positions[i][l + m][1])
                glEnd()

                datapoint_cnt += 1
            glBindVertexArray(0)

    glDisable(GL_BLEND)

def draw_unhighlighted_polylines_vertices(dataset, marker_vao):
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glLineWidth(1)

    # Loop through classes in class order
    for i in dataset.class_order[::-1]:
        size_index = 0

        for j in range(dataset.class_count):
            if j < i:
                size_index += dataset.count_per_class[j] if j < len(dataset.count_per_class) else 0
                
        if dataset.active_markers[i]:
            # Draw markers            
            for j in range(dataset.vertex_count):
                glBindVertexArray(marker_vao[i * dataset.vertex_count + j])
                glPointSize(5 if j < dataset.vertex_count - 1 else 7)  # Different size for the last marker

                glColor4ub(*dataset.class_colors[i].to_rgb(), dataset.attribute_alpha if dataset.active_attributes[j] else 255)
                glDrawArrays(GL_POINTS, 0, int(len(dataset.positions[i]) / dataset.vertex_count))

                glBindVertexArray(0)

    glDisable(GL_BLEND)

def draw_highlighted_polylines(dataset, class_vao):
    # highlight color and width
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glColor3ub(255, 255, 0)
    glLineWidth(2)

    # loop through classes in class order
    for i in dataset.class_order[::-1]:
        datapoint_cnt = 0

        size = len(dataset.positions[i])
        if dataset.active_classes[i]:
            # positions of the class
            glBindVertexArray(class_vao[i])
            size_index = 0
            for j in range(dataset.class_count):
                if j < i:
                    size_index += dataset.count_per_class[j] if j < len(dataset.count_per_class) else 0
            # draw polyline
            for j in range(0, size, dataset.vertex_count):
                if size_index + datapoint_cnt < len(dataset.vertex_in):
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


class Plot(QOpenGLWidget):
    def __init__(self, dataset, overlaps_textbox, replot_overlaps_btn, parent=None):
        super(Plot, self).__init__(parent)

        self.data = dataset

        self.vertex_info = GCA.GCA(self.data)
        self.line_vao = []
        self.marker_vao = []
        self.axis_vao = None

        self.sectors = []
        self.data.active_sectors = [True for _ in range(self.data.class_count)]
        self.replot_overlaps_btn = replot_overlaps_btn
        self.replot_overlaps_btn.setEnabled(False)
        
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

        self.background_color = [171 / 255, 171 / 255, 171 / 255, 1]  # Default gray in RGBA
        self.axes_color = [0, 0, 0, 0]  # Default black

        # if class names lower has benign and malignant case insensitive then set colors to green and red
        if isinstance(self.data.class_names[0], str):
            if ('benign' in [x.lower() for x in self.data.class_names] and 'malignant' in [x.lower() for x in self.data.class_names] or 'negative' in [x.lower() for x in self.data.class_names] and 'positive' in [x.lower() for x in self.data.class_names]) and len(self.data.class_names) == 2:
                self.color_instance = COLORS.generate_benign_malignant_colors()
        if not hasattr(self, 'color_instance'):
            self.color_instance = COLORS.generate_colors(self.data.class_count)
        
        self.data.class_colors, self.data.colors_names = self.color_instance

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
            draw_unhighlighted_curves(self.data, self.line_vao)
            draw_highlighted_curves(self.data, self.line_vao)
            draw_unhighlighted_curves_vertices(self.data, self.marker_vao)
            #self.draw_attribute_radials(self.data)
        else:  # Polylines
            draw_unhighlighted_polylines(self.data, self.line_vao)
            draw_highlighted_polylines(self.data, self.line_vao)
            draw_unhighlighted_polylines_vertices(self.data, self.marker_vao)
        
        draw_box(self.all_rect, [1.0, 0.0, 0.0, 0.5])
        
        if self.data.rule_regions:
            for key, box in self.data.rule_regions.items():
                # draw box for each rule region pure class color
                key = box[0]
                highlight = False
                if str(key).endswith('(highlighted)'):
                    key = key[:-13]
                    highlight = True
                box = box[1]
                if highlight:
                    draw_box(box, [1.0, 1.0, 0.0, 1/2])
                elif key:
                    if str(key).endswith('(pure)'):
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
        # Normalize mouse coordinates to [0,1] for both x and y.
        x = self.m_left + (event.position().x() * (self.m_right - self.m_left)) / self.width
        y = self.m_bottom + ((self.height - event.position().y()) * (self.m_top - self.m_bottom)) / self.height

        # EXPANDING COHEN SUTHERLAND SEARCH ROUTINE to left mouse button single sample select
        if event.button() == Qt.MouseButton.LeftButton:
            # TUNING PARAMETERS
            precision_exp = -4
            tuning = 0.005
            precision = 10 ** precision_exp
            
            # Reset clipped samples
            self.data.clipped_count = 0
            self.data.clipped_samples = [False for _ in range(self.data.sample_count)]

            # Expand search outward for a sample
            while self.data.clipped_count == 0 and precision_exp < -3:
                self.left_rect = [x - precision, y - precision, x + precision, y + precision]
                CLIPPING.Clipping(self.left_rect, self.data)

                precision_exp += tuning
                precision = 10 ** precision_exp
            
            # Cull clipped samples to only the nearest if multiple are found, can not handle direct overlap
            if self.data.clipped_count > 1:
                # Compute distances to each clipped sample
                positions = self.data.positions[self.data.clipped_samples]
                distances = np.linalg.norm(positions - np.array([x, y]), axis=1)
                min_index = np.argmin(distances)
                closest_sample = np.where(self.data.clipped_samples)[0][min_index]
                self.data.clipped_samples[:] = False
                self.data.clipped_samples[closest_sample] = True

            self.update()
            event.accept()
            
            return super().mousePressEvent(event)
        # END OF EXPANDING COHEN SUTHERLAND SEARCH ROUTINE

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

    def draw_radial_lines(self, data):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2)  # Adequate line width for visibility
        radius = calculate_radius(data)  # Correct radius for your plot

        for class_index, bounds in data.radial_bounds.items():
            if bounds['smallest'] is not None and bounds['largest'] is not None:
                x_min = radius * np.cos(bounds['smallest'])
                y_min = radius * np.sin(bounds['smallest'])
                x_max = radius * np.cos(bounds['largest'])
                y_max = radius * np.sin(bounds['largest'])

                glColor3ub(*data.class_colors[class_index % len(data.class_colors)])  # Using class colors

                glBegin(GL_LINES)
                glVertex2f(0, 0)
                glVertex2f(5*x_min, 5*y_min)
                glEnd()

                glBegin(GL_LINES)
                glVertex2f(0, 0)
                glVertex2f(5*x_max, 5*y_max)
                glEnd()

        glDisable(GL_BLEND)

    def draw_attribute_radials(self, data):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2)
        center = (0, 0)
        # Draw radial lines
        for i in range(data.attribute_count):
            if i < len(data.max_radial_distances):
                angle = 2 * np.pi * i / data.attribute_count
                x = data.max_radial_distances[i] * np.cos(angle)
                y = data.max_radial_distances[i] * np.sin(angle)
                glColor3ub(*data.class_colors[i % len(data.class_colors)])
                glBegin(GL_LINES)
                glVertex2f(*center)
                glVertex2f(x, y)
                glEnd()

        glDisable(GL_BLEND)

    def replot_overlaps(self):
        
        filtered_df = self.data.dataframe.iloc[self.data.overlap_indices]
        self.data.load_frame(filtered_df)
        
        self.update()
