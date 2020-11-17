
class Logger:
    def __init__(self):
        self.entries = list()

    def add_entry(self, time, s, i, r):
        self.entries.append(LogEntry(time, s, i, r))
        
    def print_last(self):
        last = self.entries[-1]
        print(str(last))

    def save_to_file(self):
        f = open('log.csv', 'w')
        for entry in self.entries:
            string = ','.join((str(entry.time), str(entry.susceptible),
                                str(entry.infected), str(entry.recovered)))
            f.write(string+'\n')
        f.close()


class LogEntry:
    def __init__(self, time, s, i, r):
        self.time = time
        self.susceptible = s
        self.infected = i
        self.recovered = r

    def __str__(self):
        return f'Time: {self.time}, S: {self.susceptible}, I: {self.infected}, R: {self.recovered}'