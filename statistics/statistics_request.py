import requests
import datetime
import os
import argparse
import time
import matplotlib.pyplot as plt
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Statistic of latency of http request to server')
    parser.add_argument('--host', type=str, default='192.168.2.132', help='IP of server')
    parser.add_argument('--port', type=str, default='32777', help='Port of server')
    parser.add_argument('--url', type=str, default='/users/ecg/rawdata/', help='URL of api')
    parser.add_argument('--second', type=str, default='10', help='Data seconds')
    parser.add_argument('--times', type=int, default=10, help='Times to calculate average latency')
    parser.add_argument('--avgPerPatient', type=str, default='avgPerPatient.png', help='Image name of latency of per patient')
    args = parser.parse_args()
        
    # Create report directory if not exist
    date = datetime.date.today()
    dir = str(date)
    try:
        os.mkdir(dir)
    except Exception as e:
        print(f'Directory: {dir} already existed', file=sys.stderr)
    
    #################### Testing ####################
    test = {'1': 0, '2': 0, '5': 0, '10': 0, '50': 0, '100': 0, '150': 0, '200': 0, '300': 0}
    perPatient = {'1': 0, '2': 0, '5': 0, '10': 0, '50': 0, '100': 0, '150': 0, '200': 0, '300': 0}
    for count in test:
        url = 'http://' + args.host + ':' + args.port + args.url + args.second + '/' + count
        sum = 0 # Millisecond
        print(f'Testing: {url}', file=sys.stderr)
        for i in range(args.times):
            t1 = time.time()
            req = requests.get(url)
            t2 = time.time()
            sum += (t2 - t1) * 1000
        test[count] = sum / args.times
        perPatient[count] = test[count] / int(count)
        
    ########## Plot Avg Per Patient Latency ##########
    x_data = list(perPatient.keys())
    y_data = list(perPatient.values())
    
    
    # Convert x-axis strings to numerical positions
    x_pos = range(len(x_data))

    # Create a line plot
    plt.plot(x_pos, y_data, marker='o')

    # Customize the plot
    plt.xlabel('Request Patient Counts')
    plt.ylabel('Latency(ms)')
    plt.xticks(x_pos, x_data)  # Set x-axis labels
    plt.title('Single Patient Latency')

    # Display the plot
    plt.savefig(dir + '/' + args.avgPerPatient)
    
    ########## Generate Report ##########
    print(f'Time Cost')
    for count in test:
        print(f'  Request Patient Counts: {count} => {format(test[count], ".2f")}ms')

    print('')
    print(f'Per Patient Latency')
    for count in perPatient:
        print(f'  Request Patient Counts: {count} => {format(perPatient[count], ".2f")}ms')
    
    
    