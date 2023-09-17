import colorsys

class getColors:
    def __init__(self, num_colors, bg_color, axis_color):
        self.bg_color = [x / 255.0 for x in bg_color]  # Normalize to [0, 1]
        self.axis_color = [x / 255.0 for x in axis_color]  # Normalize to [0, 1]
        self.colors_array = []
        self.colors_names_array = []
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
