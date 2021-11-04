from machine import Pin, I2C, Timer
from ssd1306 import SSD1306_I2C
import utime
import urandom

# Buttons
UP = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
LEFT = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
RIGHT = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
DOWN = machine.Pin(28, machine.Pin.IN, machine.Pin.PULL_UP)

# OLED CODE
sda=machine.Pin(20)
scl=machine.Pin(21)
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
oled.fill(0)

SCREEN_HEIGHT = 64
SCREEN_WIDTH = 128

SEGMENT_WIDTH = 8
SEGMENT_PIXELS = int(SCREEN_HEIGHT/SEGMENT_WIDTH)

SEGMENTS_HIGH = int(SCREEN_HEIGHT/SEGMENT_WIDTH)
SEGMENTS_WIDE = int(SCREEN_WIDTH/SEGMENT_WIDTH)
VALID_RANGE = [[int(i /SEGMENTS_HIGH), i % SEGMENTS_HIGH] for i in range(SEGMENTS_WIDE * SEGMENTS_HIGH -1)]

# Game code
game_timer = Timer()
player = None
food = None

class Snake:
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    
    def __init__(self, x=int(SEGMENTS_WIDE/2), y=int(SEGMENTS_HIGH/2) + 1):
        self.segments = [[x, y]]
        self.x = x
        self.y = y
        self.dir = urandom.randint(0,3)
        self.state = True
        
    def reset(self, x=int(SEGMENTS_WIDE/2), y=int(SEGMENTS_HIGH/2) + 1):
        self.segments = [[x, y]]
        self.x = x
        self.y = y
        self.dir = urandom.randint(0,3)
        self.state = True
        
    def move(self):
        new_x = self.x
        new_y = self.y
        
        if self.dir == Snake.UP:
            new_y -= 1
        elif self.dir == Snake.DOWN:
            new_y += 1
        elif self.dir == Snake.LEFT:
            new_x -= 1
        elif self.dir == Snake.RIGHT:
            new_x += 1
        
        for i, _ in enumerate(self.segments):
            if i != len(self.segments) - 1:
                self.segments[i][0] = self.segments[i+1][0]
                self.segments[i][1] = self.segments[i+1][1]
        
        if self._check_crash(new_x, new_y):
            # Oh no, we killed the snake :C
            self.state = False
        
        self.x = new_x
        self.y = new_y
        
        self.segments[-1][0] = self.x
        self.segments[-1][1] = self.y
        
    def eat(self):
        oled.fill_rect(self.x * SEGMENT_PIXELS, self.y * SEGMENT_PIXELS, SEGMENT_PIXELS, SEGMENT_PIXELS, 0)
        oled.rect(self.x * SEGMENT_PIXELS, self.y * SEGMENT_PIXELS, SEGMENT_PIXELS, SEGMENT_PIXELS, 1)
        self.segments.append([self.x, self.y])
        
    def change_dir(self, dir):
        if  dir == Snake.DOWN and self.dir == Snake.UP:
            return False
        
        elif dir == Snake.UP and self.dir == Snake.DOWN:
            return False
        
        elif dir == Snake.RIGHT and self.dir == Snake.LEFT:
            return False
        
        elif dir == Snake.LEFT and self.dir == Snake.RIGHT:
            return False
        
        self.dir = dir
        
    def _check_crash(self, new_x, new_y):
        if new_y >= SEGMENTS_HIGH or new_y < 0 or new_x >= SEGMENTS_WIDE or new_x < 0 or [new_x, new_y] in self.segments:
           return True
        else:
            return False
    
    def draw(self):
        oled.rect(self.segments[-1][0] * SEGMENT_PIXELS, self.segments[-1][1] * SEGMENT_PIXELS, SEGMENT_PIXELS, SEGMENT_PIXELS, 1)


def main():
    global player
    global food
    
    player = Snake()
    food = urandom.choice([coord for coord in VALID_RANGE if coord not in player.segments])
    oled.fill_rect(food[0] * SEGMENT_PIXELS , food[1] * SEGMENT_PIXELS, SEGMENT_PIXELS, SEGMENT_PIXELS, 1)
    
    # Playing around with this cool timer.
    game_timer.init(freq=5, mode=Timer.PERIODIC, callback=update_game)

    while True:
        if player.state == True:
            # If the snake is alive
            if UP.value() == 0:
                    player.change_dir(Snake.UP)
                    
            elif RIGHT.value() == 0:
                    player.change_dir(Snake.RIGHT)
                    
            elif LEFT.value() == 0:
                    player.change_dir(Snake.LEFT)
                    
            elif DOWN.value() == 0:
                    player.change_dir(Snake.DOWN)
        
        else:
            # If the snake is dead
            if UP.value() == 0:
                # Revive our snake friend
                oled.fill(0)
                player.reset()
                food = urandom.choice([coord for coord in VALID_RANGE if coord not in player.segments])
                oled.fill_rect(food[0] * SEGMENT_PIXELS , food[1] * SEGMENT_PIXELS, SEGMENT_PIXELS, SEGMENT_PIXELS, 1)
                
                
def update_game(timer):
    global food
    global player
    
    # Remove the previous tail of the snake (more effecient than clearing the entire screen and redrawing everything)
    oled.fill_rect(player.segments[0][0] * SEGMENT_PIXELS, player.segments[0][1] * SEGMENT_PIXELS, SEGMENT_PIXELS, SEGMENT_PIXELS, 0)
    
    # Move the snake
    player.move()
    
    if player.state == False:
        # I think he's dead now :/
        oled.fill(0)
        oled.text("Game Over!" , int(SCREEN_WIDTH/2) - int(len("Game Over!")/2 * 8), int(SCREEN_HEIGHT/2) - 8)
        oled.text("Snake length:" + str(len(player.segments)) , int(SCREEN_WIDTH/2) - int(len("Snake length:" + str(len(player.segments))) /2 * 8), int(SCREEN_HEIGHT/2) + 16)
    
    else:
        # Our snake is still alive and moving
        if food[0] == player.x and food[1] == player.y:
            # Our snake reached the food
            player.eat()
            food = urandom.choice([coord for coord in VALID_RANGE if coord not in player.segments])
            oled.fill_rect(food[0] * SEGMENT_PIXELS , food[1] * SEGMENT_PIXELS, SEGMENT_PIXELS, SEGMENT_PIXELS, 1)
        
        player.draw()
        
    # Show the new frame
    oled.show()

if __name__ == "__main__":
    main()
