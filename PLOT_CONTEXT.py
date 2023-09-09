from OpenGL.GL import *
import OpenGL.arrays.vbo as glvbo
from PyQt6.QtWidgets import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import numpy as np
import random

import GCA
import CLIPPING

poly_color = [[255, 0, 0],  # red
              [0, 255, 0],  # green
              [0, 0, 255],  # blue
              [255, 108, 221],  # purple
              [255, 0, 0],
              [128, 0, 128],
              [0, 255, 255],
              [233, 20, 20],
              [255, 233, 0],
              [233, 233, 233]]

def drawPolyLines(dataset, class_vao):
    # loop through classes
    for i in range(dataset.class_count):
        # check if active
        if dataset.active_classes[i]:
            # positions of the class
            glBindVertexArray(class_vao[dataset.class_order[i]])
            # colors of the class
            color = dataset.class_colors[i]
            glColor3ub(color[0], color[1], color[2])
            # draw polyline
            for j in range(0, len(dataset.positions[dataset.class_order[i]]), dataset.vertex_count):
                glDrawArrays(GL_LINE_STRIP, j, dataset.vertex_count)
                
            glBindVertexArray(0)

def drawHighlightedPolyLines(dataset, class_vao):
    # highlight color and width
    glColor3ub(255, 255, 0)
    glLineWidth(2)
    # Draw highlighted polylines
    for i in range(dataset.class_count):
        datapoint_cnt = 0
        # check if active
        if dataset.active_classes[i]:
            # positions of the class
            glBindVertexArray(class_vao[dataset.class_order[i]])
            size_index = 0
            for j in range(dataset.class_count):
                if j < dataset.class_order[i]:
                    size_index += dataset.count_per_class[dataset.class_order[j]]
            
            # draw polyline
            size = len(dataset.positions[dataset.class_order[i]])
            for j in range(0, size, dataset.vertex_count):
                if dataset.clipped_samples[size_index + datapoint_cnt]:
                    glDrawArrays(GL_LINE_STRIP, j, dataset.vertex_count)
                datapoint_cnt += 1
            glBindVertexArray(0)
    glLineWidth(1)

# draw markers
def drawMarkers(dataset, marker_vao):
    # loop through classes

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    for i in range(dataset.class_count):
        # check if active
        if dataset.active_markers[dataset.class_order[i]]:
            # positions of the markers
            for j in range(dataset.vertex_count):
                if j == dataset.vertex_count - 1:
                    glPointSize(7)

                glBindVertexArray(marker_vao[dataset.class_order[i] * dataset.vertex_count + j])
                # colors of the class
                color = dataset.class_colors[i]
                if not dataset.active_attributes[j]:
                    glColor4ub(color[0], color[1], color[2], dataset.attribute_alpha)
                else:
                    glColor4ub(color[0], color[1], color[2], 255)
                # drawing
                glDrawArrays(GL_POINTS, 0, int(len(dataset.positions[dataset.class_order[i]]) / dataset.vertex_count))
                # unbind
                glBindVertexArray(0)
                glPointSize(5)
    glDisable(GL_BLEND)

# draw axes
def drawAxes(dataset, axis_vao, color):
    # positions of the class
    glBindVertexArray(axis_vao)
    # colors
    glColor4f(*color)
    for j in range(0, dataset.axis_count * 2, 2):
        glDrawArrays(GL_LINES, j, dataset.vertex_count)
    # unbind
    glBindVertexArray(0)

# draw box for box clipping
def drawBox(all_rect):
    if all_rect:
        for r in all_rect:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(1.0, 0.0, 0.0, 0.3)
            glBegin(GL_QUADS)
            glVertex2f(r[0], r[1])
            glVertex2f(r[0], r[3])
            glVertex2f(r[2], r[3])
            glVertex2f(r[2], r[1])
            glEnd()
            glDisable(GL_BLEND)

def setViewFrustum(m_left, m_right, m_bottom, m_top):
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

        # for position vertex information
        self.data = dataset
        self.vertex_info = GCA.GCA_Option(self.data)
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

        self.zoom_level = 1
        self.zoomed_width = 1.125
        self.zoomed_height = 1.125
        self.is_zooming = False
        
        # for dragging
        self.has_dragged = False  # bool to check for starting location
        self.prev_horiz = None  # need previous x location
        self.prev_vert = None  # need previous y location

        self.background_color = [0.7, 0.7, 0.7, 1.0]  # Default grey in RGBA
        self.axes_color = [0, 0, 0, 1]  # Default black in RGBA

    def redraw_plot(self, background_color=None, axes_color=None):
        if background_color is not None:
            self.background_color = background_color
        if axes_color is not None:
            self.axes_color = axes_color
        self.update()

    def initializeGL(self):
        glClearColor(*self.background_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setViewFrustum(self.m_left, self.m_right, self.m_bottom, self.m_top)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glPointSize(5)
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

    def resizeGL(self, w, h):
        self.width, self.height = w, h
        glViewport(0, 0, w, h)

    def paintGL(self):
        glClearColor(*self.background_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setViewFrustum(self.m_left, self.m_right, self.m_bottom, self.m_top)
        drawPolyLines(self.data, self.line_vao)
        drawMarkers(self.data, self.marker_vao)
        
        drawHighlightedPolyLines(self.data, self.line_vao)
        if self.data.axis_on:
            drawAxes(self.data, self.axis_vao, self.axes_color)

        drawBox(self.all_rect)

    def mousePressEvent(self, event):      
        if event.button() == Qt.MouseButton.RightButton:
            x = self.m_left + (event.position().x() * (self.m_right - self.m_left)) / self.width
            y = self.m_bottom + ((self.height - event.position().y()) * (self.m_top - self.m_bottom)) / self.height
            # print(str(x) + " " + str(y))
            self.rect.append(x)
            self.rect.append(y)
            if len(self.rect) == 4:
                CLIPPING.Clipping(self.rect, self.data)
                self.all_rect.append(self.rect)
                self.rect = []
                self.update()

            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.has_dragged = False  # Reset the flag only when the middle mouse button is released
            self.is_zooming = False  # Reset zooming flag

    def wheelEvent(self, event):
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
        # Define panning bounds and thresholds
        drag_threshold = 0.01  # Small threshold to consider an event as a drag

        # exit if not middle mouse
        if event.buttons() != Qt.MouseButton.MiddleButton:
            return

        if self.is_zooming:
            return

        mouseX = event.position().x() / self.width
        mouseY = (1 - event.position().y()) / self.height

        if not self.has_dragged:
            self.prev_horiz = mouseX
            self.prev_vert = mouseY
            self.has_dragged = True
        else:
            dx = mouseX - self.prev_horiz
            dy = mouseY - self.prev_vert

            # Only consider the event as a drag if it's beyond a small threshold
            if abs(dx) > drag_threshold or abs(dy) > drag_threshold:
                self.m_left -= dx * (self.m_right - self.m_left)
                self.m_right -= dx * (self.m_right - self.m_left)
                self.m_bottom -= dy * (self.m_top - self.m_bottom)
                self.m_top -= dy * (self.m_top - self.m_bottom)

                self.prev_horiz = mouseX  # Update for the next iteration
                self.prev_vert = mouseY  # Update for the next iteration

            self.update()

        event.accept()
