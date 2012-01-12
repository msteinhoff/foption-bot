# -*- coding: UTF-8 -*-
"""
$Id$

$URL$

Copyright (c) 2010 foption

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@since Sep 22, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

HALT = 0

LOCAL_MEMORY = 1
LOCAL_FILESYSTEM = 2
LOCAL_SERVICE = 3
LOCAL_COMPONENT = 4

NETWORK_SERVICE = 5
NETWORK_MANAGEMENT = 6
NETWORK_INTERACTION = 7

LEVELS = [
    HALT, 
    LOCAL_MEMORY, LOCAL_FILESYSTEM, LOCAL_SERVICE, LOCAL_COMPONENT,
    NETWORK_SERVICE, NETWORK_MANAGEMENT, NETWORK_INTERACTION
]

LEVELS_START = [
    LOCAL_MEMORY, LOCAL_FILESYSTEM, LOCAL_SERVICE, 
    NETWORK_SERVICE, NETWORK_MANAGEMENT, NETWORK_INTERACTION
]

LEVELS_STOP = [
    HALT, 
]

STATE_STARTING = 1
STATE_RUNNING = 2
STATE_STOPPING = 3
STATE_HALTED = 4

DIRECTION_UP = 1
DIRECTION_DOWN = 2

class Runlevel(object):
    def __init__(self, autoboot=False, minimum_start=None):
        self.level = minimum_start

def calculate_direction(current, requested):
    """
    Calculate the rl change direction based on current and requested rl.
    
    If the requested runlevel is greater than the current runlevel,
    DIRECTION_UP is returned, otherwise DIRECTION_DOWN.
    
    @param current: The current runlevel.
    @param requested: The requested runlevel.
    
    @return DIRECTION_UP or DIRECTION_DOWN
    """
    direction = {True: DIRECTION_UP, False: DIRECTION_DOWN}
    
    return direction[current < requested]

def calculate_distance(current, requested):
    """
    Calculate the steps between the given current and requested runlevel.
    
    The calculation is based on the following table:
    current = 0, requested = 6 -> [1, 2, 3, 4, 5, 6]
    current = 2, requested = 4 -> [3, 4]
    current = 5, requested = 1 -> [4, 3, 2, 1]
    current = 6, requested = 0 -> [5, 4, 3, 2, 1, 0]
    
    @param current: The current runlevel.
    @param requested: The requested runlevel.
    """
    
    if current == requested:
        distance = []

    if current < requested:
        distance = range(current+1, requested+1)

    if current > requested:
        distance = range(requested+1, current+1)
        distance.reverse()

    return distance
