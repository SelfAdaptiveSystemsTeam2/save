import math
import sys
import os
import random
from PIL import Image
from PIL import ImageOps
import numpy as np
import libs.ssim as ssim
import libs.utils as ut
import ctls.mpc as mpccontroller
import ctls.random as randomcontroller
import ctls.bangbang as bangbangcontroller
import ctls.pid as pidcontroller
import ctls.closed_loop as closedloopcontroller
​
import subprocess
​
import tkinter as tk
import time
import sqlite3
def image_to_matrix(path):
    img = Image.open(str(path))
    img = ImageOps.grayscale(img)
    img_data = img.getdata()
    img_tab = np.array(img_data)
    w,h = img.size
    img_mat = np.reshape(img_tab, (h,w))
    return img_mat
​
def compute_ssim(path_a, path_b):
    matrix_a = image_to_matrix(path_a)
    matrix_b = image_to_matrix(path_b)
    return ssim.compute_ssim(matrix_a, matrix_b)
    
def generate_random_configuration():
    # random quality - min or max
    if bool(random.getrandbits(1)):
        quality = 100
    else:
        quality = 1
    # random sharpen - min or max
    if bool(random.getrandbits(1)):
        sharpen = 5
    else:
        sharpen = 0
    # random noise - min or max
    if bool(random.getrandbits(1)):
        noise = 5
    else:
        noise = 0
    # return random choice
    return (quality, sharpen, noise)
​
def encode(i, frame_in, frame_out, quality, sharpen, noise):
    framename = str(i).zfill(8) + '.jpg'
    img_in = frame_in + '/' + framename
    img_out = frame_out + '/' + framename
    # generating os command for conversion
    # sharpen actuator
    if sharpen != 0:
        sharpenstring = ' -sharpen ' + str(sharpen) + ' '
    else:
        sharpenstring = ' '
    # noise actuator
    if noise != 0:
        noisestring = ' -noise ' + str(noise) + ' '
    else:
        noisestring = ' '
    # command setup
    command = 'convert {file_in} -quality {quality} '.format(
            file_in = img_in, quality = quality)
    command += sharpenstring
    command += noisestring
    command += img_out
    # executing conversion
    os.system(command)
    # computing current values of indices
    current_quality = compute_ssim(img_in, img_out)
    current_size = os.path.getsize(img_out)
    return (current_quality, current_size)
​
# -------------------------------------------------------------------
​
def pinginfo(ipadr):
    ip = ipadr
    print( "running......")
    timestamp=str(int(time.time()*1000))
    (status, output) = subprocess.getstatusoutput('sudo ping -c 1 %s'%(ip))
    a=output.split(' ')
    # print(a)
    return a,timestamp
    
​
​
def main(args):
​
    # parsing arguments
    mode = args[1] # identify, mpc
    folder_frame_in = args[2]
    folder_frame_out = args[3]
    folder_results = args[4]
    setpoint_quality = float(args[5])
    setpoint_compression = float(args[6])
    
    # getting frames and opening result file
    path, dirs, files = os.walk(folder_frame_in).__next__()
    frame_count = len(files)
    final_frame = frame_count + 1
    log = open(folder_results + '/results.csv', 'w')
    #update
    ip = "www.youtube.com"
    conn = sqlite3.connect('{}/result.db'.format(folder_results))
    print ("Opened database successfully")
    c = conn.cursor()
    c.execute('''CREATE TABLE result
           (ID INT PRIMARY KEY     NOT NULL,
           quality           TEXT    NOT NULL,
           sharpen            char(50)     NOT NULL,
           noise        CHAR(50),
           ssim         REAL,
           size         CHAR(50));''')
    print ("Table result created successfully")
​
    c.execute('''CREATE TABLE netinfo
           (net           TEXT    NOT NULL,
           icmp_seq            char(50)     NOT NULL,
           ttl       CHAR(50),
           min_avg_max_mdev CHAR(50),
           timest         CHAR(50));''')
    print ("Table netinfo created successfully")
​
    #sys.stdout = log
    if mode == "mpc":
        controller = mpccontroller.initialize_mpc()
    elif mode == "random":
        controller = randomcontroller.RandomController()
    elif mode == "bangbang":
        controller = bangbangcontroller.BangbangController()
    # elif mode == "pid":
    #     controller = pidcontroller.PidController()
    # elif mode == "closed_loop":
    #     controller = closedloopcontroller.ClosedLoopController()
    
    # initial values for actuators
    ctl = np.matrix([[100], [0], [0]])
        
    for i in range(1, final_frame):
        # main loop
        ut.progress(i, final_frame) # display progress bar
​
        quality = np.round(ctl.item(0))
        sharpen = np.round(ctl.item(1))
        noise = np.round(ctl.item(2))
​
        # encoding the current frame
        (current_quality, current_size) = \
            encode(i, folder_frame_in, folder_frame_out, quality, sharpen, noise)
        log_line = '{i}, {quality}, {sharpen}, {noise}, {ssim}, {size}'.format(
            i = i, quality = quality, sharpen = sharpen, noise = noise,
            ssim = current_quality, size = current_size)
        print (log_line , file= log)
​
        a, timestamp = pinginfo(ip)
​
        #update
        c.execute("INSERT INTO result(ID,quality,sharpen,noise,ssim,size) \
      VALUES ('{}','{}','{}','{}','{}','{}')".format(int(i),quality,sharpen,noise,current_quality,current_size))
        
        c.execute("INSERT INTO netinfo(net,icmp_seq,ttl,min_avg_max_mdev,timest) \
      VALUES ('{}','{}','{}','{}','{}')".format(a[1],a[11],a[12],a[30],timestamp))
        conn.commit()
        print ("Records created successfully")
​
​
​
        setpoints = np.matrix([[setpoint_quality], [setpoint_compression]])
        current_outputs = np.matrix([[current_quality], [current_size]])
        
        # computing actuator values for the next frame
        if mode == "mpc":
            try:
                ctl = controller.compute_u(current_outputs, setpoints)
            except Exception:
                pass
    
        elif mode == "random":
            ctl = controller.compute_u()
            
        elif mode == "bangbang":
            ctl = controller.compute_u(current_outputs, setpoints)
        # elif mode == "pid":
        #     try:
        #         ctl = controller.compute_u(current_outputs, setpoints)
        #     except Exception:
        #         pass
        # elif mode == "closed_loop":
        #     try:
        #         ctl = controller.compute_u(current_outputs, setpoints)
        #     except Exception:
        #         pass
​
​
    #update
    conn.close()
​
    print (" done")
​
if __name__ == "__main__":
        # from pycallgraph import PyCallGraph
        # from pycallgraph.output import GraphvizOutput
        # with PyCallGraph(output=GraphvizOutput()):
               main(sys.argv)
