import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import sys

class Plotter():
    def __init__(self, csv_path, ident):
        os.makedirs('plot', exist_ok=True)
        self.output_dir = os.path.join('plot', ident)
        os.makedirs(self.output_dir, exist_ok=True)

        legend = False
        # if ident in ('modeD_sev2', 'modeD_sev3'):
        #     legend = True

        sev = 0
        if ident.split('_')[1] == 'sev3':
            sev = 3
        elif ident.split('_')[1] == 'sev2':
            sev = 2

        # Use Seaborn for prettier plots than vanilla matplotlib
        plt.style.use('seaborn')
        
        # Load in the data
        df = pd.read_csv(csv_path)
        self.plot_SIR(df, legend, sev)
        self.plot_infection_rate(df)
        self.plot_notifications(df)
        self.plot_isolations(df)
        self.plot_cautious_isolations(df)
        self.plot_false_alarms(df)

        


    def plot_SIR(self, df, legend, sev):
        x = df['time_ticks']
        y = [df['infected'], df['recovered'], df['susceptible']]

        palette = ['#cc4d3d',  '#3d6ccc', '#55cc3d']

        if legend:
            plt.figure(figsize=(5,4))
        else:
            plt.figure(figsize=(6,4))
        plt.stackplot(x, y, labels=['Infected', 'Recovered', 'Susceptible'], colors=palette)
        plt.xlabel('Time (ticks)')
        plt.ylabel('Population')
        plt.title('SIR Status of Population Over Time')

        if sev == 2:
            plt.ylim([0,4000])
        elif sev == 3:
            plt.ylim([0,9000])

        # Put the legend outside the graph area
        if legend:
            plt.legend(bbox_to_anchor=(1,1), loc=2)
        plt.tight_layout()

        filename = 'SIR_graph.pdf'
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path)
        plt.close()


    def plot_infection_rate(self, df):
        x = df['time_ticks']
        # y = [100 * i for i in df['infection_rate']]
        y = df['infection_rate'] * 100

        plt.figure(figsize=(4, 4))
        plt.plot(x, y)
        plt.xlabel('Time (ticks)')
        plt.ylabel('Infection Rate (%)')
        plt.title('Population Infection Rate Over Time')
        plt.ylim([0,100])

        filename = 'infection_rate_graph.pdf'
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path)
        plt.close()


    def plot_notifications(self, df):
        x = df['time_ticks']
        y_contact = df['num_tracing_notified']
        y_geo = df['num_geonotified']

        plt.style.use('seaborn')
        palette = ['#cc4d3d',  '#3d6ccc', '#55cc3d']

        plt.figure(figsize=(4, 4))
        plt.plot(x, y_contact, label='Notified via Tracing')
        plt.plot(x, y_geo, label='Notified via Geonotification')
        plt.xlabel('Time (ticks)')
        plt.ylabel('Number of Notifications')
        plt.title('Total Notifications Issued Over Time')

        # Put the legend outside the graph area
        # plt.legend(bbox_to_anchor=(1, 1), loc=2)
        plt.legend(loc='upper left')
        plt.tight_layout()

        filename = 'notification_graph.pdf'
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path)
        plt.close()


    def plot_isolations(self, df):
        x = df['time_ticks']
        y_curr_iso = df['curr_isolated']
        y_curr_caut = df['curr_cautious']
        y_total_iso = df['total_isolated']
        y_total_caut = df['total_cautious']

        plt.style.use('seaborn')
        palette = ['#cc4d3d',  '#3d6ccc', '#55cc3d']

        plt.figure(figsize=(4, 4))
        plt.plot(x, y_total_iso, label='Total Self-Isolations')
        plt.bar(x, y_curr_iso, label='Current Self-Isolations')
        plt.xlabel('Time (ticks)')
        plt.ylabel('Number of Isolations')
        plt.title('Self-Isolations Over Time')

        # Put the legend outside the graph area
        # plt.legend(bbox_to_anchor=(1, 1), loc=2)
        plt.legend(loc='upper left')
        plt.tight_layout()

        filename = 'isolation_graph.pdf'
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path)
        plt.close()

    def plot_cautious_isolations(self, df):
        x = df['time_ticks']
        y_curr_caut = df['curr_cautious']
        y_total_caut = df['total_cautious']

        plt.style.use('seaborn')
        palette = ['#cc4d3d',  '#3d6ccc', '#55cc3d']

        plt.figure(figsize=(4, 4))
        plt.plot(x, y_total_caut, label='Total Cautious Isolations')
        plt.bar(x, y_curr_caut, label='Current Cautious Isolations')
        plt.xlabel('Time (ticks)')
        plt.ylabel('Number of Isolations')
        plt.title('Cautious Isolations Over Time')

        # Put the legend outside the graph area
        # plt.legend(bbox_to_anchor=(1, 1), loc=2)
        plt.legend(loc='upper left')
        plt.tight_layout()

        filename = 'cautious_isolation_graph.pdf'
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path)
        plt.close()


    def plot_false_alarms(self, df):
        x = df['time_ticks']
        y = df['unnecessary_isolations']

        plt.figure(figsize=(5, 4))
        plt.plot(x, y)
        plt.xlabel('Time (ticks)')
        plt.ylabel('False Alarms')
        plt.title('Total False-Alarm Isolations Over Time')

        filename = 'false_alarms.pdf'
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path)
        plt.close()


if __name__ == "__main__":
    iden = sys.argv[1]
    csv_path = os.path.join('log', iden, iden+'.csv')
    p = Plotter(csv_path, iden)
