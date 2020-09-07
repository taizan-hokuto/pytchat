'''
This code for this progress bar is based on
vladignatyev/progress.py
https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
(MIT License)
'''
import sys


class ProgressBar:
    def __init__(self, total, status):
        self._bar_len = 60
        self._cancelled = False
        print(''.join([' ' * 10, '|', '-' * (self._bar_len), '|']), end="")
        self.reset(total=total, status=status)

    def reset(self, symbol_done="=", symbol_space=" ", total=100, status=''):
        self._symbol_done = symbol_done
        self._symbol_space = symbol_space
        self._total = total
        self._status = status
        self._old_len = 0
        self._count = 0
        print()
        print(f'{status:<11}', end='')

    def _disp(self, _, fetched):
        self._progress(fetched, self._total)

    def _progress(self, fillin, total):
        if total == 0 or self._cancelled:
            return
        self._count += fillin
        filled_len = int(round(self._bar_len * self._count / float(total)))
        if filled_len > self._bar_len:
            filled_len = self._bar_len
        print((filled_len - self._old_len) * self._symbol_done, end="")
        sys.stdout.flush()
        self._old_len = filled_len

    def close(self):
        if not self._cancelled:
            self._progress(self._total, self._total)

    def cancel(self):
        self._cancelled = True
    
    def is_cancelled(self):
        return self._cancelled
