import numpy as np
from ipaddress import ip_address, ip_network
import re
from Env import Env

env = Env()


def is_valid_ipv4(ip):
    """
    Validates IPv4 addresses.
    """
    pattern = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          |
            0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
              0x0*[0-9a-f]{1,2}
            |
              0+[1-3]?[0-7]{0,2}
            )
          ){0,3}
        |
          0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
          0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
          # Decimal notation, 1-4294967295:
          429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
          42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
          4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(ip) is not None


def is_valid_ipv6(ip):
    """
    Validates IPv6 addresses.
    """
    pattern = re.compile(r"""
        ^
        \s*                         # Leading whitespace
        (?!.*::.*::)                # Only a single whildcard allowed
        (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
        (?:                         # Repeat 6 times:
            [0-9a-f]{0,4}           #   A group of at most four hexadecimal digits
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
        ){6}                        #
        (?:                         # Either
            [0-9a-f]{0,4}           #   Another group
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
            [0-9a-f]{0,4}           #   Last group
            (?: (?<=::)             #   Colon iff preceeded by exacly one colon
             |  (?<!:)              #
             |  (?<=:) (?<!::) :    #
             )                      # OR
         |                          #   A v4 address with NO leading zeros
            (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            (?: \.
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            ){3}
        )
        \s*                         # Trailing whitespace
        $
    """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
    return pattern.match(ip) is not None


def is_valid_ip(ip):
    """
    Validates IP addresses.
    """
    return is_valid_ipv4(ip) or is_valid_ipv6(ip)


def isPrivate(IP: str) -> bool:
    return True if ip_address(IP).is_private else False


def check_port(port) -> str:
    allowed_port_list = [env.get(key="d1"), env.get(key="d2"), env.get(key="d3"), env.get(key="d4"), env.get(key="d5"),
                         env.get(key="d6"), env.get(key="d7"), env.get(key="d8"), env.get(key="d9"), env.get(key="d10")]

    if port not in allowed_port_list:
        return env.get(key="d-any")
    return port


def check_ip(ip: str) -> str:
    if is_valid_ip(ip):
        if isPrivate(ip):
            return env.get(key="r-private")
        else:
            return env.get(key="r-public")
    else:
        return env.get(key="r-non")


def check_direction(ip: str, cidrs) -> str:
    """
    Get the direction of a ip address (In or OUT)
    :param ip: The relevant IP address
    :param cidrs: The range of the IP address
    :return:
    """
    if is_valid_ip(ip):
        count = 0
        for cidr in cidrs:
            if ip_address(ip) in ip_network(cidr):
                count = count + 1
        if count >= 1:
            return env.get(key="x-in")
        else:
            return env.get(key="x-out")
    else:
        return env.get(key="x-non")


def class_generation(row, bot_ip, cnc_ip, victim_ip, loader_ip):
    """

    :param row:
    :param bot_ip:
    :param cnc_ip:
    :param victim_ip:
    :param loader_ip:
    :return:
    """

    if row['src_ip'] == bot_ip or row['dst_ip'] == bot_ip:
        if row['protocol'] == env.get(key="p-ssh") or row['protocol'] == env.get(key="p-sshv2"):
            return 'LOGIN'
        else:
            return 'SCAN'
    elif row['src_ip'] == cnc_ip or row['dst_ip'] == cnc_ip:
        return 'CNC_COM'
    elif ((row['src_ip'] == loader_ip or row['dst_ip'] == loader_ip) and (
            row['protocol'] == env.get(key="p-ftp") or row['protocol'] == env.get(key="p-tcp"))):
        return 'MAL_DOWN'
    elif row['src_ip'] == victim_ip or row['dst_ip'] == victim_ip:
        return 'DDOS'
    else:
        return 'NaN'


def assign_class(dataSet, bot_ip, cnc_ip, victim_ip, loader_ip):
    dataSet["Class"] = dataSet.apply(lambda row: class_generation(row, bot_ip, cnc_ip, victim_ip, loader_ip), axis=1)
    dataSet['Class'] = 'c-' + dataSet['Class']

    dataSet.drop(['time', 'dir', 'info', 'dst_ip', 'src_ip', 'src_port'], axis=1, inplace=True)

    return dataSet


def preProcessing(dataSet):
    """
    small: length < 60 -> Control packets
    medium: 60 < length <1000 -> Other packets
    large: length > 1000 -> file downloading packets
    :param dataSet: Anomaly filtered data set
    :return:
    """

    cidr = env.get(key="cidr")

    dataSet.drop(dataSet.index[dataSet['src_ip'] == '10.1.0.33'], inplace=True)
    dataSet.drop(dataSet.index[dataSet['dst_ip'] == '10.1.0.33'], inplace=True)
    dataSet.drop(dataSet.index[dataSet['src_ip'] == '10.1.0.2'], inplace=True)
    dataSet.drop(dataSet.index[dataSet['dst_ip'] == '10.1.0.2'], inplace=True)

    dataSet['length'] = np.where((dataSet.length <= 60), 0, dataSet.length)
    dataSet['length'] = np.where(np.logical_and(dataSet.length > 60, dataSet.length <= 90), 1, dataSet.length)
    dataSet['length'] = np.where(np.logical_or(dataSet.length > 90, dataSet.length < 1000), 2, dataSet.length)
    dataSet['length'] = np.where((dataSet.length >= 1000), 3, dataSet.length)

    dataSet = dataSet[dataSet['dst_ip'].notnull()]

    dataSet['Dst_ip_range'] = dataSet.apply(lambda row: check_ip(str(row["dst_ip"])), axis=1)
    dataSet['Direction'] = dataSet.apply(lambda row: check_direction(str(row["dst_ip"]), cidr), axis=1)

    dataSet['length'] = dataSet['length'].astype('str')
    dataSet['dst_port'] = dataSet['dst_port'].astype('str')
    dataSet['protocol'] = dataSet['protocol'].astype('str')

    dataSet['protocol'] = 'p-' + dataSet['protocol']
    dataSet['length'] = 'l-' + dataSet['length']
    dataSet['dst_port'] = 'd-' + dataSet['dst_port']
    dataSet['dst_port'] = dataSet.apply(lambda row: check_port(str(row["dst_port"])), axis=1)

    return dataSet


def convertToStringList(string):
    """
    Converts the string of the dataframe into list of strings
    :param string:
    :return:
    """
    a = string.replace('\'', '')
    b = a.replace('[', '')
    c = b.replace(']', '')
    l = c.split(", ")
    return l


def oneHot(dataSet, featureList):
    """
    Convert antecedents and  consequents into one hot format
    :param dataSet:
    :param featureList:
    :return:
    """
    r, c = dataSet.shape
    zeroArray = np.zeros(shape=(r, len(featureList)))
    for index, row in dataSet.iterrows():
        ItemA = row[env.get(key="itemA")]

        for item in ItemA:
            if item in featureList:
                indexA = featureList.index(item)
                zeroArray[index][indexA] = 1

    return zeroArray
