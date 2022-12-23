from datetime import datetime


def time_generator(time_stop: datetime, time_start: datetime) -> str:
    time = str(time_stop - time_start).split(".")[0]
    time = time.split(", ")
    if len(time) > 1:
        time = [int(time[0].split(" ")[0]), int(time[1].split(":")[0]), int(time[1].split(":")[1])]
    else:
        time = [0, int(time[0].split(":")[0]), int(time[0].split(":")[1])]
    
    if time[0] == 0: time[0] = ""
    elif int(str(time[0])[-1]) == 1: time[0] = f"{time[0]} день" 
    elif int(str(time[0])[-1]) > 1 and int(str(time[0])[-1]) < 5: time[0] = f"{time[0]} дня"
    else: time[0] = f"{time[0]} дней"
    
    if time[1] == 0: time[1] = ""
    elif int(str(time[1])[-1]) == 1: time[1] = f" {time[1]} час" 
    elif int(str(time[1])[-1]) > 1 and int(str(time[1])[-1]) < 5: time[1] = f" {time[1]} часа"
    else: time[1] = f" {time[1]} часов"
    
    if time[2] == 0: time[2] = ""
    elif int(str(time[2])[-1]) == 1: time[2] = f" {time[2]} минута" 
    elif int(str(time[2])[-1]) > 1 and int(str(time[2])[-1]) < 5: time[2] = f" {time[2]} минуты"
    else: time[2] = f" {time[2]} минут"
    
    return "".join(time) if "".join(time).replace(" ", "") != "" else " 0 минут"