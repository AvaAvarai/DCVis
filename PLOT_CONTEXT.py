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


# draw polylines
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

            # ============================special =============================================================
            # k = 0
            # for j in range(0, len(dataset.positions[i]), dataset.vertex_count):
            #     k = 0
            #     for m in range(1, dataset.vertex_count):
            #         color = poly_color[k]
            #         glColor3ub(color[0], color[1], color[2])
            #         glBegin(GL_LINES)
            #         glVertex2f(dataset.positions[i][j+m][0], dataset.positions[i][j+m][1])
            #         glVertex2f(dataset.positions[i][j+m-1][0], dataset.positions[i][j+m-1][1])
            #         glEnd()
            #         k += 1

            # unbind
            glBindVertexArray(0)

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
                    glPointSize(10)

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
def drawAxes(dataset, axis_vao):
    # positions of the class
    glBindVertexArray(axis_vao)
    # colors
    glColor3ub(0, 0, 0)
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


# set plot region
def setViewFrustum(m_left, m_right, m_bottom, m_top):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(m_left, m_right, m_bottom, m_top, 0, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


class MakePlot(QOpenGLWidget):
    width = 800
    height = 600

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

        # for dragging
        self.has_dragged = False  # bool to check for starting location
        self.prev_horiz = None  # need previous x location
        self.prev_vert = None  # need previous y location

    def initializeGL(self):
        glClearColor(1, 1, 1, 1)
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
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        setViewFrustum(self.m_left, self.m_right, self.m_bottom, self.m_top)
        drawPolyLines(self.data, self.line_vao)
        drawMarkers(self.data, self.marker_vao)
        if self.data.axis_on:
            drawAxes(self.data, self.axis_vao)

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

    def wheelEvent(self, event):
        zoom_factor = 1.2
        zoom_dir = 1

        if event.angleDelta().y() < 0:
            zoom_dir = zoom_factor
        elif event.angleDelta().y() > 0:
            zoom_dir = 1 / zoom_factor

        mouseX = event.position().x() / self.width
        mouseY = (1 - event.position().y()) / self.height

        mouseX_in_world = self.m_left + mouseX * self.zoomed_width
        mouseY_in_world = self.m_bottom + mouseY * self.zoomed_height

        self.zoomed_width *= zoom_dir
        self.zoomed_height *= zoom_dir

        self.m_left = mouseX_in_world - mouseX * self.zoomed_width
        self.m_right = mouseX_in_world + (1 - mouseX) * self.zoomed_width
        self.m_bottom = mouseY_in_world - mouseY * self.zoomed_height
        self.m_top = mouseY_in_world + (1 - mouseY) * self.zoomed_height

        self.update()
        event.accept()

    def mouseMoveEvent(self, event):
        # exit if not middle mouse
        if event.buttons() != Qt.MouseButton.MiddleButton:
            return

        mouseX = event.position().x() / self.width
        mouseY = (1 - event.position().y()) / self.height


        if not self.has_dragged:
            self.prev_horiz = mouseX
            self.prev_vert = mouseY
            self.has_dragged = True
        else:
            if abs(mouseX - self.prev_horiz) > 0.02 or abs(mouseY - self.prev_vert) > 0.02:
                self.has_dragged = False
            else:
                dx = mouseX - self.prev_horiz
                dy = mouseY - self.prev_vert

                self.m_left -= dx
                self.m_right -= dx
                self.m_bottom -= dy
                self.m_top -= dy

                self.prev_horiz = mouseX
                self.prev_vert = mouseY

                self.update()

        event.accept()
