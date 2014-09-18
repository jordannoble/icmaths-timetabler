import os, json, binascii
from config import redis
from timetabler import app
from flask import render_template, jsonify, request, send_from_directory
from timetabler.functions import (update_term, update_module_list,
                                  update_all_events, filter_events)


@app.route("/")
def route_index():
  is_mobile = True if "Mobi" in request.headers.get('User-Agent') else False
  current_term = json.loads(redis.get('current_term'))
  season = ('Autumn', 'Spring', 'Summer')[int(current_term[1])-1]
  return render_template('index.html',
                         is_mobile=is_mobile,
                         season=season,
                         year=current_term[0])


@app.route("/update_term")
def route_update_term():
  update_term()


@app.route("/update_module_list")
def route_update_module_list():
  update_module_list()


@app.route("/update_all_events")
def route_update_all_events():
  update_all_events()


@app.route("/module_list")
def route_module_list():
  return jsonify(modules=json.loads(redis.get('module_list')))


@app.route("/ics/<filename>")
def ics(filename):
  try:
    with open('/tmp/' + filename + '.ics'):
      filename += '.ics'
      return send_from_directory(directory='/tmp', filename=filename,
                                 as_attachment=True,
                                 attachment_filename=filename)
  except IOError:
    return 'Expired.'


@app.route("/generate")
def generate():
  filename = binascii.b2a_hex(os.urandom(6))
  titleformat = request.args.get('titleformat')
  categories = request.args.getlist('categories[]')
  module_ids = request.args.getlist('ids[]')
  events = filter_events(module_ids, categories)
  ics = ("BEGIN:VCALENDAR\n"
         "METHOD:PUBLISH\n"
         "VERSION:2.0\n"
         "PRODID:-//Apple Inc.//Mac OS X 10.9.1//EN\n"
         "X-APPLE-CALENDAR-COLOR:#0E61B9\n"
         "X-WR-TIMEZONE:Europe/London\n"
         "CALSCALE:GREGORIAN\n"
         "BEGIN:VTIMEZONE\n"
         "TZID:Europe/London\n"
         "BEGIN:DAYLIGHT\n"
         "TZOFFSETFROM:+0000\n"
         "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU\n"
         "DTSTART:19810329T010000\n"
         "TZNAME:BST\n"
         "TZOFFSETTO:+0100\n"
         "END:DAYLIGHT\n"
         "BEGIN:STANDARD\n"
         "TZOFFSETFROM:+0100\n"
         "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU\n"
         "DTSTART:19961027T020000\n"
         "TZNAME:GMT\n"
         "TZOFFSETTO:+0000\n"
         "END:STANDARD\n"
         "END:VTIMEZONE\n")
  with open('/tmp/' + filename + '.ics', 'w') as f:
      for event in events:
          year = event['week'][6:]
          month = event['week'][3:5]
          day = str(int(event['week'][0:2]) + int(event['day'])).zfill(2)
          date = ''.join([year, month, day])
          starttime = event['starttime'].replace(':', '') + "00"
          endtime = event['endtime'].replace(':', '') + "00"
          ics += "".join(["BEGIN:VEVENT\n",
                          "SUMMARY:",
                          titleformat.format(code=event['code'],
                                             name=event['name'],
                                             type=event['type']),
                          "\nDTSTART;TZID=Europe/London:",
                          date,
                          "T",
                          starttime,
                          "\nDTEND;TZID=Europe/London:",
                          date,
                          "T",
                          endtime,
                          "\nLOCATION:",
                          event['room'],
                          "\nEND:VEVENT\n"])
      ics += "END:VCALENDAR"
      f.write(ics)
  return jsonify(filename=filename)
