import os
import wave
import numpy as np

def read_wav_data(filename):
    """
    filename: wave文件地址
    读取一个wav文件，转化为矩阵(每两个字节转化为np.short)返回
    """
    if not os.path.isfile(filename):
        print("文件%s不存在" % filename)
        return
    try:
        wav = wave.open(filename, "rb")
        nframe = wav.getnframes()  # 获取帧数
        nchannel = wav.getnchannels()  # 获取声道数
        frame_rate = wav.getframerate()  # 获取帧速率
        sample_width = wav.getsampwidth()  # 获取每一帧的字节数
        str_data = wav.readframes(nframe)  # 获取全部的帧， wav.readframes() 获取多少帧，并进行指针移动

        return np.fromstring(str_data, dtype=np.short)  # 正好每帧转成一个np.short
    except IOError:
        print("读取文件: ", filename, "错误")
    finally:
        wav.close()  # 关闭流


def write_wave(data, dest_path = "wav\\test.wav"):
    """
    向dest_path输出一个wave文件
    data是np.array()类型
    """
    framerate = 16000
    try:
        f = wave.open(dest_path, "wb")
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(data.tostring()) # tostring可以将np.array()转化为bytes
    except IOError:
        print("向: ", dest_path, " 写入数据完毕")
    finally:
        f.close()


def zcr(frames):
    """
    返回这些frames的过零率是多少
    """
    tmp1 = frames[:-1]
    tmp2 = frames[1:]
    sings = (tmp1 * tmp2) <= 0
    diffs = abs(tmp1 - tmp2) > 25  # 防止轻微的抖动

    return np.sum(sings * diffs)


def get_cut_data(data, nums=int(16000 / 100), min_zcr=100):
    """
    通过过零率剪切数据
    nums: 剪切的块数
    min_zcr: 每个块要保留下来，至少需要的过零率
    """
    chunks = np.array_split(data, nums)
    zcrs = np.array(list(map(zcr, chunks)))
    saved = zcrs >= min_zcr
    lst = [chunks[i] for i in range(len(chunks)) if saved[i]]
    res = np.array([], dtype=np.short)
    for chunk in lst:
        res = np.concatenate([res, chunk])

    return res


def cut_and_output(src_path, dest_path, min_zcr):
    wave_array = read_wav_data(src_path)
    cutted = get_cut_data(wave_array, min_zcr)
    write_wave(cutted, dest_path)

def cut_files(src_dir, to_dir, min_zcr):
    files = os.listdir(src_dir)
    for filename in files:
        cut_and_output(src_dir+filename, to_dir+filename, min_zcr)
    print("切割完毕")


# cut_files("E:\\pycharm_space\\ASRwork\\t-wav\\", "E:\\pycharm_space\\ASRwork\\output\\", 150)

dir_path = "E:\\pycharm_space\\ASRwork\\t-wav\\"
cut_and_output(dir_path+"1.wav", dir_path+"cutted.wav", 150)

