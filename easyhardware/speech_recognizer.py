import time
from typing import List, Tuple

import smbus


class SpeechRecognizer:
    
    """
    适用于亚博yahboom语音识别模块
    
    该类适用于亚博yahboom语音识别模块，使用者仅需正确连接线材即可调用API进行使用。
    我对该模块的使用要求并没有做过多的限制，例如最大句长和最大序号等，具体请参考该模块的使用说明。
    注意，由于目前只实现了Python的接口，所以您仅可以在任何能够使用Python的嵌入式设备例如树莓派中进行使用。
    """
    
    __i2c_addr = 0x0f             # 语音识别模块地址
    __add_word_addr  = 0x01       # 词条添加地址
    __mode_addr  = 0x02           # 识别模式设置地址，值为0-2，0:循环识别模式 1:口令模式 ,2:按键模式，默认为循环检测
    __rgb_addr = 0x03   		  # RGB灯设置地址,需要发两位，第一个直接为灯号1：蓝 2:红 3：绿 ,第二个字节为亮度0-255，数值越大亮度越高
    __rec_gain_addr  = 0x04       # 识别灵敏度设置地址，灵敏度可设置为0x00-0x55，值越高越容易检测但是越容易误判，建议设置值为0x40-0x55,默认值为0x40                                   
    __clear_addr = 0x05           # 清除掉电缓存操作地址，录入信息前均要清除下缓存区信息
    __key_flag_addr = 0x06        # 用于按键模式下，设置启动识别模式
    __beep_addr = 0x07            # 用于设置是否开启识别结果提示音
    __result_addr = 0x08          # 识别结果存放地址
    __buzzer_addr = 0x09          # 蜂鸣器控制寄存器，1位开，0位关
    __num_cleck_addr = 0x0a       # 录入词条数目校验
    __version_addr = 0x0b         # 固件版本号
    __busy_flag_addr = 0x0c       # 忙闲标志
    
    
    def __init__(self) -> None:
        
        self.__bus = smbus.SMBus(1)
        
        
    def __read_byte(self, addr: int) -> int:
        
        self.__bus.write_byte(self.__i2c_addr, addr)
        time.sleep(0.05)
        
        return self.__bus.read_byte(self.__i2c_addr)
    
    
    def __wait(self) -> None:
        
        is_busy = 1
        
        while is_busy != 0:
            is_busy = self.__read_byte(self.__busy_flag_addr)
            
            
    def enable_buzzer(self, use: bool) -> None:
        
        """
        使能蜂鸣器
        
        Args:
            use: 是否使用蜂鸣器，True表示使用，False表示禁用
        """
        
        value = 1 if use else 0
        self.__bus.write_byte_data(self.__i2c_addr, self.__buzzer_addr, value)
        
    
    def enable_beep(self, use: bool) -> None:
        
        """
        使能提示音
        
        Args:
            use: 是否使用识别成功提示音，True表示使用，False表示禁用 
        """
        
        value = 1 if use else 0
        self.__bus.write_byte_data(self.__i2c_addr, self.__beep_addr, value)
    
    
    def set_mode(self, mode: int) -> None:
        
        """
        设置模块的工作模式
        
        Args:
            mode: 0表示循环检测模式，1表示口令模式，2表示按键检测模式
        """
        
        self.__bus.write_byte_data(self.__i2c_addr, self.__mode_addr, mode)
        self.__wait()
        
        
    def enable_recognize(self, use: bool) -> None:
        
        """
        用于按键模式下，是否开启识别
        
        Args:
            use: 是否识别，True表示开启识别功能，False表示关闭识别功能
        """
        
        value = 1 if use else 0
        self.__bus.write_byte_data(self.__i2c_addr, self.__key_flag_addr, value)
        
        
    def get_firmware_version(self) -> int:
        
        """
        获取固件版本号
        
        Returns:
            固件版本号
        """
        
        return self.__read_byte(self.__version_addr)
        
        
    def set_microphone_sensitivity(self, sensitivity: int) -> None:
        
        """
        设置语音识别的灵敏度
        
        Args:
            sensitivity: 灵敏度值，可设置为0x00-0x7f，供电为5V的时候建议设置值为0x40-0x55
        """
        
        self.__bus.write_byte_data(self.__i2c_addr, self.__rec_gain_addr, sensitivity)


    def set_rgb(self, r: int, g: int, b: int) -> None:
        
        """
        设置板载RGB灯的颜色。
        
        Args:
            r: 目标颜色的RGB色彩空间R值
            g: 目标颜色的RGB色彩空间G值
            b: 目标颜色的RGB色彩空间B值
        """
        
        self.__bus.write_i2c_block_data (self.__i2c_addr, self.__rgb_addr,[r, g, b])
        
        
    def read_result(self) -> int:
        
        """
        读取识别结果

        Returns:
            识别句序号
        """
        
        return self.__read_byte(self.__result_addr)
            
            
    def set_keys(self, keys: List[Tuple[int, str]]) -> None:
        
        """
        设置语音识别模块的识别词
        
        Args:
            keys: 传入的是一个列表，列表中的元素为元组，其元组元素组成如下：(拼音字符串, 识别序号)
        """
        
        self.__bus.write_byte_data(self.__i2c_addr, self.__clear_addr, 0x40)
        self.__wait()
        
        for key in keys:
            words = [self.__add_word_addr, len(key[0]) + 2, key[1]]
            for  alond_word in key[0]:
                words.append(ord(alond_word))
            words.append(0)	

            for word in words:
                self.__bus.write_byte(self.__i2c_addr, word)
                time.sleep(0.03)
            self.__wait()	
        
        check = 0
        while check != len(keys):
            check = self.__read_byte(self.__num_cleck_addr)