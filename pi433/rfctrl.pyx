
from libcpp cimport bool
import RPi.GPIO as GPIO


cdef extern from "src/RCSwitch.h":
    cdef cppclass RCSwitch:
        RCSwitch()
        void enableTransmit(int nTransmitterPin)
        void disableTransmit()
        void enableReceive(int interrupt)
        void setPulseLength(int nPulseLength)
        void setRepeatTransmit(int nRepeatTransmit)
        unsigned long getReceivedValue()
        unsigned int getReceivedDelay()
        bool available()
        void send(unsigned long Code, unsigned int length)
        void send(char* Code)


cdef extern from "wiringPi.h":
    cdef int wiringPiSetup() nogil


def sendRFCode(rf_code, pulse_length=185, pin=0, repeats=3):
    ''' Send `rf_code` with `pulse_length` over `pin`

    Args:
        rf_code (int): (generally) 7 digit Etekcity switch code
        pulse_length (int): empirically determined pulse length
        pin (int): wiringPi pin number attached to 433 MHz transmitter
    '''
    cdef RCSwitch *switch = new RCSwitch()
    switch.setPulseLength(185)
    switch.enableTransmit(0)
    switch.setRepeatTransmit(repeats)
    switch.send(rf_code, 24)
    del switch


# Run wiringPiSetup on import
wiringPiSetup()
