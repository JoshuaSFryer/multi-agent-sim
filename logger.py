class Logger:
    def __init__(self):
        self.entries = list()

    def add_entry(self, time, s, i, r):
        self.entries.append(LogEntry(time, s, i, r))
        
    def print_last(self):
        last = self.entries[-1]
        print(f'Time: {last.time}, S: {last.susceptible}, I: {last.infected},\
                R: {last.recovered}')


class LogEntry:
    def __init__(self, time, s, i, r):
        self.time = time
        self.susceptible = s
        self.infected = i
        self.recovered = r