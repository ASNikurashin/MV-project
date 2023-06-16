import numpy as np
import time
from modules import functions


class Frame_processing:
    def __init__(self, settings):
        self.convert_scale = settings['CONVERT_SCALE']
    
    def run(self, frame, data):         
        return data
