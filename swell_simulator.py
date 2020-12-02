import pygame
import pygame.gfxdraw
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

        self.D = {"l1": 8 * scale,  "l2": 59 * scale,  "l3": 26 * scale,
                  "l4": 60 * scale, "l4'": 34 * scale, "l5": 68 * scale,
                  "a": 58 * scale,  "b": 17 * scale,   "c": 16 * scale,
                  "d": 18 * scale,  "speed": 200}  # degrees per second

        self.psi = 0
        self.phi = 0
        self.theta = 0
        self.zeta = 0
        self.psis = []
        self.phis = []
        self.thetas = []
        self.zetas = []
        self.X = []
        self.Y = []
        self.dim_displayed = "Φ"
        self.Nmax_psis = 200

        self.origin_coord = (self.settings.screen_width/2, self.settings.screen_height/3)
        self.machine_grabbed = False

        self.settings_window = SettingsWindow(self)

        self.scale_font = pygame.font.SysFont('arial', 14)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed(num_buttons=3)[0]:
                        if self._cursor_on_origin():
                            self.machine_grabbed = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if not pygame.mouse.get_pressed(num_buttons=3)[0]:
                        self.machine_grabbed = False

            self.A_coord = (self.origin_coord[0] - self.D["l1"] * m.sin(self.psi),
                            self.origin_coord[1] - self.D["l1"] * m.cos(self.psi))
            try:
                self.settings_window.error_label.grid_remove()
                self.phi = self._calc_phi(self.psi, self.D["l1"], self.D["l2"], self.D["l3"], self.D["a"], self.D["b"])
                self.theta = self._calc_theta(self.phi, self.D["l3"], self.D["l4'"], self.D["l5"],
                                              self.D["a"], self.D["b"], self.D["c"], self.D["d"])
            except ValueError:
                self.settings_window.math_er()
            except:
                break
            else:
                self.psi += self.D["speed"] / self.fps * (m.pi / 180)
                self.psi = self.psi % (2*m.pi)

                self.C_coord = (self.origin_coord[0] + self.D["b"], self.origin_coord[1] + self.D["a"])
                self.D_coord = (self.C_coord[0] - self.D["l3"] * m.sin(self.phi), self.C_coord[1] + self.D["l3"] * m.cos(self.phi))
                self.B_coord = (self.C_coord[0] - self.D["l3"] * m.sin(self.phi+m.pi/2), self.C_coord[1] + self.D["l3"] * m.cos(self.phi+m.pi/2))

                self.F_coord = (self.origin_coord[0] - self.D["d"], self.origin_coord[1] + self.D["c"])
                self.E_coord = (self.F_coord[0] + self.D["l5"] * m.sin(self.theta), self.F_coord[1] + self.D["l5"] * m.cos(self.theta))

                angleED = m.atan((self.E_coord[1] - self.D_coord[1]) / (self.E_coord[0] - self.D_coord[0]))
                self.N_coord = (self.D_coord[0] - self.D["l4"]*m.cos(angleED), self.D_coord[1] - self.D["l4"]*m.sin(angleED))

                self.data_plot()

                self._update_screen()
                if self.machine_grabbed:
                    self.origin_coord = pygame.mouse.get_pos()

            self.settings_window.root.update()
            self.settings.clock.tick_busy_loop(self.fps)

            # if round(m.sqrt((self.A_coord[0]-self.B_coord[0])**2 + (self.A_coord[1]-self.B_coord[1])**2)) != self.D["l2"]:
            #    print('ERROR1')
            # if round(m.sqrt((self.E_coord[0]-self.D_coord[0])**2 + (self.E_coord[1]-self.D_coord[1])**2)) != self.D["l4'"]:
            #    print('ERROR2')

    @staticmethod
    def _calc_phi(psi, l1, l2, l3, a, b):
        p = l1 * m.cos(psi) + a
        q = l1 * m.sin(psi) + b
        r = (l1 ** 2 + a ** 2 + b ** 2 + l3 ** 2 - l2 ** 2 + 2 * a * l1 * m.cos(psi) +
             2 * b * l1 * m.sin(psi)) / (2 * l3)
        return 2 * m.atan((p - m.sqrt(p ** 2 + q ** 2 - r ** 2)) / (q + r))

    @staticmethod
    def _calc_theta(phi, l3, l4_, l5, a, b, c, d):
        p = d + b - l3 * m.sin(phi)
        q = l3 * m.cos(phi) + a - c
        r = (l5 ** 2 + l3 ** 2 + (c - a) ** 2 + (d + b) ** 2 - l4_ ** 2 - 2 * l3 * (c - a) * m.cos(phi) -
             2 * l3 * (d + b) * m.sin(phi)) / (2 * l5)
        return 2 * m.atan((p - m.sqrt(p ** 2 + q ** 2 - r ** 2)) / (q + r))

    def _cursor_on_origin(self):
        org_rect = pygame.Rect(0, 0, 10, 10)
        org_rect.center = self.origin_coord
        return ((org_rect.left < pygame.mouse.get_pos()[0] <org_rect.right)
                and org_rect.top < pygame.mouse.get_pos()[1] < org_rect.bottom)

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self._draw_ground()
        self._draw_lines()
        self._draw_links()
        self._draw_angles()
        if self.dim_displayed: self._draw_curve()
        pygame.display.flip()

    def _draw_ground(self):
        base = pygame.Rect(self.F_coord[0]-15, self.F_coord[1]+15, 35+self.D["d"], 15)
        pygame.draw.rect(self.screen, (170, 170, 170), base)
        pygame.draw.line(self.screen, (170, 170, 170), (self.origin_coord[0], self.F_coord[1]+15), self.origin_coord, 3)
        pygame.draw.line(self.screen, (170, 170, 170), (self.F_coord[0], self.F_coord[1]+15), self.F_coord, 3)

        wall = pygame.Rect(0, 0, 15, 50)
        wall.midleft = (self.C_coord[0] + 35, self.C_coord[1])
        pygame.draw.line(self.screen, (170, 170, 170), (self.C_coord[0] + 35, self.C_coord[1]), self.C_coord, 3)
        pygame.draw.rect(self.screen, (170, 170, 170), wall)

    def _draw_lines(self):
        pygame.draw.line(self.screen, (0, 0, 0), self.origin_coord, self.A_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.A_coord, self.B_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.B_coord, self.C_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.C_coord, self.D_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.D_coord, self.E_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.E_coord, self.F_coord, 3)
        pygame.draw.line(self.screen, (0, 0, 0), self.E_coord, self.N_coord, 3)

    def _draw_links(self):
        pygame.draw.circle(self.screen, (255, 165, 0), self.origin_coord, 4)
        pygame.draw.circle(self.screen, (255, 0, 0), self.A_coord, 4)
        pygame.draw.circle(self.screen, (255, 0, 0), self.B_coord, 4)
        pygame.draw.circle(self.screen, (255, 0, 0), self.C_coord, 4)
        pygame.draw.circle(self.screen, (255, 0, 0), self.D_coord, 4)
        pygame.draw.circle(self.screen, (255, 0, 0), self.E_coord, 4)
        pygame.draw.circle(self.screen, (255, 0, 0), self.F_coord, 4)
        pygame.draw.circle(self.screen, (255, 0, 0), self.N_coord, 4)
        # zeta = m.atan((self.D["a"]+self.D["l3"]*m.cos(self.phi)-(self.D["c"]+self.D["l5"]*m.cos(self.theta))) /
        #              (self.D["b"]-self.D["l3"]*m.sin(self.phi)-(-self.D["d"]+self.D["l5"]*m.sin(self.theta))))
        # pygame.draw.circle(self.screen, (0, 255, 0), (self.C_coord[0]-(self.D["l3"]*m.sin(self.phi)+self.D["l4"]*m.cos(zeta)),
        #                                              self.C_coord[1]+(self.D["l3"]*m.cos(self.phi)-self.D["l4"]*m.sin(zeta))), 4)

    def _draw_angles(self):
        if self.dim_displayed == "Φ":
            plan_phi = pygame.Rect(0, 0, self.D["l3"]*3/2, self.D["l3"]*3/2)
            plan_phi.center = self.C_coord
            pygame.draw.line(self.screen, (0, 119, 190), self.C_coord, (self.C_coord[0], self.C_coord[1]+self.D["l3"]*2/3+10), 1)
            #pygame.draw.arc(self.screen, (0, 119, 190), plan_phi, -(0 + (self.phi > 0)*self.phi) - m.pi/2,
            #                                                      -(0 + (self.phi < 0)*self.phi) - m.pi/2, 3)
            pygame.gfxdraw.arc(self.screen, int(self.C_coord[0]), int(self.C_coord[1]), int(self.D["l3"]*2/3),
                               (0 + (self.phi < 0)*int(self.phi*180/m.pi)) + 90,
                               (0 + (self.phi > 0)*int(self.phi*180/m.pi)) + 90, (255, 0, 0))

        elif self.dim_displayed == "θ":
            plan_theta = pygame.Rect(0, 0, self.D["l5"]*3, self.D["l5"]*3)
            plan_theta.center = self.F_coord
            pygame.draw.line(self.screen, (0, 119, 190), self.F_coord, (self.F_coord[0], self.F_coord[1] + self.D["l5"]*4/5+10), 1)
            #pygame.draw.arc(self.screen, (0, 119, 190), plan_theta, (0 + (self.theta < 0) * self.theta) - m.pi / 2,
            #                                                        (0 + (self.theta > 0) * self.theta) - m.pi / 2, 3)
            pygame.gfxdraw.arc(self.screen, int(self.F_coord[0]), int(self.F_coord[1]), int(self.D["l5"]*4/5),
                               -(0 + (self.theta > 0) * int(self.theta * 180 / m.pi)) + 90,
                               -(0 + (self.theta < 0) * int(self.theta * 180 / m.pi)) + 90, (255, 0, 0))

    def data_plot(self):
        self.zeta = m.atan(
            (self.D["a"] + self.D["l3"] * m.cos(self.phi) - (self.D["c"] + self.D["l5"] * m.cos(self.theta))) /
            (self.D["b"] - self.D["l3"] * m.sin(self.phi) - (-self.D["d"] + self.D["l5"] * m.sin(self.theta))))
        if len(self.psis) >= self.Nmax_psis:
            self.psis.pop(0)
            self.phis.pop(0)
            self.thetas.pop(0)
            self.zetas.pop(0)
            self.X.pop(0)
            self.Y.pop(0)

        self.psis.append(self.psi)
        self.phis.append(self.phi)
        self.thetas.append(self.theta)
        self.zetas.append(self.zeta)
        self.X.append(self.D["l3"] * m.sin(self.phi) + self.D["l4"] * m.cos(self.zeta))
        self.Y.append(self.D["l3"] * m.cos(self.phi) - self.D["l4"] * m.sin(self.zeta))

    def _draw_curve(self):
        y_axis_start = 25
        x_axis = self.settings.screen_height/10 + 20
        unit_len = 70
        angle_scale = unit_len / (m.pi / 4)  # pi/4 rad <--> 70 px
        X_scale = unit_len / (self.D["l3"]+self.D["l4"])
        Y_scale = unit_len / (self.D["l3"]+self.D["l4"])
        pygame.draw.line(self.screen, (0, 0, 0), (0, x_axis), (self.Nmax_psis + y_axis_start, x_axis))
        pygame.draw.line(self.screen, (0, 0, 0), (y_axis_start, 0), (y_axis_start, x_axis * 2))
        for i in [-unit_len, unit_len]:
            pygame.draw.line(self.screen, (255, 0, 0), (y_axis_start, x_axis + i), (y_axis_start + 10, x_axis + i))
        for i in [-unit_len//2, unit_len//2]:
            pygame.draw.line(self.screen, (255, 0, 0), (y_axis_start, x_axis + i), (y_axis_start + 5, x_axis + i))
        if self.dim_displayed in ["Φ", "θ", "ζ"]:
            text = self.scale_font.render('π/4', True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.midright = (y_axis_start-2, x_axis - unit_len)
            self.screen.blit(text, textRect)
        elif self.dim_displayed == "X":
            text = self.scale_font.render(f'{int(self.D["l3"]+self.D["l4"])}', True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.midright = (y_axis_start-2, x_axis - unit_len)
            self.screen.blit(text, textRect)
        elif self.dim_displayed == "Y":
            text = self.scale_font.render(f'{int(self.D["l3"]+self.D["l4"])}', True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.midright = (y_axis_start-2, x_axis - unit_len)
            self.screen.blit(text, textRect)

        text = self.scale_font.render('0', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.topright = (y_axis_start-3, x_axis)
        self.screen.blit(text, textRect)

        for index, item in enumerate(self.psis):
            if self.dim_displayed == "Φ":
                pygame.gfxdraw.pixel(self.screen, y_axis_start + index,
                                     int(x_axis-int(self.phis[index]*angle_scale)), (0, 0, 255))
            elif self.dim_displayed == "θ":
                pygame.gfxdraw.pixel(self.screen, y_axis_start+index,
                                     int(x_axis-int(self.thetas[index]*angle_scale)), (0, 0, 255))
            elif self.dim_displayed == "ζ":
                pygame.gfxdraw.pixel(self.screen, y_axis_start + index,
                                     int(x_axis-int(self.zetas[index]*angle_scale)), (0, 0, 255))
            elif self.dim_displayed == "X":
                pygame.gfxdraw.pixel(self.screen, y_axis_start + index,
                                     int(x_axis-int(self.X[index]*X_scale)), (0, 0, 255))
            elif self.dim_displayed == "Y":
                pygame.gfxdraw.pixel(self.screen, y_axis_start + index,
                                     int(x_axis-int(self.Y[index]*Y_scale)), (0, 0, 255))


if __name__ == '__main__':
    swell_sim = SwellSimulator()
    swell_sim.run()
