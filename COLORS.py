import colorsys

def downRange(color):
    return [int(x * 255) for x in color]

def upRange(color):
    return [x / 255.0 for x in color]

class HSVColor:
    """Model for HSV color"""
    
    def __init__(self, h, s, v):
        self.h = h
        self.s = s
        self.v = v
    
    def __copy__(self):
        return HSVColor(self.h, self.s, self.v)

    def to_rgb(self):
        r, g, b = colorsys.hsv_to_rgb(self.h, self.s, self.v)
        r, g, b = downRange([r, g, b])
        return r, g, b

    def shift_hue(self, amount):
        self.h = (self.h + amount) % 1.0
        return self  # Return the modified object for further use

class RGBColor:
    """Model for RGB color"""
    
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __copy__(self):
        return RGBColor(self.r, self.g, self.b)
    
    def to_rgb(self):
        return self.r, self.g, self.b

    def to_hsv(self):
        r, g, b = upRange([self.r, self.g, self.b])
        return colorsys.rgb_to_hsv(r, g, b)

    def shift_hue(self, amount):
        # Convert to HSV, shift hue, and convert back to RGB
        hsv = HSVColor(*self.to_hsv())
        hsv.shift_hue(amount)
        self.r, self.g, self.b = hsv.to_rgb()
        return self  # Return the modified object for further use

def generate_benign_malignant_colors():
    """Generates benign (GREEN) and malignant (RED) colors"""
    colors_array: list[RGBColor] = [RGBColor(0, 255, 0), RGBColor(255, 0, 0)]
    colors_names_array = ["Green", "Red"]
    return colors_array, colors_names_array

def generate_colors(num_colors):
    """Generates a list of unique colors based on the number of colors specified"""
    colors_array = []
    colors_names_array = []
    for i in range(num_colors):
        hue = i / float(num_colors)
        lightness = 0.5
        saturation = 0.8

        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        r, g, b = downRange([r, g, b])
        colors_array.append(RGBColor(r, g, b))
        colors_names_array.append(f"color_{i}")
    return colors_array, colors_names_array
