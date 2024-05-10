import colorsys

color_dict = {
    'black': [0, 0, 0, 255],
    'white': [255, 255, 255, 255],
    'red': [255, 0, 0, 255],
    'green': [0, 255, 0, 255],
    'blue': [0, 0, 255, 255],
    'dark_gray': [169, 169, 169, 255],
    'gray': [128, 128, 128, 255],
    'light_gray': [211, 211, 211, 255],
}

class getColors:
    def __init__(self, num_colors, bg_color, axis_color, default_colors=None, color_names=None):
        self.bg_color = downRange(bg_color)
        self.axis_color = downRange(axis_color)
        self.colors_array = []
        self.colors_names_array = []
        if default_colors is not None:
            self.colors_array = default_colors
            if color_names is not None:
                self.colors_names_array = color_names
        self.num_colors = num_colors
        self.generate_colors()

    def generate_colors(self):
        for i in range(self.num_colors):
            hue = i / float(self.num_colors)
            lightness = 0.5
            saturation = 0.8

            r, g, b = upRange(colorsys.hls_to_rgb(hue, lightness, saturation))
            
            self.colors_array.append([r, g, b])
            self.colors_names_array.append(f"color_{i}")


def shift_hue(rgb, amount):
    # Convert RGB to HSV
    r, g, b = downRange(rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    # Shift the hue
    h = (h + amount) % 1.0
    # Convert back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return upRange([r, g, b])

def get_color_dict():
    return color_dict

def downRange(color):
    return [x / 255.0 for x in color]

def upRange(color):
    return [int(x * 255) for x in color]
