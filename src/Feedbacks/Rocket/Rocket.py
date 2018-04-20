# !/usr/bin/env pyff

"""
This is the script for creating the rocket feedback for
NF experiment. This is a demo with a dummy variable for
calculating the speed of the rocket - this will be done
in future with the input from the EEG power spectrum
(e.g. theta band power)
"""

from PygameFeedback import PygameFeedback
from random import randrange
import pygame as pg

## constants ##

WHITE = [255, 255, 255]
BLACK = [0, 0, 0]
GREY = [192, 192, 192]


class Rocket(PygameFeedback):
    # TRIGGER VALUES FOR PARALLEL PORT (MARKERS)
    START_EXP, END_EXP = 100, 101
    CROSS = 30
    START_TRIAL = 15
    INPUT = 55

    def on_control_event(self, data):
        parallel = data.get('parallelsignal', None)
        if parallel == None:
            return
        if parallel:
            self.val = parallel  # where signal comes in
            self.send_parallel(self.INPUT)

    def init(self):

        PygameFeedback.init(self)
        self.pg_is_running = False
        # timing
        self.FPS = 30
        self.stimTime = 8
        self.otherTime = 2
        self.trials = 10
        self.completedtrials = 0
        self.badtrials = 0
        self.goodtrials = 0

        self.fullscreen = True

        ## feedback states
        self.f = 0
        self.val = self.f

        ## colors
        self.backgroundColor = GREY
        self.foregroundColor = BLACK

    def init_pygame(self):
        # initialise screen
        pg.init()
        self.w, self.h = self.screenSize
        self.screen = pg.display.set_mode((self.w, self.h), pg.FULLSCREEN)
        self.screenrect = self.screen.get_rect()
        self.clock = pg.time.Clock()

        # load graphics
        self.bg = pg.image.load('data/background.png').convert()
        self.rkt = pg.image.load('data/01_rocket.png').convert_alpha()
        self.bg_rect = self.bg.get_rect(center=self.screenrect.center)
        self.pos = self.rkt.get_rect(center=self.screenrect.center)

        self.font = pg.font.SysFont("liberationserif", 56)
        self.text = "Prepare for liftoff!"

        self.surface_c = pg.Surface((self.w, self.h), pg.SRCALPHA)
        self.surface_l = pg.Surface((self.w, self.h), pg.SRCALPHA)

    def pre_mainloop(self):
        self.send_parallel(self.START_EXP)
        self.state = self.message
        self.init_pygame()
        self.currentTick = 0
        self.state_finished = False

    def tick(self):
        # if last state is finished proceed to next state
        # full sequence should be MESSAGE, BLANK SCREEN, CROSS, BLANK, STIM, BLANK, CROSS, BLANK, STIM, ETC.
        if self.state_finished:
            if self.state == self.message:
                self.state = self.pre_cross
            elif self.state == self.pre_cross:
                self.send_parallel(self.CROSS)
                self.state = self.cross
            elif self.state == self.cross:
                self.state = self.pre_stim
            elif self.state == self.pre_stim:
                self.send_parallel(self.START_TRIAL)
                self.state = self.stim
            elif self.state == self.stim:
                if self.completedtrials == self.trials:
                    self.on_stop()
                else:
                    self.state = self.pre_cross
            self.state_finished = False
            self.currentTick = 0 #reset timer
        self.clock.tick(self.FPS)
        for event in pg.event.get():
            if event.type in (pg.QUIT, pg.K_ESCAPE):
                self.on_stop()

    def play_tick(self):
        state = self.state
        if state == self.message:
            self.message()
        elif state == self.pre_cross:
            self.pre_cross()
        elif state == self.cross:
            self.cross()
        elif state == self.pre_stim:
            self.pre_stim()
        elif state == self.stim:
            self.stim()

    def message(self):
        if self.currentTick / self.FPS == self.otherTime:
            # finished
            self.state_finished = True
            self.screen.fill(self.backgroundColor)
            pg.display.update()
        else:
            image = self.font.render(self.text, True, self.foregroundColor)
            rect = image.get_rect()
            rect.center = self.screen.get_rect().center
            self.screen.fill(self.backgroundColor)
            self.screen.blit(image, rect)
            pg.display.update()
            self.currentTick += 1

    def pre_cross(self):
        if self.currentTick / self.FPS == self.otherTime:
            self.screen.fill(self.backgroundColor)
            self.state_finished = True
            pg.display.update()
        else:
            self.screen.fill(self.backgroundColor)
            pg.display.update()
            self.currentTick += 1

    def cross(self):
        if self.currentTick / self.FPS == self.otherTime:
            # finished
            self.state_finished = True
            self.screen.fill(self.backgroundColor)
            pg.display.update()
        else:
            c1 = pg.draw.line(self.surface_c, self.foregroundColor, (2 * self.w / 5, self.h / 2),
                              (3 * self.w / 5, self.h / 2), 10)
            c2 = pg.draw.line(self.surface_c, self.foregroundColor, (self.w / 2, 2 * self.h / 5),
                              (self.w / 2, 3 * self.h / 5), 10)
            self.screen.fill(self.backgroundColor)
            self.screen.blit(self.surface_c, (0, 0))
            pg.display.update()
            self.currentTick += 1

    def pre_stim(self):
        if self.currentTick / self.FPS == self.otherTime:
            self.screen.fill(self.backgroundColor)
            self.state_finished = True
            pg.display.update()
        else:
            self.screen.fill(self.backgroundColor)
            pg.display.update()
            self.currentTick += 1

    def stim(self):
        if self.currentTick / self.FPS == self.stimTime:
            # finished
            self.completedtrials += 1
            self.screen.fill(self.backgroundColor)
            self.state_finished = True
            pg.display.update()
        else:
            # move rocket
            self.pos = self.pos.move(0, self.val)
            l1 = pg.draw.line(self.surface_l, self.foregroundColor, (self.w / 3, 5 * self.h / 6),
                              (2 * self.w / 3, 5 * self.h / 6), 10)  # lower line
            l2 = pg.draw.line(self.surface_l, self.foregroundColor, (self.w / 3, self.h / 6),
                              (2 * self.w / 3, self.h / 6), 10)  # upper line
            #  collision detection
            if l1.colliderect(self.pos):
                self.badtrials += 1  #
            if l2.colliderect(self.pos):
                self.goodtrials += 1 # if trying to upregulate

            self.screen.blit(self.bg, self.bg_rect)
            self.screen.blit(self.surface_l, (0, 0))
            self.screen.blit(self.rkt, self.pos)
            pg.display.update()
            self.currentTick += 1

    def post_mainloop(self):
        self.send_parallel(self.END_EXP)
        self.on_stop()
        PygameFeedback.post_mainloop(self)

        ## put something here if you want to show score or rate their performance ##


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    fb = Rocket()
    fb.on_init()
    fb.on_play()
