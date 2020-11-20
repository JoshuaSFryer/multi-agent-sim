from datetime import datetime
import os
class Logger:
    def __init__(self):
        self.filename = None
        os.makedirs('log', exist_ok=True)

    def create_log_file(self):
        time = datetime.now()
        timestamp = time.strftime('%Y-%m-%d_%H:%M:%S')
        self.filename = os.path.join('log',timestamp + '.csv')

    def log_line(self, entry):
        with open(self.filename, 'a') as f:
            string = ','.join((str(entry.time), str(entry.susceptible),
                                    str(entry.infected), str(entry.recovered)))
            f.write(string+'\n')
            print(str(entry))


class LogEntry:
    def __init__(self, time, s, i, r):
        self.time = time
        self.susceptible = s
        self.infected = i
        self.recovered = r

    def __str__(self):
        return f'Time: {self.time}, S: {self.susceptible}, I: {self.infected}, R: {self.recovered}'