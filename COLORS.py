# COLORS.py: Has models for RGB and HSV colors, and functions to generate colors for unique color palettes or benign/malignant.

import colorsys

def downRange(color):
    return [int(x * 255) for x in color]

def upRange(color):
    return [int(x * 255) for x in color]


class HSVColor:
    """Model for HSV color"""
    
    def __init__(self, h, s, v):
        self.h = h
        self.s = s
        self.v = v

    def to_rgb(self):
        r, g, b = upRange(colorsys.hsv_to_rgb(self.h, self.s, self.v))
        return r, g, b

    def to_hsv(self):
        return self.h, self.s, self.v

    def shift_hue(self, amount):
        self.h = (self.h + amount) % 1.0


class RGBColor:
    """Model for RGB color"""
    
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def to_rgb(self):
        return self.r, self.g, self.b

    def to_hsv(self):
        return colorsys.rgb_to_hsv(downRange([self.r, self.g, self.b]))

    def shift_hue(self, amount):
        hsv = HSVColor(*self.to_hsv())
        hsv.shift_hue(amount)
        self.r, self.g, self.b = hsv.to_rgb()


def generate_benign_malignant_colors():
    """Generates benign (GREEN) and malignant (RED) colors"""
    
    colors_array: list[RGBColor] = [RGBColor(0, 255, 0), RGBColor(255, 0, 0)]
    colors_names_array = ["Green", "Red"]
    return colors_array, colors_names_array

def generate_colors(num_colors):
    """Generates a list of unique colors based on the number of colors specified in the input parameter"""
    
    colors_array = []
    colors_names_array = []
    for i in range(num_colors):
        hue = i / float(num_colors)
        lightness = 0.5
        saturation = 0.8

        r, g, b = upRange(colorsys.hls_to_rgb(hue, lightness, saturation))
        
        colors_array.append(RGBColor(r, g, b))
        colors_names_array.append(f"color_{i}")
    return colors_array, colors_names_array
