'''
pi433.pcbctrl
(c) Ben Pruitt, 2017 [MIT License, see LICENSE]

Methods to control the pi433 PCB features (12V boost converter, status LEDs)

'''
import atexit

from gevent import sleep
from gevent.lock import Semaphore
import RPi.GPIO as GPIO

GPIO_INIT = False
BOOST_12V_PIN = 4
STATUS_LED_PIN = 19

STATUS_LED_SEMA = Semaphore()


def _initGPIO():
    global GPIO_INIT
    if not GPIO_INIT:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BOOST_12V_PIN, GPIO.OUT)
        GPIO.setup(STATUS_LED_PIN, GPIO.OUT)
        atexit.register(GPIO.cleanup)
        GPIO_INIT = True


def turnStatusLEDOn():
    ''' Turn the green status LED on
    '''
    _initGPIO()
    GPIO.output(STATUS_LED_PIN, 1)


def turnStatusLEDOff():
    ''' Turn the green status LED off
    '''
    _initGPIO()
    GPIO.output(STATUS_LED_PIN, 0)


def blinkStatusLED(blink_str='010101', blink_rate=0.1):
    ''' Blink the green status LED

    Args:
        blink_str (str): binary string representing LED states (0-off, 1-on)
        blink_rate (str): delay between `blink_str` states
    '''
    _initGPIO()
    # Ensure that only one greenlet is blinking the LED at a given time
    # Status LED operation is not mission critical
    if STATUS_LED_SEMA.acquire(blocking=False):
        for s in blink_str:
            GPIO.output(STATUS_LED_PIN, int(s))
            sleep(blink_rate)
        STATUS_LED_SEMA.release()


def turn12VOn():
    ''' Turn the 12V boost converter on
    '''
    _initGPIO()
    GPIO.output(BOOST_12V_PIN, 1)


def turn12VOff():
    ''' Turn the 12V boost converter on
    '''
    _initGPIO()
    GPIO.output(BOOST_12V_PIN, 0)
