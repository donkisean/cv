
import csv
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from datetime import datetime


 
def get_data():
    api_id = 1111
    api_hash = ''
    phone = '+7......'
    client = TelegramClient(phone, api_id, api_hash)
    client.start()

    chats = []  # список чатов
    last_date = None
    size_chats = 200  # ограничим максимальное количество получаемых групп
    groups=[]

    result = client(GetDialogsRequest(
      offset_date=last_date,
      offset_id=0,
      offset_peer=InputPeerEmpty(),
      limit=size_chats,
      hash = 0
    ))
    chats.extend(result.chats)

    for chat in chats:
      try:
          if chat.megagroup== True:  # парсер будет работать только с каналами, а не с личными чатами
              groups.append(chat)
      except:
          continue
    
    print('Все группы:')
    i=0
    for g in groups:
      print(str(i) + '- ' + g.title)
      i+=1
    
    target_group=groups[1]  # int(input("Введите нужную цифру: "))
    all_messages = []
    offset_id = 0
    limit = 100  # за каждый цикл работы будет сохраняться только 100 сообщений.
    total_messages = 0  # счётчиком спарсенных сообщений
    total_count_limit = 0

    period = 0
    while True:
      period += 1
      history = client(GetHistoryRequest(
        peer=target_group,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=0,
        hash=0
      ))
      if not history.messages:
        break
      messages = history.messages
      for message in messages:
        print('message', message.to_dict())
        all_messages.append(message.to_dict())
      offset_id = messages[len(messages) - 1].id
      if total_count_limit != 0 and total_messages >= total_count_limit:
        break  # Если нет, то цикл завершается
      if period > 2:
        break

    data = []
    for n in all_messages:
      users_bad = [int(n) for n in open('i/users.txt', 'r').read().splitlines()]
      if n['from_id'] and 'message' in n and n['peer_id']['channel_id'] == 1814210774 and n['from_id']['user_id'] not in users_bad:
        data.append({
          'id': n['id'],
          'user': n['from_id']['user_id'],
          'date': n['date'].strftime('%Y-%m-%d %H:%M'),
          'mess': n['message'],
          'bad': 0,
        })
    print("Сохраняем данные в файл...")
    with open("i/chats.json", "w",  encoding="utf-8") as f:
      f.write(json.dumps(data, indent=2, ensure_ascii=False))

    print("Парсинг сообщений группы успешно выполнен.") #Сообщение об удачном парсинге чата.
  
    