import lib.helper as Helper
import random
import os
import requests

NEWS_DIR = '/Users/outsider/Source/Docker/airflow/data/news/masa_live_short'
CONFIG_DIR = './config/'
MIN_NEWS_COUNT = 1

# читаем конфигурацию config_name из config_dir для samlpe_name
# формат имени файла конфигурации <sample_name>.<config_name>(.<id>).json
# если <sample_name> есть а <config_name> нет тошда подгружаем  <sample_name>.default.json
def get_sample_config(config_dir, sample_name, config_name):
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

# если нет конфигурации для указанного семпла то данные отправляем без поля config,
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
            config_name = s[1]

            data = Helper.read_file_lines(file)
            if data == None:
                continue
            if len(data) < min_news_count:
                continue

            sample_config = get_sample_config(config_dir, sample_name, config_name)
            if sample_config == None:
                project = {
                    'sample': sample_name,
                    'data': data,
                }
            else:
                project = {
                    'sample': sample_name,
                    'config': sample_config,
                    'data': data,
                }

            #print(project)
            # Удаляем новостной файл. Проблема в том что если далее возникнит ошибка то пост теряется
            #os.remove(file)
            return project
        

def send_to_t2v(data):
    # Замените URL на свой адрес сервера Flask
    #url = 'http://172.17.0.2:5000/video'
    url = 'http://127.0.0.1:5000/video'
    #url = 'http://81.200.154.127:5000/video'

    # Отправляем POST-запрос с данными JSON
    response = requests.post(url, json=data)

    #escaped_string = '\u0414\u0430\u043d\u043d\u044b\u0435 \u0443\u0441\u043f\u0435\u0448\u043d\u043e \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u044b'
    decoded_string = bytes(response.text, 'utf-8').decode('unicode-escape')
    print(decoded_string)
    # Печать ответа от сервера
    #print("Ответ сервера:", response.text)

news = get_news(NEWS_DIR, MIN_NEWS_COUNT, CONFIG_DIR)
send_to_t2v(news)
#print(news)

#files = Helper.files_in_directory('./news')
#print(files)


    # Вывести отсортированный список файлов
#for file in files:
#    print(file)

