import requests, json, re
import xml.etree.ElementTree as ET
from config import redis
from datetime import date


def form_tt_url(year, term):
  root_url = 'http://www2.imperial.ac.uk/~csisson/'
  return ''.join((root_url, str(year)[-2:], '/', str(term), '/fnd/'))


def get_current_term():
  year = date.today().year
  years = (year - 1, year, year, year, year + 1)
  terms = (3, 1, 2, 3, 1)
  yts = zip(years, terms)
  status_codes = [requests.get(form_tt_url(*yt)).status_code for yt in yts]
  current_term = yts[len(status_codes) - status_codes[::-1].index(200) - 1]
  return current_term


def get_tt_url():
  return form_tt_url(*json.loads(redis.get('current_term')))


def root_from_url(url):
  try:
    return ET.fromstring(requests.get(url).content)
  except ET.ParseError:
    print 'Could not parse ' + url


def update_term():
    current_term = json.dumps(get_current_term())
    try:
      redis.set('current_term', current_term)
    except:
      print 'Failed to update current_term'


def update_module_list():
    root = root_from_url(get_tt_url() + 'finder.xml')
    modules = root.findall(".//resource[@type='module']")
    module_list = []
    for module in modules:
      module_name = module.find('name').text
      if re.match("^M[12345][^0-9]", module_name):
        module_name_split = module_name.split(" - ")
        module_list.append(dict(code=module_name_split[0],
                                name=module_name_split[1],
                                id='m' + module.get('id')))
    try:
      redis.set('module_list', json.dumps(module_list))
    except:
      print 'Failed to update module_list.'


def get_room(event):
  try:
      room = event.find('.//room/item/a').text
  except AttributeError:
    try:
      room = event.find('.//notes').text
    except AttributeError:
      room = ''
  return room


def update_events_by_id(module_id):
  root = root_from_url(get_tt_url() + module_id + '.xml')
  title_split = root.find(".//subheading").text.split(" - ")
  module_code = title_split[1]
  module_name = title_split[2]
  events = root.findall(".//event")
  event_list = []
  for event in events:
    event_list.append(dict(name=module_name,
                           code=module_code,
                           type=event.find('category').text,
                           starttime=event.find('starttime').text,
                           endtime=event.find('endtime').text,
                           week=event.get('date'),
                           day=event.find('day').text,
                           room=get_room(event)))
  try:
    redis.set(module_id, json.dumps(event_list))
  except:
    print ''.join(['Failed to update events for module ', module_id, '.'])


def update_all_events():
  module_ids = [m['id'] for m in json.loads(redis.get('module_list'))]
  for module_id in module_ids:
    update_events_by_id(module_id)


# def update_staff_list():
#     root = root_from_url(get_tt_url() + 'finder.xml')
#     staff = root.findall(".//resource[@type='staff']")
#     staff_list = []
#     for s in staff:
#       staff_name = s.find('name').text
#       staff_list.append(dict(name=staff_name,
#                              id=s.get('id')))
#     try:
#       redis.set('staff_list', json.dumps(staff_list))
#     except:
#       print 'Failed to update staff_list.'


# def update_events_by_staff(staff_id):
#   root = root_from_url(get_tt_url() + 's' + staff_id + '.xml')
#   events = root.findall(".//event")
#   event_list = []
#   for event in events:
#     title_split = event.find('.//module/item/a').text.split(" - ")
#     module_code = title_split[0]
#     module_name = title_split[1]
#     event_list.append(dict(name=module_name,
#                            code=module_code,
#                            type=event.find('category').text,
#                            starttime=event.find('starttime').text,
#                            endtime=event.find('endtime').text,
#                            week=event.get('date'),
#                            day=event.find('day').text,
#                            room=get_room(event)))
#   print event_list
#   try:
#     redis.set(staff_id, json.dumps(event_list))
#   except:
#     print ''.join(['Failed to update events for ', staff_id, '.'])


def update_all():
  print 'Updating term...',
  update_term()
  print 'Updated.'
  print 'Updating module list...',
  update_module_list()
  print 'Updated.'
  print 'Updating events...',
  update_all_events()
  print 'Updated.'


def filter_events(module_ids, categories):
  filtered_events = []
  all_events = redis.mget(module_ids)
  for events in all_events:
    for event in json.loads(events):
      if event['type'] in categories or "Other" in categories:
        filtered_events.append(event)
  return filtered_events


# def delete_old_modules():
#   module_ids = [m['id'] for m in json.loads(redis.get('module_list'))]
#   redis_keys = redis.keys()
#   for key in redis_keys:
#     if key not in module_ids and re.match("^m[^0-9]*", key):
#       redis.delete(key)
