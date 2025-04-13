from pypinyin import lazy_pinyin
import asyncio
import subprocess
from datetime import datetime
import os



# 音频输出目录
hzys_output_dir = os.path.join(os.path.dirname(__file__), "wav_output")


def chinese_to_pinyin(text):
    # 使用 lazy_pinyin 获取不带声调的拼音列表
    pinyin_list = lazy_pinyin(text)
    # 将列表中的拼音用空格连接成字符串
    result = ' '.join(pinyin_list)
    return result

async def run_hzys(ori_text):
    # 参考：https://github.com/DSP-8192/HuoZiYinShua
    '''
    :usage: HZYS.exe [-h] [-t TEXT] [-d] [-o OUTPUT] [-f FILE] [-y] [-p PITCHMULT] [-s SPEEDMULT] [-r] [-n]

    :使用程序进行电棍活版印刷

    :options:
    -t TEXT, --text TEXT : 要输出的文字
    -o OUTPUT, --output OUTPUT:  输出音频文件名称，例如./输出.wav         
    -f FILE, --file FILE : 读取的文件名称，例如./输入.txt
    -y, --inYsddMode :     匹配到特定文字时使用原声大碟
    -p PITCHMULT, --pitchMult PITCHMULT: 音调偏移程度，大于1升高音调，小于1降低音调，建议[0.5, 2]
    -s SPEEDMULT, --speedMult SPEEDMULT: 播放速度，大于1加速，小于1减速，建议[0.5, 2]            
    -r, --reverse :        频音的成生放倒
    -n, --norm   :         统一所有字音量
    '''
        # 获取当前时间戳
    current_time = datetime.now()
        # 创建输出目录
    if not os.path.exists(hzys_output_dir):
        os.makedirs(hzys_output_dir)
    # 格式化为字符串，例如：2023-10-05_14_30_00_123456
    current_time_str = current_time.strftime("%Y-%m-%d_%H_%M_%S_%f")
    text = chinese_to_pinyin(ori_text)
    hzys_exe_path = os.path.join(os.path.dirname(__file__), "hzys.exe")
    process = await asyncio.create_subprocess_exec(
        hzys_exe_path,
        '-t', text,  # 输入的文字
        '-o', os.path.join(hzys_output_dir,f"{current_time_str}.wav"), # 输出目录以及文件名
        '-y',               # 使用原声大碟
        '-set', os.path.join(os.path.dirname(__file__), "settings.json"),  # 配置文件路径，默认为同目录下的settings.json
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print(f"Error for text '{ori_text}': {stderr.decode()}")
        return "Error"
    else:
        return current_time_str

async def main():
    # input_text1 = "大家好啊，不可以"
    # input_text2 = "bu shi ni ma e xin ren ni you ge du"
    
    input_t1 = "yuan zi dan"
    input_t2 = "zhu bi ba zhei zen me zhei me cai a"
    
    # 并发运行两个任务
    await asyncio.gather(
        run_hzys(input_t1),
        run_hzys(input_t2)
    )

if __name__ == "__main__":
    asyncio.run(main())


