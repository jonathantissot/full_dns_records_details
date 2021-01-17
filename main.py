from argparse import ArgumentParser
from datetime import datetime
import yaml
import csv


def dynect_parser(data, delimiter):
    parsed_data = data.split('/')
    parsed_index = parsed_data.index(delimiter)
    return parsed_data[parsed_index + 1]


def check_ip_in_subnet(ip, subnet):
    from netaddr import IPNetwork, IPAddress, core
    try:
        if IPAddress(ip) in IPNetwork(subnet):
            return True
    except core.AddrFormatError:
        return False
    return False


def get_dns(dns_details):
    import requests
    import json
    import boto3

    records_list = [['Zone', 'Name', 'Type', 'IP', 'Present in Subnet']]
    if 'dynect' in dns_details['dns_providers'].keys():
        dynect_url = 'https://api.dynect.net'
        dynect_url_session = dynect_url + '/REST/Session/'
        dynect = dns_details['dns_providers']['dynect']
        payload_get_token = {
            'customer_name': dynect['customer_name'],
            'user_name': dynect['user_name'],
            'password': dynect['password']
        }
        res = json.loads(requests.post(dynect_url_session, json=payload_get_token).text)
        dynect['token'] = res['data']['token']
        headers = {
            'Auth-Token': dynect['token'],
            'Content-Type': 'application/json'
        }
        payload = {}
        url_all_zones = dynect_url + '/REST/Zone/'
        res = json.loads(requests.get(url_all_zones, data=json.dumps(payload), headers=headers).text)
        dynect_zones_uri = res['data']
        for uri in dynect_zones_uri:
            zone = dynect_parser(uri, 'Zone')
            all_records_zone_url = dynect_url + '/REST/AllRecord/' + zone + '/'
            res = json.loads(requests.get(all_records_zone_url, data=json.dumps(payload), headers=headers).text)
            all_records_zone = res['data']
            for record_uri in all_records_zone:
                record_name = dynect_parser(record_uri, zone)
                record_type = dynect_parser(record_uri, 'REST')
                if record_type != 'ARecord':
                    continue
                record_url = dynect_url + record_uri
                res = json.loads(requests.get(record_url, data=json.dumps(payload), headers=headers).text)
                record_detail = res['data']
                record_ip = record_detail['rdata']['address']
                for subnet in dns_details['local_segments']:
                    present_in_subnet = check_ip_in_subnet(record_ip, subnet)
                    if present_in_subnet:
                        break
                records_list.append([zone, record_name, record_type, record_ip, present_in_subnet])
            print(records_list)
            exit(0)
    if 'route53' in dns_details['dns_providers'].keys():
        route53 = dns_details['dns_providers']['route53']

        client = boto3.client(
            'route53',
            aws_access_key_id=route53['access_key'],
            aws_secret_access_key=route53['secret_access_key']
        )
        zones = client.list_hosted_zones()['HostedZones']
        for zone in zones:
            record_sets = client.list_resource_record_sets(HostedZoneId=zone['Id'])['ResourceRecordSets']
            for record in record_sets:
                if record['Type'] != 'A' or 'ResourceRecords' not in record.keys():
                    continue
                for record_value in record['ResourceRecords']:
                    record_ip = record_value['Value']
                    for subnet in dns_details['local_segments']:
                        present_in_subnet = check_ip_in_subnet(record_ip, subnet)
                        if present_in_subnet:
                            break
                    records_list.append([zone['Name'], record['Name'], record['Type'], record_ip, present_in_subnet])
    return records_list


dns_name = str(datetime.now().strftime('%Y%m%d%H%m')) + '_sli_dns_report.csv'
parser = ArgumentParser()
parser.add_argument("-i", "--input", dest="input_file", default='./input.yml',
                    help="Input YML file path", metavar="FILE")
parser.add_argument("-o", "--output",
                    dest="output_file", default=dns_name,
                    help="Output filename")

args = parser.parse_args()

try:
    with open(args.input_file, 'r') as input_file:
        details = yaml.safe_load(input_file)
except yaml.YAMLError as exc:
    print('An error occurred while working with the YAML')
    print(exc)
    exit(1)
except FileNotFoundError as e:
    print('No file under ' + args.input_file + ' was found')
    print(e)
    exit(1)


if __name__ == '__main__':
    records_detailed_list = get_dns(details)
    with open(args.output_file, 'w', newline='') as csv_file:
        write = csv.writer(csv_file)
        write.writerows(records_detailed_list)


