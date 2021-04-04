from Env import Env
from HashTab import HashTab
from Shell import Shell
import csv
import threading
import os
import pandas as pd
import queue
import time
import re
import subprocess
import ipaddress
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from Device import Device

env = Env()

q = queue.Queue()
c = HashTab(100)
has_profiles = False
times = 0
writeHeader = True
all_profiles_frame = pd.DataFrame()

shell = Shell()


class Handler(FileSystemEventHandler):

    def __init__(self, file_queue):
        self.file_queue = file_queue
        self.shell = Shell()

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Event is created, you can process it now 
            print("Watchdog received created event - % s." % event.src_path)

            if 'traffic' in str(event.src_path):
                self.file_queue.put(str(event.src_path)[2:])


def get_host_ip():
    p1 = subprocess.Popen(['ip', 'addr'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', 'state UP', '-A2'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['tail', '-n1'], stdin=p2.stdout, stdout=subprocess.PIPE)
    p4 = subprocess.Popen(['awk', '{print $2}'], stdin=p3.stdout, stdout=subprocess.PIPE)
    output = p4.communicate()[0]

    host_ip = output.decode('utf-8')[:-1]
    return host_ip


def get_network_data():
    network = ipaddress.ip_network(get_host_ip(), strict=False)
    result = subprocess.run(['sudo', 'nmap', '-sP', str(network)], stdout=subprocess.PIPE)
    data = result.stdout.decode('utf-8')

    ip_adresses = re.findall(r'[0-9]+(?:\.[0-9]+){3}', data)

    mac_address = re.findall(r'(?:[0-9a-fA-F]:?){12}', data)

    net_data = []

    for i in range(len(mac_address)):
        device = Device(mac_address[i], ip_adresses[i], 'dev' + str(i))
        net_data.append(device)

    return net_data


def profile(filename):
    global has_profiles
    global times
    global all_profiles_frame
    i = 0
    inserted = 0

    traffic_frame = pd.DataFrame(read_traffic(filename))

    if os.path.exists('Profiles/devices.csv') and not traffic_frame.empty:
        devices_frame = pd.read_csv('Profiles/devices.csv')

        for index, row in devices_frame.iterrows():
            routes_frame = traffic_frame.loc[(traffic_frame.src_ip == row[2]) | (traffic_frame.dst_ip == row[2])]
            if not routes_frame.empty:
                routes_frame['dir'] = routes_frame.apply(lambda x: direction(str(row[2]), x['src_ip'], x['dst_ip']),
                                                         axis=1)
                profile_frame = routes_frame.groupby(['src_ip', 'dst_ip', 'dst_port', 'protocol', 'dir'],
                                                     as_index=False).length.agg(['count', 'mean']).reset_index()

                for index1, row1 in profile_frame.iterrows():
                    route = str(row1['src_ip']) + str(row1['dst_ip']) + str(row1['protocol']) + str(row1['dir'])
                    if c.insert(route, index1):
                        inserted += 1

                all_profiles_frame = all_profiles_frame.append(profile_frame, ignore_index= True)

                profile_file = "Profiles/" + row['name'] + ".csv"
                profile_frame = profile_frame.drop('src_ip', axis=1)
                profile_frame.to_csv(profile_file, index=False, mode='a')

                

        times = times + 1
        if times > int(env.get(key="times")):
            has_profiles = True


        print('inserted ' + str(inserted))

    else:
        i = i + 1
        print(i)

    print("Profiling complete")


def filter_anomalies(filename):
    found = 0
    missing = 0
    anomalies = []
    allowes = []
    i = 0
    global writeHeader
    global all_profiles_frame

    traffic_frame2 = pd.DataFrame(read_traffic(filename))

    if os.path.exists('Profiles/devices.csv') and not traffic_frame2.empty:

        devices_frame2 = pd.read_csv('Profiles/devices.csv')
        traffic_frame2['dir'] = traffic_frame2.apply(lambda x: direction_without_source(devices_frame2, x['src_ip'], x['dst_ip']), axis=1)


        for index, row in traffic_frame2.iterrows():

            route = str(row['src_ip']) + str(row['dst_ip']) + str(row['protocol']) + str(row['dir'])
            index = c.find(route)
            if index is None:
                print(index, "Couldn't find key", route)
                missing += 1
                anomalies.append(row)
            else:
                print(index, "Found", route)
                found += 1
                allowes.append(row)

        print(str(found) + " " + str(missing))

        anomaly_df = pd.DataFrame(anomalies)
        allowes_df = pd.DataFrame(allowes)

        # behavioral anomaly analysis
        if not allowes_df.empty:
            grouped_frame = allowes_df.groupby(['src_ip', 'dst_ip', 'dst_port', 'protocol', 'dir'],
                                                     as_index=False).length.agg(['count', 'mean']).reset_index()
            print(grouped_frame.head())
            print(all_profiles_frame.head())
            for index, row in grouped_frame.iterrows():
                temp_df = all_profiles_frame.loc[ (all_profiles_frame.src_ip == row['src_ip']) & (all_profiles_frame.dst_ip == row['dst_ip']) & (all_profiles_frame.protocol == row['protocol']) & (all_profiles_frame.dir == row['dir'])]

                if not temp_df.empty:
                    high_count = int(temp_df['count'].values[0]) + 20
                    low_count = int(temp_df['count'].values[0]) - 20

                    if not (high_count >= row['count'] and low_count <= row['count']):
                        temp_anomalies = allowes_df.loc[(allowes_df.src_ip == row['src_ip']) & (allowes_df.dst_ip == row['dst_ip']) & (allowes_df.dst_port == row['dst_port']) & (allowes_df.protocol == row['protocol']) & (allowes_df.dir == row['dir'])]
                        anomaly_df = anomaly_df.append(temp_anomalies)
                        temp_anomalies.to_csv('UpdatedAnomali/tempAnomalies.csv', index=False, mode='a')

        anomaly_df.to_csv('UpdatedAnomali/anomalies.csv', index=False, mode='a', header=False)
        allowes_df.to_csv('UpdatedAnomali/allowes.csv', index=False, mode='a', header=False)

        # if writeHeader:
        #     shell.execute("chmod +x /root/GateWay/createAnomalieFile.sh")
        #     shell.execute("sh /root/GateWay/createAnomalieFile.sh")
        #     anomaly_df.to_csv('UpdatedAnomali/anomalies.csv', index=False, mode='a', header=False)
        #     allowes_df.to_csv('UpdatedAnomali/allowes.csv', index=False, mode='a', header=False)
        # else:
        #     anomaly_df.to_csv('UpdatedAnomali/anomalies.csv', index=False, mode='a', header=False)
        #     allowes_df.to_csv('UpdatedAnomali/allowes.csv', index=False, mode='a', header=False)

    else:
        i = i + 1
        print(i)


def create_profiles(name):
    print(str(name) + ' Thread starts')
    if not (os.path.exists('Profiles/devices.csv')):
        current_devices = get_network_data()
        print(current_devices)
        devices_dict = {
            'name': [],
            'mac': [],
            'internal_ip': []
        }

        for i in range(len(current_devices)):
            if not (os.path.exists('Profiles/' + current_devices[i].name)):
                open('Profiles/' + current_devices[i].name + '.csv', 'a').close()

            devices_dict['name'].append(current_devices[i].name)
            devices_dict['mac'].append(current_devices[i].mac)
            devices_dict['internal_ip'].append(current_devices[i].ip)

        df = pd.DataFrame(devices_dict)
        df.to_csv('Profiles/devices.csv', index=False)


def direction(device_ip, src_ip, dst_ip):
    if device_ip == src_ip:
        return 'OUT'
    elif device_ip == dst_ip:
        return 'IN'
    else:
        return 'NA'

def direction_without_source(devices_frame, src_ip, dst_ip):

    if src_ip in devices_frame.internal_ip.values:
        return 'OUT'
    elif dst_ip in devices_frame.internal_ip.values:
        return 'IN'
    else:
        return 'NA'

def read_traffic(filename):
    if os.path.exists(filename):
        packets = []
        filepath = filename
        csv_file = open(filepath, mode='r')
        csv_reader = csv.DictReader(csv_file,
                                    fieldnames=['no', 'time', 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'protocol',
                                                'length', 'info'])
        regex = re.compile(r'[0-9]+(?:\.[0-9]+){3}')

        for row in csv_reader:
            if row['time'] != '' and row['time'] != None:
                packet = {
                    'time': row['time'],
                    'src_ip': {True: row['src_ip'], False: '0.0.0.0'}[
                        row['src_ip'] != '' and bool(regex.match(row['src_ip']))],
                    'src_port': {True: row['src_port'], False: '0'}[row['src_port'] != ''],
                    'dst_ip': {True: row['dst_ip'], False: '0.0.0.0'}[
                        row['dst_ip'] != '' and bool(regex.match(row['dst_ip']))],
                    'dst_port': {True: row['dst_port'], False: '0'}[row['dst_port'] != ''],
                    'protocol': row['protocol'],
                    'length': int(row['length']),
                    'info': row['info'],
                    'dir': 'NA'
                }
                if (packet['protocol'] != 'ICMPv6' and packet['src_ip'].split('.')[3] != str(2) and
                        packet['dst_ip'].split('.')[3] != str(2)):
                    packets.append(packet)

        csv_file.close()
        os.remove(filepath)

        return packets


def __main():
    thread1 = threading.Thread(target=create_profiles, args=('t1',))
    thread1.start()

    shell.execute("chmod +x /root/GateWay/createAnomalieFile.sh")
    shell.execute("sh /root/GateWay/createAnomalieFile.sh")

    file_queue = queue.Queue()
    global writeHeader

    event_handler = Handler(file_queue)
    observer = Observer()
    observer.schedule(event_handler, './Profiles/', recursive=False)
    print("About to start observer")
    observer.start()

    try:
        while True:
            if file_queue.qsize() > 0 and not has_profiles:
                profile(file_queue.get())

            if file_queue.qsize() > 0 and has_profiles:
                filter_anomalies(file_queue.get())
                writeHeader = False
            time.sleep(5)

    except KeyboardInterrupt:
        observer.stop()
        print("Observer Stopped")

    observer.join()


if __name__ == '__main__':
    __main()
