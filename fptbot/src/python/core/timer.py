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

@since May 6, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import datetime
import threading

class BaseTimer(object):
    def __init__(self, interval=None, callback=None):
        self.interval = interval
        self.callback = callback


class SingleTimer(BaseTimer):
    def start(self):
        if hasattr(self, 'timer') and self.timer:
            self.stop()
        
        self.timer = threading.Timer(self.interval, self.callback)
        self.timer.start()
    
    def stop(self):
        self.timer.stop()


class DailyTimer(BaseTimer):
    def start(self):
        if hasattr(self, 'timer') and self.timer:
            self.stop()
        
        self.timer = threading.Timer(self.interval, self._check, [datetime.date.today()])
        self.timer.start()
    
    def stop(self):
        # TODO check if timer was started
        self.timer.stop()
    
    def _check(self, start):
        today = datetime.date.today()
        
        if today != start:
            self.callback(today)
        
        self.start()


timer_map = {
    'single': SingleTimer,
    'daily': DailyTimer
}

