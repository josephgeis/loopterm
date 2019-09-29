# -*- coding: utf-8 -*-


class Font:
    RESET = "\033[m"

    STANDOUT = "\033[7m"
    UNDERLINE = "\033[4m"
    REVERSE = STANDOUT
    BLINK = "\033[5m"
    BOLD = "\033[1m"

    class Colors:
        class Foreground:
            BLACK = "\033[38;000m"
            RED = "\033[38;001m"
            GREEN = "\033[38;002m"
            YELLOW = "\033[38;003m"
            BLUE = "\033[38;004m"
            PURPLE = "\033[38;005m"
            CYAN = "\033[38;006m"
            WHITE = "\033[38;007m"

            class Bright:
                BLACK = "\033[38;008m"
                RED = "\033[38;009m"
                GREEN = "\033[38;010m"
                YELLOW = "\033[38;011m"
                BLUE = "\033[38;012m"
                PURPLE = "\033[38;013m"
                CYAN = "\033[38;014m"
                WHITE = "\033[38;015m"

        class Background:
            BLACK = "\033[48;000m"
            RED = "\033[48;001m"
            GREEN = "\033[48;002m"
            YELLOW = "\033[48;003m"
            BLUE = "\033[48;004m"
            PURPLE = "\033[48;005m"
            CYAN = "\033[48;006m"
            WHITE = "\033[48;007m"

            class Bright:
                BLACK = "\033[48;008m"
                RED = "\033[48;009m"
                GREEN = "\033[48;010m"
                YELLOW = "\033[48;011m"
                BLUE = "\033[48;012m"
                PURPLE = "\033[48;013m"
                CYAN = "\033[48;014m"
                WHITE = "\033[48;015m"
