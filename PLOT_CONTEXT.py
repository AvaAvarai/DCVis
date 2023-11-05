import typing

from OpenGL.GL import *
import OpenGL.arrays.vbo as glvbo
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import numpy as np
from COLORS import getColors

import GCA
import CLIPPING


def draw_unhighlighted_nd_points(dataset, marker_vao, class_vao):
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glLineWidth(1)

    # loop through classes in class order
    for i in dataset.class_order[::-1]:
        color = dataset.class_colors[i]
        
        # draw polylines
        if dataset.active_classes[i]:
            # positions of the class
            glBindVertexArray(class_vao[i])
            
            # draw polyline
            for j in range(dataset.vertex_count):
                if dataset.active_attributes[j]:
                    glColor4ub(color[0], color[1], color[2], dataset.attribute_alpha)
                else:
                    glColor4ub(color[0], color[1], color[2], 255)

                # draw line for n-1 to n with attribute alpha
                for l in range(0, len(dataset.positions[i]), dataset.vertex_count):
                    k = 0
                    for m in range(1, dataset.vertex_count):
                        if dataset.active_attributes[m-1]:
                            glColor4ub(color[0], color[1], color[2], dataset.attribute_alpha)
                        else:
                            glColor4ub(color[0], color[1], color[2], 255)
                            
                        glBegin(GL_LINES)
                        glVertex2f(dataset.positions[i][l+m][0], dataset.positions[i][l+m][1])
                        glVertex2f(dataset.positions[i][l+m-1][0], dataset.positions[i][l+m-1][1])
                        glEnd()
                        k += 1
                
            glBindVertexArray(0)

        # draw markers
        if dataset.active_markers[i]:
            # positions of the markers
            for j in range(dataset.vertex_count):
                if j == dataset.vertex_count - 1:
                    glPointSize(7)
                    color = [min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255)]

                glBindVertexArray(marker_vao[i * dataset.vertex_count + j])

                if dataset.active_attributes[j]:
                    glColor4ub(color[0], color[1], color[2], dataset.attribute_alpha)
                else:
                    glColor4ub(color[0], color[1], color[2], 255)
                # drawing
                glDrawArrays(GL_POINTS, 0, int(len(dataset.positions[i]) / dataset.vertex_count))
                # unbind
                glBindVertexArray(0)
                glPointSize(5)
    glDisable(GL_BLEND)


def draw_highlighted_nd_points(dataset, marker_vao, class_vao):    
    # highlight color and width
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glColor3ub(255, 255, 0)
    glLineWidth(4)
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
                if dataset.clipped_samples[size_index + datapoint_cnt]:
                    glDrawArrays(GL_LINE_STRIP, j, dataset.vertex_count)
                datapoint_cnt += 1
            glBindVertexArray(0)

    glLineWidth(1)


# draw axes
def draw_axes(dataset, axis_vao, color):
    # positions of the class
    glBindVertexArray(axis_vao)
    # colors
    glColor4f(*color)
    
    if dataset.plot_type != 'SCC': # draw a line axis
        for j in range(0, dataset.axis_count * 2, 2):
            glDrawArrays(GL_LINES, j, dataset.vertex_count)
            
    else: # draw a circle axis
        circumference = dataset.attribute_count
        diameter = circumference / np.pi
        radius = diameter / 2
        
        lineSeg = 1000
        # draw axis
        glBegin(GL_LINE_LOOP)
        for i in range(lineSeg + 1):
            glVertex2f(radius * np.cos(i * 2 * np.pi / lineSeg), radius * np.sin(i * 2 * np.pi / lineSeg))
        glEnd()

        # calculate angle between each tick mark
        angle_between_ticks = 2 * np.pi / dataset.attribute_count

        # draw tick marks
        tick_length = 0.1 * radius
        for i in range(dataset.attribute_count):
            # Adjusting the angle to start from the 12 o'clock position
            angle_for_tick = i * angle_between_ticks - np.pi/2
            # compute start and end position of the tick mark
            inner_x = (radius - tick_length/2) * np.cos(angle_for_tick)
            inner_y = (radius - tick_length/2) * np.sin(angle_for_tick)
            outer_x = (radius + tick_length/2) * np.cos(angle_for_tick)
            outer_y = (radius + tick_length/2) * np.sin(angle_for_tick)
            
            # draw tick mark
            glBegin(GL_LINES)
            glVertex2f(inner_x, inner_y)
            glVertex2f(outer_x, outer_y)
            glEnd()

        glBindVertexArray(0)
        
    # unbind
    glBindVertexArray(0)


# draw box for box clipping
def draw_box(all_rect):
    if all_rect:
        for r in all_rect:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(1.0, 0.0, 0.0, 0.5)
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
    def __init__(self, dataset, parent=None):
        super(MakePlot, self).__init__(parent)

        self.data = dataset
        self.vertex_info = GCA.GCA(self.data)
        self.line_vao = []
        self.marker_vao = []
        self.axis_vao = None

        # for clipping
        self.all_rect = []  # holds all clip boxes
        self.rect = []  # working clip box

        # for zooming
        self.m_left = -1.125
        self.m_right = 1.125
        self.m_bottom = -1.125
        self.m_top = 1.125
        
        if self.data.plot_type == 'SCC':
            self.m_left *= self.data.attribute_count * 0.25
            self.m_right *= self.data.attribute_count * 0.25
            self.m_bottom *= self.data.attribute_count * 0.25
            self.m_top *= self.data.attribute_count * 0.25

        self.zoomed_width = 1.125
        self.zoomed_height = 1.125
        self.is_zooming = False
        self.is_panning = False
        
        # for dragging
        self.has_dragged = False  # bool to check for starting location
        self.prev_horiz = None  # need previous x location
        self.prev_vert = None  # need previous y location

        self.background_color = [0.9375, 0.9375, 0.9375, 1]  # Default gray in RGBA
        self.axes_color = [0, 0, 0, 1]  # Default black in RGBA
        
        self.data = dataset
        
        self.color_instance = getColors(self.data.class_count, self.background_color, self.axes_color)
        self.data.class_colors = self.color_instance.colors_array

    def redraw_plot(self, background_color=None, axes_color=None):
        if background_color is not None:
            self.background_color = background_color
        if axes_color is not None:
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
            # grab the class positions
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
            # unbind
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
        
        # unbind
        glBindVertexArray(0)

    def resizeGL(self, width, height):
        self.width, self.height = width, height
        glViewport(0, 0, width, height)

    def paintGL(self):
        glClearColor(*self.background_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        set_view_frustrum(self.m_left, self.m_right, self.m_bottom, self.m_top)

        # draw points
        draw_unhighlighted_nd_points(self.data, self.marker_vao, self.line_vao)
        draw_highlighted_nd_points(self.data, self.marker_vao, self.line_vao)
        
        if self.data.axis_on:
            draw_axes(self.data, self.axis_vao, self.axes_color)

        draw_box(self.all_rect) # draw clip box

    # === Mouse Events ===
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            x = self.m_left + (event.position().x() * (self.m_right - self.m_left)) / self.width
            y = self.m_bottom + ((self.height - event.position().y()) * (self.m_top - self.m_bottom)) / self.height
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
