import lib.helper as Helper
import random
import os
import requests

NEWS_DIR = '/Users/outsider/Source/Docker/airflow/data/news/masa_live_short'
CONFIG_DIR = './config_example/'
MIN_NEWS_COUNT = 1

# читаем конфигурацию из config_dir для samlpe_name
# формат имени файла конфигурации <sample_name>(.<id>).json
def get_media_config(config_dir, sample_name):
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
        # если есть указанная конфигурация то грузим 
        if sample_name == s[0]:    
            config = Helper.read_file_json(file)
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
            #os.remove(file)
            return media_config
        

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


#config = get_media_config(CONFIG_DIR, 'short_news')
#print(config)

news = get_news(NEWS_DIR, MIN_NEWS_COUNT, CONFIG_DIR)
print(news)
send_to_t2v(news)


#config = Helper.read_file_json("/Users/outsider/Source/Docker/airflow/dags/mediaflow/config_example/short_news.default.json")
#print(config['sender'])

#files = Helper.files_in_directory('./news')
#print(files)


    # Вывести отсортированный список файлов
#for file in files:
#    print(file)

