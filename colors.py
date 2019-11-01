from cal_setup import get_calendar_service

# https://developers.google.com/calendar/v3/reference/events
TIMEZONE = 'Europe/Madrid'
CALENDAR = '0nv7r8l3d0h9vp2av45nudjj5s@group.calendar.google.com'


service = get_calendar_service()

colors = service.colors().get().execute()

print('<!DOCTYPE html><html><head><title>Google Calendar Colors</title></head>')
print('<body><h1>Calendar colors</h1><ul>')

# Print available calendarListEntry colors.
for id, color in colors['calendar'].items():
  print('<li><font color="{}">colorId: {} ({})</font>'.format(color['background'], id, color['background']))

print('</ul><h1>Event colors</h1><ul>')

# Print available event colors.
for id, color in colors['event'].items():
  print('<li><font color="{}">colorId: {} ({})</font>'.format(color['background'], id, color['background']))

print('</ul></body></html>')
