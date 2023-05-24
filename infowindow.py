#!/usr/bin/env python3

import sys
import os.path
import json
import logging
import string
import datetime
from datetime import date
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageChops
from mod_infowindow import infowindow
from mod_utils import iw_utils
from mod_todo import mod_todoist as modTodo 

# Configuration ###############################################################
config_path = os.path.join(iw_utils.getCWD(), "config.json")
with open(config_path) as config_file:
    config_data = json.load(config_file)

# Rotation. 0 for desktop, 180 for hanging upside down
rotation = config_data["general"]["rotation"]
charset = config_data["general"]["charset"]
todo_opts = config_data["todo"]
infowindow_opts = {}
# give the timeformat to all the modules needing it
infowindow_opts["timeformat"] = config_data["general"]["timeformat"]
infowindow_opts["cell_spacing"] = config_data["general"]["cell_spacing"]

# Define column properties
column_properties = {
    1: {'name': 'Tasks', 'x_start': 1, 'x_end': 286},
    2: {'name': 'Decisions', 'x_start': 298, 'x_end': 583},
    3: {'name': 'Food', 'x_start': 595, 'x_end': 880},
}
initial_y = 25
next_task_y = {1: initial_y, 2: initial_y, 3: initial_y}
current_task_X = 0
current_task_Xend = 0
current_task_y = 0
column = 0
line_height = 0

# END CONFIGURATION ###########################################################
###############################################################################

# Setup Logging -  change to logging.DEBUG if you are having issues.
logging.basicConfig(level=logging.DEBUG)
logging.info("Configuration Complete")


# helper to calculate max char width and height
def get_max_char_size(black, chars, font):
    max_x = 0
    max_y = 0
    for char in chars:
        bbox = black.getFont(font).getbbox(char)  # Get the bounding box of the character
        x, y = bbox[2], bbox[3]  # Extract the width and height from the bounding box
        if x > max_x:
            max_x = x
        if y > max_y:
            max_y = y
    return max_x, max_y

def set_column(Set_Column):
    global current_task_X, current_task_Xend, current_task_y, next_task_y, line_height, column
    
    column = Set_Column    
    # Set the current_task_X and current_task_Xend based on the column input
    current_task_X = column_properties[column]['x_start']
    current_task_Xend = column_properties[column]['x_end']
    
    # Set the current_task_y for the specified column and update next_task_y for that column
    current_task_y = next_task_y[column]
    next_task_y[column] += line_height + infowindow_opts["cell_spacing"]
    
    
# Main Program ################################################################
def main():
    global column_properties, current_task_X, current_task_Xend, current_task_y, next_task_y, line_height, column
    
    # Set fonts
    title_font = "robotoBlack24"
    date_font = "robotoBlack18"
    tasks_font = "robotoBlack18"
    
    # Instantiate API modules
    todo = modTodo.ToDo(todo_opts)

    # Setup e-ink initial drawings
    red = infowindow.InfoWindow(infowindow_opts, "red")
    black = infowindow.InfoWindow(infowindow_opts, "black")

    # Title Line
    black.line(0, 0, 880, 0)  # Top Line
    red.rectangle(1, 1, 880, 24)  # Red Rectangle
    black.line(0, 25, 880, 25)  # Bottom Black Line

    # Titles
    for column, properties in column_properties.items():
      name_upper = properties['name'].upper()
      text_width = red.textwidth(name_upper, title_font)
      x_center = (properties['x_start'] + properties['x_end']) // 2
      red.text(x_center - text_width/2, 0, name_upper, title_font, 'white')

    #Date header
    text_width = red.textwidth(date.today().strftime('%a'), date_font)
    red.text(292 - text_width/2, 0, date.today().strftime('%a'), date_font, 'white')
    text_width = red.textwidth(date.today().strftime('%-d %b'), date_font)
    red.text(589 - text_width/2, 0, date.today().strftime('%-d %b'), date_font, 'white')
    logging.info(date.today().strftime('%-d %b'))

    # Dividing lines
    black.line(286, 24, 286, 528)  # Left Black line
    red.rectangle(287, 24, 296, 528)  # Red Rectangle
    black.line(297, 24, 297, 528)  # Right Black line

    black.line(583, 24, 583, 528)  # Left Black line
    red.rectangle(584, 24, 593, 528)  # Red Rectangle
    black.line(594, 24, 594, 528)  # Right Black line

    # DISPLAY TODO INFO
    # =========================================================================
    todo_items = todo.list()
    logging.debug("Todo Items")
    logging.debug("-----------------------------------------------------------------------")
    
    (t_x, t_y) = get_max_char_size(red, string.printable, tasks_font)
    line_height = t_y + (2 * infowindow_opts["cell_spacing"])

    for todo_item in todo_items:
            
            column = 0
            colour = black
            if todo_item['due']:
              todo_date = datetime.datetime.fromisoformat(todo_item['due']).date()
            else:
              todo_date = False
            todo_days = (todo_date - date.today()).days
            
            
            if todo_item['project_name'] == 'Food':        
              set_column(3)
              
              if "Freezer" in todo_item['labels']:  
                colour = "black"
              else:
                colour = "red"              

            if "To_Decide" in todo_item['labels']:
                set_column(2)
                if int(todo_days) < 3:
                  colour = "red"
                  
            if "Charlotte" in todo_item['labels']:
                set_column(1)
                colour = "red"
                if int(todo_days) > 3:
                    continue
                
            if "Joint" in todo_item['labels']:
                set_column(1)
                colour = "black"
                if int(todo_days) > 3:
                    continue

            
            if column:
                
                if column:
                    # Set the start and end positions of the column space
                    column_width = current_task_Xend - current_task_X
                    
                    # Get the number of days until the task is due
                   
                    number_text = str(todo_days) + " "
                    number_length = colour.textwidth(number_text, tasks_font)
                    
                    # Truncate the task content to fit within the column space
                    text = colour.truncate(todo_item['content'].strip(), tasks_font, column_width - number_length)
                    text_length = colour.textwidth(text, tasks_font)
                    
                    # Calculate the position to right-align the task content within the column space
                    content_x = current_task_Xend - text_length

                    # Draw the number of days and task content
                    colour.text(current_task_X, (current_task_y + infowindow_opts["cell_spacing"]), number_text, tasks_font)
                    colour.rtext(content_x, (current_task_y + infowindow_opts["cell_spacing"]), text, tasks_font)
                    
                    # Draw a horizontal line to separate the tasks
                    red.line(current_task_X, (current_task_y + line_height + 1), (current_task_Xend-1), (current_task_y + line_height + 1))
                    
                    if colour == "red":                  
                        logging.debug(f"\033[91m{column_properties[column]['name']}:{todo_item['content'].strip()}\033[0m")
                    else:
                        logging.debug(f"{column_properties[column]['name']}:{todo_item['content'].strip()}")

    # Write to screen
    # =========================================================================
    red.image = red.image.rotate(rotation)
    black.image = black.image.rotate(rotation)

    new_image_found = 2
    if os.path.exists(red.tmpImagePath):
            old_image = Image.open(red.tmpImagePath)
            diff = ImageChops.difference(red.image, old_image)
            if not diff.getbbox():
                new_image_found -= 1

    if os.path.exists(black.tmpImagePath):
            old_image = Image.open(black.tmpImagePath)
            diff = ImageChops.difference(black.image, old_image)
            if not diff.getbbox():
                new_image_found -= 1

    if new_image_found:
            logging.info("New information in the image detected. Updating the screen.")
            red.image.save(red.tmpImagePath)
            black.image.save(black.tmpImagePath)
            red.epd.display(black.epd.getbuffer(black.image),red.epd.getbuffer(red.image))
            red.epd.sleep()
    else:
            logging.info("No new information found. Not updating the screen.")

if __name__ == '__main__':
    main()
