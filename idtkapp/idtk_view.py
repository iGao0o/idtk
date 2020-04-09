from datetime import date, datetime, timedelta
import crcmod
from django.views.generic import View
from idtkapp.models import DeviceData, DeviceStatus, DeviceLogModel
from django.http import HttpResponse


class GetStettingModel:

    def __init__(self, data):
        self.data = {
            "sn": data[:8],
            "commonType": data[8:10],  # 请求数据的命令类型: 0x00:不包含校验时间与营业时间;0x01:包含校验系统时间;0x02:包含校验营业时间;0x03:包含校验系统时间与营业时间
            "speed": data[10:12],  # 设备探测速度 0x00 低速，0x01 是高速
            "recordingCycle": data[12:14],  # 记录周期的分钟数 .范围0x00 --0xff  对应时间范围0-255分钟 0 表示实时记录。
            "uploadCycle": data[14:16],  # 上传周期.范围0x00 --0xff 对应时间范围0-255分钟  0表示实时上传。无论周如何设置，营业时间开始,如果有未上传数据默认会上传。
            "fixedTimeUpload": data[16:18],
            "upload": data[18:34],
            "model": data[34:36],  # 运行 0x00  联网模式0x00单机模式 0x01  单机版不上传到服务器
            "disableType": data[36:38],  # 显示类型 0x00:计数不在幕上显示;0x01:显示总数;0x02:显示双向
            "mac1": data[38:52],  # mac1
            "mac2": data[52:66],  # mac2
            "mac3": data[66:80],  # mac3
            "day": timeDecode(data[80:94]),  # 格式化后的时间
            "openTime": "%s:%s" % (int(data[94:96], 16), int(data[96:98], 16)),  # 开业时间
            "closeTime": "%s:%s" % (int(data[98:100], 16), int(data[100:102], 16)),  # 关门时间
            "crc": data[102:]
        }

    def get(self, key):
        return self.data.get(key)

    def timeIsOk(self):
        """
        检查服务器时间和设备时间相差是否小于60s
        :return:True 时间相差不大 ok的
        """
        return (self.get("day") + timedelta(minutes=1)) > datetime.now()


class SendNewSetting:

    @classmethod
    def set(cls, flag):
        return cls.msg("04", flag)

    @classmethod
    def ok(cls, flag):
        return cls.msg("05", flag)

    @classmethod
    def msg(cls, resultType, flag):
        result = [
            resultType,
            flagEncode(flag),
            "00000000",
            "03",  # 包含系统时间和营业时间
            "00",  # 00 低速 01 高速
            "00",  # 记录周期 实时记录
            "00",  # 上传周期 实时
            "00",  # 保留字段
            "00",  # 保留字段
            "00",  # 保留字段
            "00",  # 保留字段
            "00",  # 保留字段
            "00",  # 保留字段
            "00",  # 保留字段
            "00",  # 保留字段
            "00",  # 保留字段
            "00",  # 设备运行模式 00 联机 01 单机
            "02",  # 显示类型 00 不在幕上显示 01 单向客流总数 02 双向客流总数
            "00000000000000",  # mac1
            "00000000000000",  # mac2
            "00000000000000",  # mac2
        ]
        result.extend(timeEncode())  # 时间
        result.append("00")  # 保留字段
        result.append("00")  # 开店时间闭店时间
        result.append("00")  # 开店时间闭店时间
        result.append("17")  # 开店时间闭店时间
        result.append("3B")  # 开店时间闭店时间
        result.append("0000")  # 保留字段
        crc = getCrC(result)
        result.append(crc)
        return "".join(result)


class CacheResult:
    @classmethod
    def ok(cls, flag):
        return cls.msg("01", flag)

    @classmethod
    def err(cls, flag):
        return cls.msg("00", flag)

    @classmethod
    def msg(cls, resType, flag):
        result = [
            resType,
            flagEncode(flag),
            "01"
        ]
        result.extend(timeEncode(True))  # 当前时间
        result.append("00")  # 开店时间闭店时间
        result.append("00")  # 开店时间闭店时间
        result.append("17")  # 开店时间闭店时间
        result.append("3B")  # 开店时间闭店时间
        crc = getCrC(result)
        result.append(crc)
        return "".join(result)


crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)


def getCrC(msgs: list):
    msg = b""
    for m in msgs:
        msg = msg + int(m, 16).to_bytes(int(len(m) / 2), "big")
    return crc16(msg).to_bytes(2, "big").hex().upper()


def timeEncode(week=False):
    """
    格式化时间 将时间转为16进制字符形式
    :return [year,month,day,hour,minute,second]
    """
    now = datetime.now()
    result = []
    result.append(hex(now.year % 2000)[2:])  # year
    result.append(hex(now.month)[2:].zfill(2))  # month
    result.append(hex(now.day)[2:].zfill(2))  # day
    result.append(hex(now.hour)[2:].zfill(2))  # hour
    result.append(hex(now.minute)[2:].zfill(2))  # minute
    result.append(hex(now.second)[2:].zfill(2))  # second
    if week:
        result.append(hex(now.weekday())[2:].zfill(2))  # 星期
    return result


def timeDecode(day: str):
    """
    将时间解码 将16进制字符形式转为datetime
    :param day:
    :return:
    """
    return datetime(year=int("20%s" % to10(day[:2])), month=to10(day[2:4]),
                    day=to10(day[4:6]), hour=to10(day[6:8]),
                    minute=to10(day[8:10]), second=to10(day[10:12]))


def flagEncode(flag):
    """
    标志位编码
    :param flag:
    :return:
    """
    return to10(flag).to_bytes(2, "little").hex()


def toBig(data: str) -> int:
    """
    将原先的小端转为大端
    :param data:
    :return:
    """
    return int(to10(data).to_bytes(int(len(data) / 2), "little").hex(), 16)


def to10(data: str) -> int:
    """
    将原先的16进制数据转为10进制
    :param data:
    :return:
    """
    return int(data, 16)


# 接收红外数据视图 /dataport.aspx
class IndexView(View):

    def getDeviceStatus(self, flag: int, data: str):
        return DeviceStatus(
            flag=flag,
            version=to10(data[:4]),  # 版本号
            dev_sn=toBig(data[4:12]),  # 设备号
            ir_voltage=to10(data[14:16]),  # 发射器剩余电量
            voltage=to10(data[18:20])  # 红外接收器剩余电量
        )

    def getDeviceData(self, data: str, status_id: int):
        return DeviceData(
            time=timeDecode(data[:12]),
            focus=to10(data[12:14]),
            din=toBig(data[14:22]),
            dout=toBig(data[22:30]),
            status_id=status_id
        )

    def handleGetSetting(self, data, flag):
        """
        初始化配置信息
        :param data:
        :param flag:
        :return:
        """
        getSettingModel = GetStettingModel(data)
        #                 时间检查通过                                                时间检查不通过
        result_msg = SendNewSetting.ok(flag) if getSettingModel.timeIsOk() else SendNewSetting.set(flag)
        return result_msg

    def handleCache(self, body: str, status: str, flag: int):
        status = self.getDeviceStatus(flag, status)
        status.save()
        status_id = status.id
        print(f"status: id={status_id} flag={status.flag} "
              f"version={status.version} devSn={status.dev_sn} i"
              f"r={status.ir_voltage} vo={status.voltage}")
        datas = [self.getDeviceData(i[5:], status_id) for i in body.split("&") if i.startswith("data")]
        for d in datas:
            d.save()
            msg = f"data: id={d.id}, time={d.dev_time}, focus={d.focus}, din={d.din} dout={d.dout}"
        return CacheResult.ok(flag)

    def post(self):
        body = self.request.body.decode("utf-8")
        body_dict = {i[0]: i[1] for i in [i.split("=") for i in body.split("&")]}
        cmd = body_dict['cmd']
        flag = body_dict['flag']
        if cmd == "getsetting":
            result_msg = self.handleGetSetting(body_dict['data'], flag)
        else:
            status = body_dict['status']
            result_msg = self.handleCache(body, status, flag)
        msg = "result=%s" % result_msg
        log = DeviceLogModel(get_msg=body, to_msg=msg)
        log.save()
        return HttpResponse(content=msg)
