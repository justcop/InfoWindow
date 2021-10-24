#!/usr/bin/env python2

import sys
import os.path
import json
import logging
import string
from datetime import date
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageChops
from mod_infowindow import infowindow

# Select pluggable module for todo list, calendar and weather.
# Replace the mod_<name> with one of:
# TODO: mod_todoist, mod_teamwork
# CALENDAR: mod_google, mod_ical
from mod_utils import iw_utils
from mod_todo import mod_todoist as modTodo  # TODO
from mod_calendar import mod_google as modCalendar  # CALENDAR
from mod_todo import mod_grocy as modGrocy

# TODO: Create dictionaries for API args. so that they can be custom.

# Configuration ###############################################################
config_path = os.path.join(iw_utils.getCWD(), "config.json")
with open(config_path) as config_file:
    config_data = json.load(config_file)

# Rotation. 0 for desktop, 180 for hanging upside down
rotation = config_data["general"]["rotation"]
charset = config_data["general"]["charset"]
todo_opts = config_data["todo"]
grocy_opts = config_data["grocy"]
calendar_opts = config_data["calendar"]
infowindow_opts = {}
# give the timeformat to all the modules needing it
calendar_opts["timeformat"] = config_data["general"]["timeformat"]
infowindow_opts["timeformat"] = config_data["general"]["timeformat"]
infowindow_opts["cell_spacing"] = config_data["general"]["cell_spacing"]

# END CONFIGURATION ###########################################################
###############################################################################

# Setup Logging -  change to logging.DEBUG if you are having issues.
logging.basicConfig(level=logging.DEBUG)
logging.info("Configuration Complete")


# Custom exception handler. Need to handle exceptions and send them to the
# display since this will run headless most of the time. This gives the user
# enough info to know that they need to troubleshoot.
def HandleException(et, val, tb):
    red = infowindow.InfoWindow()
    red.text(0, 10, "EXCEPTION IN PROGRAM", 'robotoBlack18', 'black')
    red.text(0, 30, val.encode(charset).strip(), 'robotoBlack18', 'black')
    red.text(0, 60, "Please run program from command line interactivly to resolve", 'robotoBlack18', 'black')
    print("EXCEPTION IN PROGRAM ==================================")
    print("error message: %s" % val)
    print("type:          %s" % et)
    print("traceback:     %s" % tb)
    print("line:          %s" % tb.lineno)
    print("END EXCEPTION =========================================")
    red.display(rotation)


sys.excepthook = HandleException

# helper to calculate max char width and height
def get_max_char_size(black, chars, font):
    max_x = 0
    max_y = 0
    for char in chars:
        (x, y) = black.getFont(font).getsize(char)
        if x > max_x:
            max_x = x
        if y > max_y:
            max_y = y
    return max_x, max_y

# Main Program ################################################################
def main():
    # Instantiate API modules
    todo = modTodo.ToDo(todo_opts)
    cal = modCalendar.Cal(calendar_opts)
    grocy = modGrocy.test(grocy_opts)

    # Setup e-ink initial drawings
    red = infowindow.InfoWindow(infowindow_opts, "red")
    black = infowindow.InfoWindow(infowindow_opts, "black")

    # Title Line
    black.line(0, 0, 880, 0)  # Top Line
    red.rectangle(1, 1, 880, 24)  # Red Rectangle
    black.line(0, 25, 880, 25)  # Bottom Black Line

    # Titles
    text_width = red.textwidth("CALENDAR", 'robotoBlack24')
    red.text(143 - text_width, 0, "CALENDAR", 'robotoBlack24', 'white')
    text_width = red.textwidth("FRIDGE", 'robotoBlack24')
    red.text(440 - text_width, 0, "FRIDGE", 'robotoBlack24', 'white')
    text_width = red.textwidth("TASKS", 'robotoBlack24')
    red.text(737 - text_width, 0, "TASKS", 'robotoBlack24', 'white')
    
    #Date header
    text_width = red.textwidth(date.today().strftime('%a'), 'robotoBlack18')
    red.text(292 - text_width, 0, date.today().strftime('%a'), 'robotoBlack18', 'white')
    text_width = red.textwidth(date.today().strftime('%-d %b'), 'robotoBlack18')
    red.text(589 - text_width, 0, date.today().strftime('%-d %b'), 'robotoBlack18', 'white')
    logging.info(date.today().strftime('%-d %b'))
    
    # Set some things
    calendar_date_font = "robotoRegular14"
    calendar_entry_font = "robotoBlack18"
    tasks_font = "robotoBlack18"

    # Dividing lines
    black.line(286, 24, 286, 528)  # Left Black line
    red.rectangle(287, 24, 296, 528)  # Red Rectangle
    black.line(297, 24, 297, 528)  # Right Black line

    black.line(583, 24, 583, 528)  # Left Black line
    red.rectangle(584, 24, 593, 528)  # Red Rectangle
    black.line(594, 24, 594, 528)  # Right Black line

    # DISPLAY TODO INFO
    # =========================================================================
    try:
        todo_items = todo.list()
        logging.debug("Todo Items")
        logging.debug("-----------------------------------------------------------------------")

        (t_x, t_y) = red.getFont(tasks_font).getsize('JgGj')
        (t_x, t_y) = get_max_char_size(red, string.printable, tasks_font)
        line_height = t_y + (2 * infowindow_opts["cell_spacing"])

        current_task_y = 25
        for todo_item in todo_items:
            if todo_item['due']:
                caldate = datetime.datetime.strptime(todo_item['due'][0:10], '%Y-%m-%d').date()
            else:
                calcdate = datetime.datetime.now().date()
            if datetime.datetime.now().date() >= caldate:
            
                if 2156103501 in todo_item['labels']:
                    red.text(595, (current_task_y + infowindow_opts["cell_spacing"]), red.truncate(todo_item['content'].encode(charset).strip(), tasks_font, 286), tasks_font)
                    red.line(595, (current_task_y + line_height + 1), 880, (current_task_y + line_height + 1))
                    # set next loop height
                    current_task_y = (current_task_y + line_height + 2)
                    logging.debug("ITEM: %s" % todo_item['content'].encode(charset).strip())
                if todo_item['priority'] > 2:    
                    black.text(595, (current_task_y + infowindow_opts["cell_spacing"]), black.truncate(todo_item['content'].encode(charset).strip(), tasks_font, 286), tasks_font)
                    red.line(595, (current_task_y + line_height + 1), 880, (current_task_y + line_height + 1))
                    # set next loop height
                    current_task_y = (current_task_y + line_height + 2)
                    logging.debug("ITEM: %s" % todo_item['content'].encode(charset).strip())
        

    # DISPLAY GROCY INFO
    # =========================================================================
    try:
      grocy_items = grocy.list()
      logging.debug("Grocy Items")
      logging.debug("-----------------------------------------------------------------------")

      #(t_x, t_y) = red.getFont(tasks_font).getsize('JgGj')
      (t_x, t_y) = get_max_char_size(red, string.printable, tasks_font)
      line_height = t_y + (2 * infowindow_opts["cell_spacing"])

      current_task_y = 25
      for grocy_item in grocy_items:
          (np_x, np_y) = red.getFont(tasks_font).getsize(str(grocy_item['days']) + " ")
          if int(grocy_item['days']) < 3:
              text = red
          else:
              text = black
      
          text.text(298, (current_task_y + infowindow_opts["cell_spacing"]), str(grocy_item['days'] + " "), tasks_font)
          (op_x, op_y) = text.getFont(tasks_font).getsize(black.truncate(grocy_item['content'].encode(charset).strip(), tasks_font, 286 - np_x))
          text.text(583 - op_x, (current_task_y + infowindow_opts["cell_spacing"]), text.truncate(grocy_item['content'].encode(charset).strip(), tasks_font, 286 - np_x), tasks_font)
          red.line(298, (current_task_y + line_height + 1), 582, (current_task_y + line_height + 1))


          # set next loop height
          current_task_y = (current_task_y + line_height + 2)
          logging.debug("ITEM: %s" % grocy_item['content'].encode(charset).strip())
      except:
        logging.debug("Grocy Failed")
        logging.debug("-----------------------------------------------------------------------")
        red.text(298, (25 + infowindow_opts["cell_spacing"]), str("Grocy failed to load"), tasks_font)
        

    # DISPLAY CALENDAR INFO
    # =========================================================================
        cal_items = cal.list()
        logging.debug("Calendar Items")
        logging.debug("-----------------------------------------------------------------------")

        if calendar_opts['timeformat'] == "12h":
            (t_x, t_y) = get_max_char_size(red, string.digits, calendar_date_font)
            (dt_x, dt_y) = black.getFont(calendar_date_font).getsize(': pm')
            dt_x = dt_x + (4 * t_x)
            if t_y > dt_y:
                dt_y = t_y

        else:
            (t_x, t_y) = get_max_char_size(red, string.digits, calendar_date_font)
            (dt_x, dt_y) = black.getFont(calendar_date_font).getsize('.')
            dt_x = dt_x + (4 * t_x)

        (it_x, it_y) = get_max_char_size(red, string.printable, calendar_entry_font)

        line_height = (2 * dt_y) + (2 * infowindow_opts["cell_spacing"])

        current_calendar_y = 26
        for cal_item in cal_items:
            font_color = 'black'
            text = black
            if cal_item['today']:
                text = red
                black.rectangle(0, current_calendar_y,
                         285, (current_calendar_y + line_height),
                         calendar_opts['today_background_color'])

            # draw horizontal line
            red.line(0, (current_calendar_y + line_height + 1),
                285, (current_calendar_y + line_height + 1),
                'black')
            # draw vertical line
            red.line((dt_x + (2 * infowindow_opts["cell_spacing"]) + 1), current_calendar_y,
                (dt_x + (2 * infowindow_opts["cell_spacing"]) + 1), (current_calendar_y + line_height),
                'black')

            # draw event date
            text.text((infowindow_opts["cell_spacing"]),
                (current_calendar_y + infowindow_opts["cell_spacing"]),
                cal_item['caldate'].encode(charset).strip(), calendar_date_font, font_color)
            # draw event time
            text.text((infowindow_opts["cell_spacing"]),
                (current_calendar_y + ((line_height - 2 * infowindow_opts["cell_spacing"]) / 2)),
                cal_item['time'].encode(charset).strip(), calendar_date_font, font_color)
            # draw event text
            calendar_event_text_start = dt_x + (3 * infowindow_opts["cell_spacing"]) + 1
            max_event_text_length = 285 - calendar_event_text_start - infowindow_opts["cell_spacing"]
            text.text(calendar_event_text_start,
                (current_calendar_y + ((line_height - it_y) / 2)),
                black.truncate(cal_item['content'].encode(charset).strip(), calendar_entry_font, max_event_text_length),
                calendar_entry_font, font_color)

            # set new line height for next round
            current_calendar_y = (current_calendar_y + line_height + 2)
            # logging.debug("ITEM: "+str(cal_item['caldate']), str(cal_item['time']), str(cal_item['content']))
            logging.debug("ITEM: %s" % cal_item['content'].encode(charset).strip())

    # Write to screen
    # =========================================================================
    red.image = red.image.rotate(rotation)
    black.image = black.image.rotate(rotation)
    
    new_image_found = 0
    if os.path.exists(red.tmpImagePath):
            old_image = Image.open(red.tmpImagePath)
            diff = ImageChops.difference(red.image, old_image)
            if not diff.getbbox():
                new_image_found += 1
                
    if os.path.exists(black.tmpImagePath):
            old_image = Image.open(black.tmpImagePath)
            diff = ImageChops.difference(black.image, old_image)
            if not diff.getbbox():
                new_image_found += 1

    if new_image_found < 2:      
            logging.info("New information in the image detected. Updating the screen.")
            red.image.save(red.tmpImagePath)
            black.image.save(black.tmpImagePath)
            red.epd.display(black.epd.getbuffer(black.image),red.epd.getbuffer(red.image))
            red.epd.sleep()
    else:
            logging.info("No new information found. Not updating the screen.")
    
if __name__ == '__main__':
    main()
