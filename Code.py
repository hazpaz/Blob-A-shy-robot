# Blob: A Shy Robot - my midterm project
# When someone comes close, Blob covers its eye with its hand and turns purple.
# When they leave, Blob peeks out (pink), then relaxes and gets happy (gold).

import time
import board
import digitalio
import pwmio
import neopixel
from adafruit_motor import servo
import adafruit_hcsr04

#  my settings (These can be changed to tune her) 
SCARE_DISTANCE = 80    # closer than this (cm) = she gets shy
CALM_DISTANCE = 110    # farther than this (cm) = they left
WARMUP_SECONDS = 4     # time alone before she is happy again

HAND_DOWN = 10         # eyes uncovered
HAND_HALF = 90         # peeking
HAND_UP = 170          # eyes covered (not 180, so the servo doesn't get hot)

NUM_PIXELS = 12        # LEDs on my ring
BRIGHTNESS = 0.6

SHY_COLOR = (110, 0, 255)       # purple
PEEK_COLOR = (255, 0, 100)      # hot pink
HAPPY_COLOR = (255, 140, 0)     # gold

# turns on power for the servo header and the ring's 5V
power = digitalio.DigitalInOut(board.EXTERNAL_POWER)
power.direction = digitalio.Direction.OUTPUT
power.value = True

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D5, echo_pin=board.D6)
ring = neopixel.NeoPixel(board.EXTERNAL_NEOPIXELS, NUM_PIXELS, brightness=BRIGHTNESS)
hand = servo.Servo(pwmio.PWMOut(board.EXTERNAL_SERVO, frequency=50),
                   min_pulse=600, max_pulse=2400)

angle = HAND_DOWN
color = HAPPY_COLOR


def distance():
    # if the sensor hears nothing, pretend nobody is close
    try:
        return sonar.distance
    except RuntimeError:
        return 999


def move_hand(target):
    # moves slowly so it looks cute
    global angle
    step = 4 if target > angle else -4
    while abs(target - angle) > 4:
        angle += step
        hand.angle = angle
        time.sleep(0.012)
    angle = target
    hand.angle = angle
    time.sleep(0.3)
    hand.angle = None   # let the servo rest so it stays cool


def fade_to(new_color, steps=20):
    # slowly changes the ring from the old color to the new one
    global color
    for i in range(1, steps + 1):
        ring.fill(tuple(int(a + (b - a) * i / steps)
                        for a, b in zip(color, new_color)))
        time.sleep(0.015)
    color = new_color


#  start out happy 
hand.angle = HAND_DOWN
ring.fill(HAPPY_COLOR)
mood = "happy"
left_at = 0
near = 0

while True:
    d = distance()

    # needs 2 close readings in a row so one bad reading doesn't scare herit

    if near >= 2 and mood != "shy":
        print("shy")
        fade_to(SHY_COLOR, 10)
        move_hand(HAND_UP)
        mood = "shy"

    elif mood == "shy" and d > CALM_DISTANCE:
        print("peeking")
        move_hand(HAND_HALF)
        fade_to(PEEK_COLOR)
        mood = "peeking"
        left_at = time.monotonic()

    elif mood == "peeking" and time.monotonic() - left_at > WARMUP_SECONDS:
        print("happy")
        move_hand(HAND_DOWN)
        fade_to(HAPPY_COLOR)
        mood = "happy"

    time.sleep(0.05)
