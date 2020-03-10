__all__ = (
    'Color',
    'no_color',
    'blue',
    'green',
    'red',
    'yellow',
)


class Color:
    """Class for adding some color to text.

    Example of use:

        print('This text will be red' * Color(91))
        print('This text also will be red' * red)
        print(green('This text will be green as grass in minecraft'))

    """

    def __init__(self, color_number):
        """Initialize class instance."""
        self.color_number = color_number

    def __call__(self, value):
        return self.colored_value(value)

    def __mul__(self, value):
        return self.colored_value(value)

    def __rmul__(self, value):
        return self.colored_value(value)

    def colored_value(self, value):
        return (
            f'\033[{self.color_number}m{value}\033[00m'
            if self.color_number
            else value
        )


# Predefined colors

no_color = Color(None)
blue = Color(94)
green = Color(92)
red = Color(91)
yellow = Color(93)
