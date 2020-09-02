'''
This code for this progress bar is based on
vladignatyev/progress.py
https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
(MIT License)
'''
import sys


class ProgressBar:
    def __init__(self, duration):
        self._duration = duration
        self._count = 0
        self._bar_len = 60
        self._cancelled = False

    def _disp(self, _, fetched):
        self._progress(fetched / 1000, self._duration)

    def _progress(self, fillin, total, status=''):
        if total == 0 or self._cancelled:
            return
        self._count += fillin
        filled_len = int(round(self._bar_len * self._count / float(total)))
        percents = round(100.0 * self._count / float(total), 1)
        if filled_len > self._bar_len:
            filled_len = self._bar_len
            percents = 100
        bar = '=' * filled_len + ' ' * (self._bar_len - filled_len)
        sys.stdout.write(' [%s] %s%s ...%s\r' % (bar, percents, '%', status))
        sys.stdout.flush()

    def close(self):
        if not self._cancelled:
            self._progress(self._duration, self._duration)

    def cancel(self):
        self._cancelled = True
    
    def is_cancelled(self):
        return self._cancelled
