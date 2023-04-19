import hashlib
import re
import urllib.parse
import time
from datetime import datetime, timedelta
import requests
import json

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from pika.spec import BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from pika.spec import BasicProperties
from server import channel
from functions.models import RawLog,CleanLog
from http.client import responses
from .orm_conn import CreateEngine



def process_raw_message(chan: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    
    con = CreateEngine()
    
    body = body.decode("utf-8")
    regex = re.compile(r"(?P<session>\S{1}|\S{15}) (?P<user>\S{1,50})")
    
    if get_match(regex, body) != None:
        if get_user(get_match(regex, body)) != "-" and get_session(get_match(regex, body)) != "-":
            
            
            row_logs = RawLog(id= get_hash_body(body), timestamp=get_datetime(body), log=get_log(body))
            con.add(row_logs)
            con.commit()
            print("Data inserted !")

            print(
                f"[{method.routing_key}] event consumed from exchange `{method.exchange}` body `{body}`")
        
        else:
            print("ignored")
    else:
        print("ignored")

def process_msg_data_clean(chan: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    
    con = CreateEngine()
    
    body = body.decode("utf-8")
    regex = re.compile(r"(?P<ip>\S{7,15}) (?P<session>\S{1}|\S{15}) (?P<user>\S{1,50}) \[(?P<timestamp>\S{20}) "
                r"(?P<utc>\S{5})\] \"(?P<method>GET|POST|DELETE|PATCH|PUT) (?P<url>\S{1,4096}) "
                r"(?P<version>\S{1,10})\" (?P<status>\d{3}) (?P<size>\d+) -")
    match = match_regex(regex, body)
    if match != None:   
        if get_user(match) != None or get_session(match) != None:
            
            clean_logs = CleanLog(id=get_id(body),timestamp=get_timestamp(match), year=get_year(match), month=get_month(match), day=get_day(match), day_of_week=get_day_of_week(match), time=get_time(match), ip=get_ip_adress(match), country=get_country(get_ip_adress(match)), city=get_city(get_ip_adress(match)), session=get_session(match), user=get_user(match), is_email=is_email(get_user(match)), email_domain=get_email_domain(get_user(match)),
                                rest_method=get_rest_method(match), url=get_url(match), schema=get_schema(get_url(match)), host=get_host(get_url(match)), status=get_status(match), status_verbose=get_status_verbose(match), size_bytes=get_size(match), size_kilo_bytes=get_size_kb(get_size(match)), size_mega_bytes=get_size_mb(get_size(match)))
            con.add(clean_logs)
            con.commit()
            print("Data inserted !")

            print(
                f"[{method.routing_key}] event consumed from exchange `{method.exchange}` body `{body}`")
            time.sleep(0.01)

        else:
            print("ignored")
    else:
        print("ignored")
    



def match_regex(regex, body):
    match = re.search(regex, body)
    if match:
        return match
    else:
        return None

###
def get_log(body):
    log = body
    log = log.replace('-', "")
    log = log.replace('"', "")
    return log

def get_datetime(body):
    regex = r"\[.*?\]"
    datetime = re.findall(regex, body)
    datetime = datetime[0].replace("[", "").replace("]", "")
    return datetime

def get_hash_body(body):
    hash_body = hashlib.md5(body.encode()).hexdigest()
    return hash_body    

def get_match(regex, body):
        match = re.search(regex, body)
        if match:
            return match
        else:
            return None

def get_user(match):
    user = match.group("user")
    if user == "-":
        return None
    return user

def get_session(match):
    session = match.group("session")
    
    if session == "-":
        return None
    return session


def get_id(body):
            id = hashlib.md5(body.encode()).hexdigest()
            return id


def get_timestamp(match):
    timestamp = match.group("timestamp")
    format = "%d/%b/%Y:%H:%M:%S"
    date_time = datetime.strptime(timestamp, format)
    date_time = date_time + timedelta(hours=5)
    return date_time

def get_year(match):
    date_time = get_timestamp(match)
    year = date_time.strftime("%Y")
    return year

def get_month(match):
    date_time = get_timestamp(match)
    month = date_time.strftime("%m")
    return month

def get_day(match):
    date_time = get_timestamp(match)
    day = date_time.strftime("%d")
    return day

def get_day_of_week(match):
    date_time = get_timestamp(match)
    day_of_week = date_time.strftime("%A")
    return day_of_week

def get_time(match):
    date_time = get_timestamp(match)
    time = date_time.strftime("%H:%M:%S")
    return time

def get_ip_adress(match):
    ip_matches = match.group("ip")
    return ip_matches

def get_country(ip_matches):
    url = f'http://ip-api.com/json/{ip_matches}'
    try:
        response = requests.get(url)
        data = json.loads(response.content.decode('utf-8'))
        country = data['country']
        return country
    except Exception as e:
        return None

def get_city(ip_matches):
    url = f'http://ip-api.com/json/{ip_matches}'
    try:
        response = requests.get(url)
        data = json.loads(response.content.decode('utf-8'))
        city = data['city']
        return city
    except Exception as e:
        return None

def get_session(match):
    session = match.group("session")
    if session == "-":
        return "None"
    else:
        return session

def get_user(match):
    user = match.group("user")
    if user == "-":
        return "None"
    else:
        return user

def get_email_domain(user):
    if len(re.findall(r'((?<=@)[^.]+(?=\.)+.+)', user)) > 0:
        email_domain = re.findall(r'((?<=@)[^.]+(?=\.)+.+)', user)
        return email_domain
    else:
        return None
    
def is_email(user):
    if get_email_domain(user) != None:
        return "True"
    else:
        return "False"

def get_rest_method(match):
    rest_method = match.group("method")
    return rest_method

def get_url(match):
    url = match.group("url")
    return url

def get_schema(url):
    schema = urllib.parse.urlsplit(url).scheme
    return schema

def get_host(url):
    host = urllib.parse.urlsplit(url).hostname
    return host

def get_version(match):
    version = match.group("version")
    return version

def get_status(match):
    status = match.group("status")
    return status

def get_status_verbose(match):
    status = match.group("status")
    status_verbose = responses[int(status)] if int(
        status) in responses else None
    return status_verbose

def get_size(match):
    size = match.group("size")
    return size

def get_size_kb(size):
    size_kb = int(size) / 1024
    return size_kb

def get_size_mb(size):
    size_mb = int(size) / 1024 / 1024
    return size_mb