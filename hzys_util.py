from pypinyin import lazy_pinyin,load_phrases_dict
import asyncio
import subprocess
from datetime import datetime
import os
from Pinyin2Hanzi import DefaultDagParams, dag,simplify_pinyin
import json
import re


settings_path =  os.path.join(os.path.dirname(__file__), "settings.json")
# 音频输出目录
hzys_output_dir = os.path.join(os.path.dirname(__file__), "wav_output")

with open(settings_path ,"r", encoding="utf-8") as f:
    settings_hzys = json.load(f)
    ysddTable_path = settings_hzys["ysddTableFile"]

with open(ysddTable_path , "r", encoding="utf-8") as f:
    ysddTable = json.load(f)

# 自定义词组的拼音
load_phrases_dict({'好恶心啊': [['hao'],['ě'], ['xin'],['a']], '谁': [['shéi']]})

def chinese_to_pinyin(text):
    # 使用 lazy_pinyin 获取不带声调的拼音列表
    pinyin_list = lazy_pinyin(text)
    # 将列表中的拼音用空格连接成字符串
    result = ' '.join(pinyin_list)
    return result

def pinyin_2_hanzi(pinyin_list):
    dag_params = DefaultDagParams()
    # 规范化拼音
    simplified_pinyin_list = [simplify_pinyin(pinyin) for pinyin in pinyin_list]
    result = dag(dag_params, simplified_pinyin_list, path_num=10, log=True)
    if result:
        return ''.join(result[0].path)  # 返回第一个路径的字符串
    return ''  # 如果没有匹配到，返回空字符串

def py2hanzi(pinyin_text,ori_text):
    # 创建一个正则表达式模式来匹配所有字典中的关键词
    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in ysddTable.keys()) + r')\b')
    
    # 使用正则表达式分割字符串
    parts = pattern.split(pinyin_text)
    matches = pattern.findall(pinyin_text)
    
    # 如果没有任何匹配，直接返回原始字符串
    if len(matches) == 0:
        return ori_text
    else:
        new_string = ""
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # 转换非关键词部分的拼音为汉字
                py_lists = [piyi for piyi in part.split(" ") if piyi.isalpha()]
                if py_lists:
                    hanzi = pinyin_2_hanzi(py_lists)
                    if hanzi:
                        new_string += hanzi
                    else:
                        # 如果没有匹配到，返回原始的拼音对应的中文部分
                        new_string += ori_text[:len(part.split(" "))]
                else:
                    new_string += part
            else:
                # 保留关键词
                new_string += part
    return new_string

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
    global settings_path
    global hzys_output_dir
        # 获取当前时间戳
    current_time = datetime.now()
        # 创建输出目录
    if not os.path.exists(hzys_output_dir):
        os.makedirs(hzys_output_dir)
    # 格式化为字符串，例如：2023-10-05_14_30_00_123456
    current_time_str = current_time.strftime("%Y-%m-%d_%H_%M_%S_%f")
    text = chinese_to_pinyin(ori_text)
    text = py2hanzi(text,ori_text)
    hzys_exe_path = os.path.join(os.path.dirname(__file__), "hzys.exe")
    process = await asyncio.create_subprocess_exec(
        hzys_exe_path,
        '-t', text,  # 输入的文字
        '-o', os.path.join(hzys_output_dir,f"{current_time_str}.wav"), # 输出目录以及文件名
        '-y',               # 使用原声大碟
        '-set',settings_path,  # 配置文件路径，默认为同目录下的settings.json
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
        # run_hzys(input_t2)
    )

if __name__ == "__main__":
    asyncio.run(main())


