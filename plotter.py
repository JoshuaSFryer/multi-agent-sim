import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns

class Plotter():
    def __init__(self, csv_path ):
        os.makedirs('plot', exist_ok=True)

        # Load in the data
        df = pd.read_csv(csv_path)
        x = df['time_ticks']
        y = [df['infected'], df['recovered'], df['susceptible']]

        # Use Seaborn for prettier plots than vanilla matplotlib
        plt.style.use('seaborn')
        palette = ['#cc4d3d',  '#3d6ccc', '#55cc3d']

        plt.figure(figsize=(12,4))
        plt.stackplot(x, y, labels=['Infected', 'Recovered', 'Susceptible'], colors=palette)
        plt.xlabel('Time (min)')
        plt.ylabel('Population')
        plt.title('SIR Status of Population Over Time')

        # Put the legend outside the graph area
        plt.legend(bbox_to_anchor=(1,1), loc=2)
        plt.tight_layout()

        # Take the timestamp from the .csv file and use it for plot filename
        filename = csv_path.split('/')[1]
        output_path = os.path.join('plot', filename.split('.')[0]+'.pdf')
        plt.savefig(output_path)
        
        plt.show()
