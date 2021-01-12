import numpy as np;

class ClosedLoopController:
        increase_quality=0.5
        decrease_quality=0.5
        previous_quality=0
        sharpness=0.5
        noises=0.5
        image_quality=0
        ssim_cond=2
        max_error_rate=75000
        max_quality=100
        once=2
	def __init__(self):
		self.quality = 25
		self.sharpen = 5
		self.noise = 5

	def compute_u(self, current_outputs, setpoints):	
		error_rate_size=setpoints.item(1)-current_outputs.item(1)
		error_rate_ssim=setpoints.item(0)-current_outputs.item(0)
                if(self.once>0):
                        
                        if(setpoints.item(1)<20000):
                                if(current_outputs.item(1)>20000):
                                        self.quality= self.quality/2
                        elif(setpoints.item(1)>=20000):
                                if(current_outputs.item(1)<20000):
                                        self.quality=self.quality*1.3
                                elif(current_outputs.item(1)>25000):
                                        self.quality= self.quality/2
                        self.once=self.once-1
                
		if(self.ssim_cond==2):
                        if (error_rate_size<0): # negative value
                                if(self.quality>0.75):
                                        self.quality=self.quality-self.decrease_quality
                                        self.previous_quality=self.quality
                        elif(error_rate_size>0): # positive value
                                self.quality=self.quality+self.increase_quality
                                self.previous_quality=self.quality
                        if(error_rate_size<2000 and error_rate_size>-2000):
                                self.ssim_cond=1
                if(self.ssim_cond!=2):
                        if (error_rate_ssim<0): # negative value
                                if (self.sharpen!=0):
                                        self.sharpen=self.sharpen-self.sharpness
                                if (self.noise!=5):
                                        self.noise=self.noise-self.noises
                                if (error_rate_size>0 and error_rate_size<2000):
                                        self.quality=self.quality-self.decrease_quality
                                        self.previous_quality=self.quality
                        elif(error_rate_ssim>0): # positive value
                                if (self.sharpen!=5):
                                        self.sharpen=self.sharpen+self.sharpness
                                if (self.noise!=0):
                                        self.noise=self.noise+self.noises
                                if (error_rate_size<0 and error_rate_size >-2000):
                                        self.quality=self.quality+self.increase_quality
                                        self.previous_quality=self.quality
                        if(error_rate_size>2000 or error_rate_size<-2000):
                                self.ssim_cond=2
	
		self.ctl = np.matrix([[self.quality], [self.sharpen], [self.noise]])
		return self.ctl
	