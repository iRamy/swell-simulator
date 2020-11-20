import pygame
import sys
import math as m
from settings import Settings
from gui import SettingsWindow


class SwellSimulator:

    def __init__(self):
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption('Swell Simulator')

        self.fps = 60

        scale = 3

        self.D = {"l1": 8 * scale,
                  "l2": 59 * scale,
                  "l3": 26 * scale,
                  "l4": 60 * scale,
                  "l4'": 30 * scale,
                  "l5": 68 * scale,
                  "a": 58 * scale,
                  "b": 17 * scale,
                  "c": 16 * scale,
                  "d": 18 * scale}

        self.psi = 0
        self.phi = 0

        self.origin_coord = (self.settings.screen_width * 2 / 3, self.settings.screen_height / 5)

        self.settings_window = SettingsWindow(self)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()

            self.A_coord = (self.origin_coord[0] - self.D["l1"] * m.sin(self.psi),
                            self.origin_coord[1] - self.D["l1"] * m.cos(self.psi))
            try:
                self.settings_window.error_label.grid_remove()
                self.phi = self._calc_phi(self.psi, self.D["l1"], self.D["l2"], self.D["l3"], self.D["a"], self.D["b"])
                self.theta = self._calc_theta(self.phi, self.D["l3"], self.D["l4'"], self.D["l5"],
                                              self.D["a"], self.D["c"], self.D["b"], self.D["d"])
            except ValueError:
                self.settings_window.math_er()
            else:
                self.psi += 200 / self.fps * (m.pi / 180)  # degrees per second

                self.C_coord = (self.origin_coord[0] + self.D["b"], self.origin_coord[1] + self.D["a"])
                self.D_coord = (self.C_coord[0] - self.D["l3"] * m.sin(self.phi), self.C_coord[1] + self.D["l3"] * m.cos(self.phi))
                self.B_coord = (self.C_coord[0] - self.D["l3"] * m.sin(self.phi+m.pi/2), self.C_coord[1] + self.D["l3"] * m.cos(self.phi+m.pi/2))

                self.F_coord = (self.origin_coord[0] - self.D["d"], self.origin_coord[1] + self.D["c"])
                self.E_coord = (self.F_coord[0] + self.D["l5"] * m.sin(self.theta), self.F_coord[1] + self.D["l5"] * m.cos(self.theta))

                angleED = m.atan((self.E_coord[1] - self.D_coord[1]) / (self.E_coord[0] - self.D_coord[0]))
                self.N_coord = (self.D_coord[0] - self.D["l4"]*m.cos(angleED), self.D_coord[1] - self.D["l4"]*m.sin(angleED))

                self._update_screen()

            self.settings_window.root.update()
            self.settings.clock.tick_busy_loop(self.fps)
            print(m.sqrt((self.E_coord[0]-self.D_coord[0])**2 + (self.E_coord[1]-self.D_coord[1])**2))
            print(m.sqrt((self.A_coord[0]-self.B_coord[0])**2 + (self.A_coord[1]-self.B_coord[1])**2))

    def _calc_phi(self, psi, l1, l2, l3, a, b):
        p = l1 * m.cos(psi) + a
        q = l1 * m.sin(psi) + b
        r = (l1 ** 2 + a ** 2 + b ** 2 + l3 ** 2 - l2 ** 2 + 2 * a * l1 * m.cos(psi) +
             2 * b * l1 * m.sin(psi)) / (2 * l3)
        return 2 * m.atan((p - m.sqrt(p ** 2 + q ** 2 - r ** 2)) / (q + r))

    def _calc_theta(self, phi, l3, l4_, l5, a, b, c, d):
        p = d + b - l3 * m.sin(phi)
        q = l3 * m.cos(phi) + a - c
        r = (l5 ** 2 + l3 ** 2 + (c - a) ** 2 + (d + b) ** 2 - l4_ ** 2 - 2 * l3 * (c - a) * m.cos(phi) -
             2 * l3 * (d + b) * m.sin(phi)) / (2 * l5)
        return 2 * m.atan((p - m.sqrt(p ** 2 + q ** 2 - r ** 2)) / (q + r))

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self._draw_ground()
        self._draw_lines()
        self._draw_links()
        pygame.display.flip()

    def _draw_ground(self):
        wall = pygame.Rect(0, 0, 15, 50)
        wall.midleft = (self.C_coord[0] + 35, self.C_coord[1])
        pygame.draw.line(self.screen, (170, 170, 170), (self.C_coord[0] + 35, self.C_coord[1]), self.C_coord, 3)
        pygame.draw.rect(self.screen, (170, 170, 170), wall)

        base = pygame.Rect(self.F_coord[0]-15, self.F_coord[1]+15, 35+self.D["d"], 15)
        pygame.draw.rect(self.screen, (170, 170, 170), base)
        pygame.draw.line(self.screen, (170, 170, 170), (self.origin_coord[0], self.F_coord[1]+15), self.origin_coord, 3)
        pygame.draw.line(self.screen, (170, 170, 170), (self.F_coord[0], self.F_coord[1]+15), self.F_coord, 3)


    def _draw_lines(self):
        pygame.draw.line(self.screen, (0, 0, 0), self.origin_coord, self.A_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.A_coord, self.B_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.B_coord, self.C_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.C_coord, self.D_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.D_coord, self.E_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.E_coord, self.F_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.E_coord, self.N_coord, 3)

    def _draw_links(self):
        pygame.draw.circle(self.screen, (255, 0, 0), self.origin_coord, 3)
        pygame.draw.circle(self.screen, (255, 0, 0), self.A_coord, 3)
        pygame.draw.circle(self.screen, (255, 0, 0), self.B_coord, 3)
        pygame.draw.circle(self.screen, (255, 0, 0), self.C_coord, 3)
        pygame.draw.circle(self.screen, (255, 0, 0), self.D_coord, 3)
        pygame.draw.circle(self.screen, (255, 0, 0), self.E_coord, 3)
        pygame.draw.circle(self.screen, (255, 0, 0), self.F_coord, 3)


if __name__ == '__main__':
    swell_sim = SwellSimulator()
    swell_sim.run()
