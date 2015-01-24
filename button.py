import time

from addon import *

state = namespace()
state.released = 1
state.pressed = 2
state.falling = 4
state.rising = 8
state.changing = (state.rising | state.falling)
state.auto_repeat = 16
state.auto_rate = 30; #auto_repeat per second
state.auto_delay = 500; #in millis

class button:
    def __init__(self, pressed_state, auto_rate = state.auto_rate, auto_delay = state.auto_delay):
        self.auto_delay = auto_delay
        self.auto_rate = auto_rate
        self.start = 0
        self.start_press = 0
        self.pressed_state = pressed_state
        self.state_ = state.released
        self.old_read = not pressed_state
    
    def update(self, read):
        read = (self.pressed_state == read)
        
        if self.state_ & (state.falling | state.auto_repeat):
            self.state_ = state.pressed
            return
        
        if self.state_ & state.rising:
            self.state_ = state.released
            return
        
        t = time.time()*1000
        if self.state_ & state.pressed:
            if (t - self.start_press) > (1000.0 / self.auto_rate):
                self.start_press = time.time()*1000
                self.state_ = (state.auto_repeat | state.pressed)
            
        if read != self.old_read:
            if self.start == 0:
                self.start = t
            else:
                if t - self.start > 2: # deprell
                    self.state_ = self.state_ << 2 #brings pressed -> rising and released -> falling
                    self.start_press = t + self.auto_delay - (1000.0 / self.auto_rate)
                    self.old_read = read
        else:
            self.start = 0
    
    def state(self):
        return self.state_
    
    def __eq__(self, rhs_state):
        return self.state_ & rhs_state
