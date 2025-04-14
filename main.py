from ncatbot.plugin import BasePlugin, CompatibleEnrollment
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.utils.logger import get_log
import os
import yaml
import json
from .hzys_util import hzys_output_dir,run_hzys,chinese_to_pinyin
_log = get_log()
HuoZiYinShua_help_info =[
    "活字印刷使用方法：",
    "1.输入 /活字印刷+空格+消息，bot会生成otto活字印刷语音。",
    "2.检测到原声大碟时，bot会自动发送原声大碟语音。",
    "3.输入 /活字印刷+空格+help 或者/活字印刷+空格+帮助，bot会自动发送帮助信息。",


]

ysddTable_dict_path = os.path.join(os.path.dirname(__file__), "ysddTable.json")
super_user = ""
ysddTable_dict = {}
bot = CompatibleEnrollment  # 兼容回调函数注册器
global_hzys_check = True
global_config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
class HuoZiYinShua_Bot(BasePlugin):
    name = "HuoZiYinShua_Bot" # 插件名称
    version = "0.7.0"  # 插件版本
    
    @bot.group_event()
    async def on_group_event(self, msg: GroupMessage):
        '''
        群聊事件处理-配置与帮助信息
        '''
        global HuoZiYinShua_help_info
        global global_hzys_check
        
        if msg.raw_message == "测试活字印刷":
            if msg.user_id == super_user:
                await self.api.post_group_msg(msg.group_id, text="插件活字印刷测试成功")
        if msg.raw_message.lower() == "/活字印刷 help" or msg.raw_message.lower() == "/活字印刷 帮助":
            await self.api.post_group_msg(msg.group_id, text="\n".join(HuoZiYinShua_help_info))
        if msg.raw_message.lower() == "/活字印刷 关闭原声大碟检测"or msg.raw_message.lower() == "关闭原声大碟检测":
            if msg.user_id == super_user:
                global_hzys_check = False
        if msg.raw_message.lower() == "/活字印刷 开启原声大碟检测"or msg.raw_message.lower() == "开启原声大碟检测":
            if msg.user_id == super_user:
                global_hzys_check = True

    @bot.group_event()
    async def on_group_event(self, msg: GroupMessage):
        '''
        群聊事件处理-HuoZiYinShua_Bot运行
        '''
        global global_hzys_check
        hzys_text = ""
        hzys_yyds_text = ""
        message_segs = msg.message
        for item in message_segs:
            if item["type"] == "text" :
                if global_hzys_check:
                    hzys_yyds_text = item["data"]["text"].strip()
                if item["data"]["text"].startswith("/活字印刷 "):
                    hzys_text = item["data"]["text"].strip()[6:]
                    print(hzys_text)
                    if hzys_text == "help" or hzys_text == "帮助" or hzys_text == "":
                        return
                    wav_file_name = await run_hzys(hzys_text)
                    if wav_file_name == "Error":
                        _log.info(f"Error for text '{hzys_text}'")
                        return
                    wav_file = f"{wav_file_name}.wav"
                    wav_record_path = os.path.join(hzys_output_dir,wav_file)
                    
                    if not os.path.exists(wav_record_path):
                        _log.info(f"路径不存在:{wav_record_path}")
                        return
                    
                    await self.api.post_group_file(msg.group_id,record=wav_record_path)
                    
                    if os.path.exists(wav_record_path):
                        # 发送完就删除文件
                        os.remove(wav_record_path)

                    return
                    
        # if hzys_yyds_text == "":
        #     return
        if global_hzys_check: # 如果全局检测原声大碟，则检测原声大碟
            hzys_text_pinyin = chinese_to_pinyin(hzys_yyds_text).strip()
            if hzys_text_pinyin in ysddTable_dict.keys():
                wav_file_name = await run_hzys(hzys_yyds_text)
                if wav_file_name == "Error":
                    _log.info(f"Error for text '{hzys_yyds_text}'")
                    return
                wav_file = f"{wav_file_name}.wav"
                wav_record_path = os.path.join(hzys_output_dir,wav_file )
                if not os.path.exists(wav_record_path):
                    _log.info(f"路径不存在:{wav_record_path}")
                    return
                    
                await self.api.post_group_file(msg.group_id,record=wav_record_path)
                
                if os.path.exists(wav_record_path):
                    # 发送完就删除文件
                    os.remove(wav_record_path)

        
        
    @bot.private_event()
    async def on_private_message(self, msg: PrivateMessage):
        '''
        私聊事件处理
        '''
        pass
    
    
    
    async def on_load(self):
        # with self.work_space:
            # os.chdir(os.path.join(os.getcwd(), "plugins", "PixivNcat"))
        print("插件加载中……")
        # 从 config.yaml 中读取配置
        with open(global_config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            global super_user
            super_user = config_data["manager_id"]
        with open(ysddTable_dict_path, "r", encoding="utf-8") as f:
            global ysddTable_dict
            ysddTable_dict = json.load(f)
        print(f"wav文件输出路径为:{hzys_output_dir}")


        # 插件加载时执行的操作, 可缺省
        print(f"{self.name} 插件已加载")
        print(f"插件版本: {self.version}")