import os
import wave
import numpy as np
import pylab as pl

sep = os.sep



def read_wave(path):
    dir_path = "E:"+sep+"pycharm_space"+sep+"ASRwork"+sep+"wav"+sep
    try:
        f = wave.open(dir_path+path, "rb")
        nchannels, sampwidth, framerate, nframes = f.getparams()[:4]
        print(nchannels, sampwidth, framerate, nframes)

        # 读取波形数据(里面全是字节(nframes * sampwidth个))
        str_data = f.readframes(nframes)

        # 将波形数据转化为数组
        wave_data = np.fromstring(str_data, dtype=np.short)

        print(wave_data[:1000])

    except IOError:
        print("读取文件出错")
    finally:
        f.close()

read_wave("17.wav")