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
        with open(self.filename, 'w') as f:
            string = ','.join(( 'time_ticks',
                                'susceptible',
                                'infected',
                                'recovered',
                                'infection_rate',
                                'curr_isolated',
                                'total_isolated',
                                'curr_cautious',
                                'total_cautious',
                                'num_tracing_notified',
                                'num_geonotified',
                                'unnecessary_isolations'
                                ))
            f.write(string + '\n')
            print(string.replace(',', '\t'))

    def log_line(self, entry):
        with open(self.filename, 'a') as f:
            string = ','.join(( str(entry.time), 
                                str(entry.susceptible),
                                str(entry.infected), 
                                str(entry.recovered),
                                str(entry.infection_rate),
                                str(entry.curr_isolating),
                                str(entry.total_isolating),
                                str(entry.curr_cautious),
                                str(entry.total_cautious),
                                str(entry.tracing_notifications),
                                str(entry.total_geonotified)
                                ))
            f.write(string+'\n')
            print(string.replace(',','\t'))


class LogEntry:
    def __init__(self, time, s, i, r, rate, trace, curr_isolating, total_isolating,
                    curr_cautious, total_cautious, geo, unnecessary):
        self.time = time
        self.susceptible = s
        self.infected = i
        self.recovered = r
        self.infection_rate = rate
        self.tracing_notifications = trace
        self.curr_isolating = curr_isolating
        self.total_isolating = total_isolating
        self.curr_cautious = curr_cautious
        self.total_cautious = total_cautious
        self.total_geonotified = geo
        self.unnecessary_isolations = unnecessary

    def __str__(self):
        return (f'Time: {self.time}, S: {self.susceptible}, I: {self.infected}, '
                f'R: {self.recovered}, ')