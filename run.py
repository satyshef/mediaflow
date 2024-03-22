from datetime import datetime, timedelta
import requests
import json
import os
import random

from airflow import models
from airflow.decorators import task
from airflow.operators.python import PythonOperator
from airflow.hooks.base_hook import BaseHook
from airflow.exceptions import AirflowSkipException


import mediaflow.lib.sender as Sender
import mediaflow.lib.helper as Helper

#MEDIA_SERVER_URL = 'http://81.200.154.127:5000/video'
MEDIA_SERVER_URL = 'http://194.31.175.189:5000/video'
BOT_TOKEN = "6078932856:AAHyPSOhwkUsCFW9Zw5v7y-sInZ2LH5a0sE"
CID = "-1001950662813"
MIN_NEWS_COUNT = 1
NEWS_DIR = "./data/news/"
CONFIG_DIR = "./data/media_config/"
#PROJECT_DIR = "./dags/masa/projects"
DAG_ID = "mediaflow"
INTERVAL = timedelta(minutes=10)
bot = Sender.TelegramWorker(BOT_TOKEN)


# читаем конфигурацию config_name из config_dir для samlpe_name
# формат имени файла конфигурации <sample_name>.<config_name>(.<id>).json
# если <sample_name> есть а <config_name> нет тошда подгружаем  <sample_name>.default.json
def get_media_config(config_dir, sample_name, config_name):
    conf_default_name = 'default'
    conf_ext = 'json'

    if config_dir == '' or config_dir == None:
        return None
    files = Helper.files_in_directory(config_dir, [conf_ext])
    if files == None or len(files)==0:
        return None
    
    random.shuffle(files)

    for file in files:
        file_name = Helper.get_file_name(file)
        s = file_name.split(".")
        if sample_name == s[0]:
            # если есть указанная конфигурация то грузим ее иначе конфу по умолчанию
            if config_name == s[1]:
                config_path = file
            else:
                default = f"{sample_name}.{conf_default_name}.{conf_ext}"
                config_path = os.path.join(config_dir, default)
            config = Helper.read_file_json(config_path)
            if config != None:
                return config
    return None


# если нет конфигурации для указанного семпла то в поле samle указывается имя семпла,
# в таком случае будет применена установленная по умолчанию конфигурация семпла на t2v сервере
def get_news(news_dir, min_news_count, config_dir = ''):
    news_ext = ['txt']
    files = Helper.files_in_directory(news_dir, news_ext)
    if len(files) != 0:
        for file in files:
            #if Helper.get_file_extension(file) == news_ext:
            file_name = Helper.get_file_name(file)
            s = file_name.split(".")
            sample_name = s[0]
            #config_name = s[1]

            data = Helper.read_file_lines(file)
            if data == None:
                continue
            if len(data) < min_news_count:
                continue

            media_config = get_media_config(config_dir, sample_name)
            if media_config == None or 'sample' not in media_config:
                media_config = {
                    'sample': sample_name,
                    'data': data,
                }
            else:
                media_config['data'] = data

            #print(project)
            # Удаляем новостной файл. Проблема в том что если далее возникнит ошибка то пост теряется
            os.remove(file)
            return media_config
        


def __get_news(news_dir):
    news_ext = ['txt']
    files = Helper.files_in_directory(news_dir, news_ext)
    if len(files) != 0:
        for file in files:
            #if Helper.get_file_extension(file) == news_ext:
            file_name = Helper.get_file_name(file)
            s = file_name.split(".")
            project_name = s[0]
            data = Helper.read_file_lines(file)
            if data == None:
                continue
            if len(data) < MIN_NEWS_COUNT:
                continue
            project = {
                'sample': project_name,
                #'file': file,
                'data': data,
            }
            # Удаляем новостной файл. Проблема в том что если далее возникнит ошибка то пост теряется
            os.remove(file)
            return project
        
    print('Empty news file list')
    raise AirflowSkipException

@task.python
def generate_media(news):
    if news == None or len(news['data']) == 0:
        raise ValueError('News not set')
    
    #print("News :::::",news)
    response = requests.post(MEDIA_SERVER_URL, json=news)
    decoded_string = bytes(response.text, 'utf-8').decode('unicode-escape')
    data = json.loads(decoded_string)
    print('data :::::',data)
    if data['success'] == False:
        raise ValueError(data['error'])
        #raise AirflowSkipException
    
    news['url'] = data['url']
    return news
    #return decoded_string['url']

@task.python
def generate_post(news):
    # Проверяем нужно ли отправлять пост
    if 'sender' in news and 'enable' in news['sender'] and news['sender']['enable'] == False:
        raise AirflowSkipException
    
    if isinstance(news.get('sample'), str):
        text = "#%s" % news['sample']
    else:
        text = "#%s" % news['sample']['name']

    text = text.replace('_', '\_')
    post = {
            "text": text,
            "link": "none",
            "foto_link": [],
            "video_link": [news['url']]
    }
    # Удаляем новостной файл. Переделать
    # os.remove(news['file'])
    #print(post)
    return post


@task.python
def send_post(bot, cid, post):
     bot.send_media_post(cid, post)


with models.DAG(
    DAG_ID,
    schedule=INTERVAL,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["masa", "polihoster", "mediaflow"],
) as dag: 
    news = get_news(NEWS_DIR, MIN_NEWS_COUNT, CONFIG_DIR)
    news_full = generate_media(news)
    post = generate_post(news_full)
    send_post(bot, CID, post)
