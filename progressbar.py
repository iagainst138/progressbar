import sys
import time
import threading

class progressbar(object):
    def __init__(self, min_size=0, pre_map={}, post_map={}, precise=False,
            record_time=False, estimate=False, output_stream=sys.stdout, reset=True, full_symbol='=', half_symbol='-'):
        self.previous_output = ''
        self.min_size = min_size
        self.pre_map = pre_map
        self.post_map = post_map 
        self.precise = precise
        self.lock = threading.Lock()
        self.started = False
        self.record_time = record_time 
        self.estimate = estimate
        self.start_time = 0
        self.end_time = 0
        self.previous_size = 0
        self.last_time = {}
        self.output_stream = output_stream
        self.reset = reset
        if len(full_symbol) != len(half_symbol):
            sys.stderr.write("symbol lengths don't match, reverting to defaults\n")
            full_symbol = '='
            half_symbol = '-'
        self.full_symbol = full_symbol
        self.half_symbol = half_symbol

    def progress(self, current_size, max_size, pre='', post=''):
        # reset values
        if self.reset and (self.previous_size > current_size):
            self.last_time = {}
            self.started = False

        if self.record_time and not self.started:
            self.started = True
            self.start_time = time.time()
        
        if max_size < self.min_size:
            return
        
        max_size = float(max_size)
        current_size = float(current_size)
        p = float((current_size/max_size)*100)

        bar = ''
        for i in xrange(0,105,5):
            if p >= i and i%10 == 0:
                bar = self.full_symbol * ( i / 10 ) 
            elif p >= i and i%5 == 0:
                bar = self.full_symbol * ( (i-5) / 10 )
                bar += self.half_symbol
        bar = bar.ljust(len(self.full_symbol) * 10)
        bar = '[' + bar + ']'

        if len(pre) > 0:
            pre = pre + ' '
        else:
            for k in sorted(self.pre_map.keys()):
                if p >= k:
                    pre = self.pre_map[k] + ' '
        
        if len(post) > 0:
            post = post + ' '
        else:
            for k in sorted(self.post_map.keys()):
                if p >= k:
                    post = self.post_map[k] + ' '

        # display points if precise output is desired
        if self.precise:
            str_p = str(p)[:4]
        else:        
            str_p = str(int(p))

        # calculate the the amount of time remaining
        estimate_str = ''
        if self.estimate:
            now = time.time()
            if self.last_time:
                t = now - self.last_time['time']
                diff = current_size - self.last_time['size']
                e = ( t * ( (max_size-current_size)/diff ) )
                if e < 60:
                    estimate_str = str(int(e)) + 's remaining'
                else:
                    mins = int(e/60)
                    secs = int(e%60)
                    estimate_str = str(mins) + 'm ' + str(secs) + 's remaining'
            else:
                self.last_time['time'] = now
                self.last_time['size'] = current_size
                self.last_time['samples'] = 0 
            
            if self.last_time['samples'] < 10000:  # should prob calculate sample rate based off of max_size
                self.last_time['samples']+=1
            else:
                self.last_time['time'] = now
                self.last_time['size'] = current_size
                self.last_time['samples'] = 0
            if p == 100:
                estimate_str = ''

        output = pre + bar + ' ' + str_p + '% ' + estimate_str + ' ' + post

        # append a newline if we are at 100%
        if p == 100:
            if self.record_time:
                self.end_time = time.time()
                str_t = ''
                t = self.end_time - self.start_time
                if t < 60:
                    str_t = str(int(t)) + ' secs'
                else:
                    str_t = str(int(t)/60) + ' mins ' + str(int(t)%60) + ' secs'
                output += ' (duration: ' + str_t + ') '
            output += '\n'

        # clear the line if the new line is shorter than the last
        if len(output) < len(self.previous_output):
            self.write(' '.join(' ' for x in range(0, len(self.previous_output))))

        self.write(output)

        # only becomes useful if called as a thread
        with self.lock:
            self.previous_output = output
            self.previous_size = current_size

    # calls progress in a thread
    def update(self, c, m, pre='', post=''):
        t = threading.Thread(target=self.progress, args=(c,m,pre,post))
        t.start()

    # can be used as a reporthook for urlretrieve
    def reporthook(self, read, block_size, total):
        self.progress(read*block_size, total)

    # a generic write function
    def write(self, line):
        self.output_stream.write('\r' + line)
        self.output_stream.flush()

def loop(l, **kwargs):
    p = progressbar()
    i = 0
    for item in l:
        p.progress(i, len(l), **kwargs)
        yield item
        i+=1
    p.progress(len(l), len(l))

def wait(sleep):
    c = ['\\', '|', '/', '-']
    if sleep > 0:
        i = 0
        previous_t = ''
        while sleep > 0:
            t = '\r' + c[i] + ' ' + str(sleep) + ' '
            if len(t) < len(previous_t):
                sys.stdout.write('\r' + ' '.join(' ' for x in range(0, len(previous_t))))
                sys.stdout.flush()

            sys.stdout.write(t)
            sys.stdout.flush()
            sleep -= 1
            time.sleep(1)
            i+=1
            if i == len(c):
                i=0
            previous_t = t
        clear = ' '.join(' ' for x in range(0, len(t)))
        sys.stdout.write('\r' + clear + '\n')
        sys.stdout.flush()
