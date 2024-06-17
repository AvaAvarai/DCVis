import colorsys


class getColors:
    def __init__(self, num_colors, bg_color, axis_color, default_colors=None, color_names=None):
        self.bg_color = [x / 255.0 for x in bg_color]  # Normalize to [0, 1]
        self.axis_color = [x / 255.0 for x in axis_color]  # Normalize to [0, 1]
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

            r, g, b = [int(x * 255.0) for x in colorsys.hls_to_rgb(hue, lightness, saturation)]

            self.colors_array.append([r, g, b])
            self.colors_names_array.append(f"color_{i}")


def shift_hue(rgb, amount):
    # Convert RGB to HSV
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    # Shift the hue
    h = (h + amount) % 1.0
    # Convert back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)
