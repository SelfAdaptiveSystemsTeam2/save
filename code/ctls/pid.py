import numpy as np
import time as times

class PidController:
    global compute_ssim
    global compute_size
    prior_error_ssim = 0
    prior_integral_ssim = 0
    prior_error_size = 0
    prior_integral_size = 0
    sample_time = 0.00
    current_time = times.time()
    last_time = current_time
    current_time2 = times.time()
    last_time2 = current_time2
    ssim_error = 0
    size_error = 0
    qualitys = 0.1
    quality2 = 0.5
    decrease_quality = 0.5
    previous_quality = 0
    previous_sharpness = 0
    previous_noise = 0
    sharpness = 0.5 
    noises = 0.5
    ssim_cond = 2
    max_error = 75000
    max_error2 = 0.3
    max_quality = 100
    max_ssim = 1
    previous_quality1 = 25

    def __init__(self):
        self.quality = 25
        self.sharpen = 5
        self.noise = 5


    def compute_u(self, current_outputs, setpoints):
        if(self.ssim_error != setpoints.item(0)):
            self.ssim_error = compute_ssim(self, current_outputs, setpoints)
            self.size_error = compute_ssim(self, current_outputs, setpoints)
            calculate_quality = self.size_error / self.max_error * self.max_quality
            if(calculate_quality < 0 and calculate_quality > - 100):
                calculate_quality = calculate_quality * -1
                if(self.previous_quality1 - calculate_quality > 0):
                    if(self.previous_quality1 - calculate_quality > 0.5):
                        self.quality = self.previous_quality1 - calculate_quality
                        self.previous_quality1 = self.quality
                elif(self.previous_quality1 - calculate_quality < 0):
                    calculate_quality = calculate_quality - self.previous_quality1
                    if(self.previous_quality1 - calculate_quality > 0.5):
                        self.quality = self.previous_quality1 - calculate_quality
                        self.previous_quality1 = self.quality
            elif(calculate_quality > 0 and calculate_quality < 100):
                self.quality = calculate_quality + self.previous_quality1
                self.previous_quality1 = self.quality
            
            calculate_sharpness = self.ssim_error / self.max_error2 * self.max_ssim

            if(calculate_sharpness < 0 and calculate_sharpness > -1):
                calculate_sharpness = calculate_sharpness * -1
                if(self.previous_sharpness - calculate_sharpness > 0):
                    self.sharpen = self.previous_sharpness - calculate_sharpness
                    self.previous_sharpness = self.sharpen
                elif(self.previous_sharpness - calculate_sharpness < 0):
                    self.sharpen = calculate_sharpness - self.previous_sharpness
                    self.previous_sharpness = self.sharpen
            elif(calculate_sharpness > 0 and calculate_sharpness < 1):
                if(calculate_sharpness + self.previous_sharpness < 5):
                    self.sharpen = calculate_sharpness + self.previous_sharpness
                    self.previous_sharpness = self.sharpen
                elif(calculate_sharpness + self.previous_sharpness > 5):
                    self.sharpen = 5
                    self.previous_sharpness = self.sharpen

            calculate_noise = self.ssim_error / self.max_error2 * self.max_ssim
            if(calculate_noise < 0 and calculate_noise > -1):
                calculate_noise = calculate_noise * -1
                if(self.previous_noise - calculate_noise > 0):
                    self.noise = self.previous_noise - calculate_noise
                    self.previous_noise = self.noise
                elif(self.previous_noise - calculate_noise < 0):
                    self.noise = calculate_noise - self.previous_noise
                    self.previous_noise = self.noise
            elif(calculate_noise > 0 and calculate_noise < 1):
                if(calculate_noise + self.previous_noise < 5):
                    self.noise = calculate_noise + self.previous_noise
                    self.previous_noise = self.noise
                elif(calculate_noise + self.previous_noise > 5):
                    self.noise = 5
                    self.previous_noise = self.noise

        self.ctl = np.matrix([[self.quality], [self.sharpen], [self.noise]])
        return self.ctl

    def compute_ssim(self, current_outputs, setpoints):
        kp_ssim = 0.5
        ki_ssim = 0
        kd_ssim = 0
        self.current_time = times.time()
        time = self.current_time - self.last_time
        error = setpoints.item(0) - current_outputs.item(0)
        integral = self.prior_integral_ssim + error * time
        derivative = error - self.prior_error_ssim / time
        output = (kp_ssim * error)  + (ki_ssim * integral) + (kd_ssim * derivative)
        self.last_time = self.current_time
        self.prior_error_ssim = error
        self.prior_integral_ssim = integral
        return output

    def compute_size(self, current_outputs, setpoints):
        kp_size = 0.52
        ki_size = 0
        kd_size = 0
        self.current_time2 = times.time()
        time = self.current_time2 - self.last_time2
        #print setpoints.item(1)
        #print current_outputs.item(1)
        error = setpoints.item(1) - current_outputs.item(1)
        integral = self.prior_integral_size + error * time
        derivative = error - self.prior_error_size / time
        output = kp_size * error + ki_size * integral + kd_size * derivative

        self.last_time2 = self.current_time2
        self.prior_error_size = error
        self.prior_integral_size = integral

        return output
