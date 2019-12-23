import wave
import numpy as np
import contextlib
import os

def read_wave(path):
    """
    :param path:音频文件路径
    :return: 音频数据(short一维矩阵), 采样率
    """
    with contextlib.closing(wave.open(path, "rb")) as f:
        n_channels = f.getnchannels() # 通道数
        assert n_channels == 1
        sample_width = f.getsampwidth() # 样本宽度
        assert sample_width == 2
        frame_rate = f.getframerate() # 采样率
        assert frame_rate == 16000
        n_frames = f.getnframes() # 总共帧数
        pcm_data = f.readframes(n_frames) # 全部的音频数据(字节形式)
        wave_array = np.fromstring(pcm_data, dtype=np.short) # 每帧一个np.short

        return wave_array


def write_wave(wave_array, dest_path):
    """
    :param wave_array: 音频数据，矩阵形式
    :param dest_path: 目标路径
    :return:
    """
    with contextlib.closing(wave.open(dest_path, "wb")) as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(wave_array.tostring()) # tostring()可以将np.array转化为字节形式


def zcr(frames, min_amp=20):
    """
    计算 average zero cross rate
    :param frames:
    :param min_amp: 最小幅度值(防止轻微的抖动)
    :return:
    """
    tmp1 = frames[:-1]
    tmp2 = frames[1:]
    center = int(np.mean(frames)) # 计算平均值
    # sings = (tmp1 * tmp2) - center <= 0
    sings = (tmp1-center)*(tmp2-center) <= 0
    diffs = abs(tmp1 - tmp2) > min_amp

    return np.sum(sings * diffs)


def ste(frames):
    """
    short time energy
    :param frames:
    :return:
    """
    return np.sum(np.abs(frames))


def get_cutted_array(wave_array, chunk_size, min_zcr, min_ste):
    """
    :param wave_array: 音频数据，矩阵形式
    :param chunk_size: 每一块的帧数
    :param min_zcr: 最小的zcr值
    :param min_ste: 最小的能量幅度值(每一帧的) (经经验判断, 每一帧能量值至少会有150)
    :return: 被切割后，组装起来的wave_array
    """
    n_chunk = int(len(wave_array) / chunk_size)
    chunks = np.array_split(wave_array, n_chunk)
    zcrs = np.array(list(map(zcr, chunks)))
    print("该声音平均zcr(每chunk): ", np.mean(zcrs))
    stes = np.array(list(map(ste, chunks)))
    print("该声音平均ste(每chunk): ", np.mean(stes) / 160)
    print("min_ste: ", min_ste)
    saved = (zcrs >= min_zcr) * (stes >= min_ste)
    lst = [chunks[i] for i in range(n_chunk) if saved[i]]
    res = np.array([], dtype=np.short)
    for chunk in lst:
        res = np.concatenate([res, chunk])

    return res


def cut_and_output(src_path, dest_path, chunk_size, min_zcr, min_ste):
    wave_array = read_wave(src_path)
    cutted = get_cutted_array(wave_array, chunk_size, min_zcr, min_ste)
    write_wave(cutted, dest_path)
    print("切割后占切割前: {}%".format(len(cutted) / len(wave_array) * 100))


def cut_files(src_dir, dest_dir, chunk_size, min_zcr, min_ste):
    files = os.listdir(src_dir)
    for file in files:
        print(src_dir + file)
        cut_and_output(src_dir+file, dest_dir+file, chunk_size, min_zcr, min_ste)
    print("切割完毕")


chunk_size = 160
min_zcr = 30
min_ste = 200
dir_path = "E:\\pycharm_space\\ASRwork\\VAD\\"
# cut_and_output(dir_path+"2.wav", dir_path+"cutted.wav", chunk_size, min_zcr, min_ste)
#
# cut_files("E:\\pycharm_space\\ASRwork\\t-wav\\", "E:\\pycharm_space\\ASRwork\\output\\",
#           chunk_size, min_zcr, min_ste)


cut_and_output(R"E:\pycharm_space\ASRwork\t-wav\T11_009.wav", dir_path+"cutted.wav", chunk_size, min_zcr, min_ste)