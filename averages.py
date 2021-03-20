import os
import pandas as pd
import sys

class Averager():
    def __init__(self, path):
        self.csv_folder = path
        self.output_path = os.path.join(self.csv_folder, 'averages.csv')

        with open(self.output_path, 'w') as f:
            header = ','.join(( 'min_rate',
                                'max_rate',
                                'avg_rate',
                                'tracing_notified',
                                'geonotified',
                                'total_cautious',
                                'avg_cautious'
                                ))
            f.write(header + '\n')
        
        for sev in (1,2,3):
            self.get_averages(sev)
            self.write_row('\n')


    def get_averages(self, severity):
        for mode in ('A', 'B', 'C', 'D'):
            iden = f'mode{mode}_sev{severity}'
            file_path = os.path.join(self.csv_folder, iden, iden+'.csv')
            df = pd.read_csv(file_path)

            # Infection rate data
            max_infected = df['infection_rate'].max()
            min_infected = df['infection_rate'].min()
            avg_infected = round(df['infection_rate'].mean(), 2)

            # Contact-tracing data
            notified_tracing = df['num_tracing_notified'].iat[-1]
            notified_geo = df['num_geonotified'].iat[-1]

            # Cautious isolating data
            cautious_isolated = df['total_cautious'].iat[-1]
            avg_cautious = round(df['curr_cautious'].mean(), 2)

            # False alarm data
            false_alarms = df['unnecessary_isolations'].iat[-1]
            # Combine and write to file
            row = ','.join((    mode, 
                                str(min_infected), 
                                str(max_infected), 
                                str(avg_infected),
                                str(notified_tracing),
                                str(notified_geo),
                                str(cautious_isolated),
                                str(avg_cautious),
                                str(false_alarms)
                            ))
            self.write_row(row)


    def write_row(self, row):
        with open(self.output_path, 'a') as f:
            f.write(row + '\n')


if __name__ == '__main__':
    a = Averager(sys.argv[1])
