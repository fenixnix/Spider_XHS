import hashlib
import random
import struct
import base64
import json

class XHS_Signature:
    """小红书签名生成工具类，完全使用Python实现，脱离Node.js依赖"""
    
    def __init__(self):
        self.CONFIG = {
            "BASE58_ALPHABET": "NOPQRStuvwxWXYZabcyz012DEFTKLMdefghijkl4563GHIJBC7mnop89+/AUVqrsOPQefghijkABCDEFGuvwz0123456789xy",
            "CUSTOM_BASE64_ALPHABET": "ZmserbBoHQtNP+wOcza/LpngG8yJq42KWYj0DSfdikx3VT16IlUAFM97hECvuRX5",
            "STANDARD_BASE64_ALPHABET": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
            "X3_BASE64_ALPHABET": "MfgqrsbcyzPQRStuvC7mn501HIJBo2DEFTKdeNOwxWXYZap89+/A4UVLhijkl63G",
            "HEX_KEY": "71a302257793271ddd273bcee3e4b98d9d7935e1da33f5765e2ea8afb6dc77a51a499d23b67c20660025860cbf13d4540d92497f58686c574e508f46e1956344f39139bf4faf22a3eef120b79258145b2feb5193b6478669961298e79bedca646e1a693a926154a5a7a1bd1cf0dedb742f917a747a1e388b234f2277",
            "VERSION_BYTES": [119, 104, 96, 41],
            "ENV_FINGERPRINT_XOR_KEY": 41,
            "SEQUENCE_VALUE_MIN": 15,
            "SEQUENCE_VALUE_MAX": 50,
            "WINDOW_PROPS_LENGTH_MIN": 900,
            "WINDOW_PROPS_LENGTH_MAX": 1200,
            "CHECKSUM_VERSION": 1,
            "CHECKSUM_XOR_KEY": 115,
            "CHECKSUM_FIXED_TAIL": [249, 65, 103, 103, 201, 181, 131, 99, 94, 7, 68, 250, 132, 21],
            "ENV_FINGERPRINT_TIME_OFFSET_MIN": 10,
            "ENV_FINGERPRINT_TIME_OFFSET_MAX": 50,
            "X3_PREFIX": "mns0301_",
            "XYS_PREFIX": "XYS_",
            "TEMPLATE": {
                "x0": "4.2.6",
                "x1": "xhs-pc-web",
                "x2": "Windows",
                "x3": "",
                "x4": "",
            },
        }
        
        # 预计算HEX_KEY_BYTES
        self.HEX_KEY_BYTES = bytes.fromhex(self.CONFIG["HEX_KEY"])
        
        # 预计算base64映射表
        self.STD_TO_CUSTOM_B64 = {}
        self.STD_TO_X3_B64 = {}
        for i in range(64):
            self.STD_TO_CUSTOM_B64[self.CONFIG["STANDARD_BASE64_ALPHABET"][i]] = self.CONFIG["CUSTOM_BASE64_ALPHABET"][i]
            self.STD_TO_X3_B64[self.CONFIG["STANDARD_BASE64_ALPHABET"][i]] = self.CONFIG["X3_BASE64_ALPHABET"][i]
    
    def rand32(self):
        """生成32位随机数"""
        return random.randint(0, 0xFFFFFFFF)
    
    def rand_byte(self, min_val=0, max_val=255):
        """生成指定范围内的随机字节"""
        return random.randint(min_val, max_val)
    
    def int_to_le(self, val, length=4):
        """将整数转换为小端字节序"""
        return val.to_bytes(length, byteorder='little', signed=False)
    
    def struct_pack_little_endian_q(self, ts):
        """将时间戳打包为小端字节序的8字节数组"""
        return struct.pack('<Q', ts)
    
    def xor_array(self, arr):
        """异或数组与HEX_KEY"""
        result = []
        for i, b in enumerate(arr):
            # 确保HEX_KEY_BYTES有足够的长度
            if i < len(self.HEX_KEY_BYTES):
                result.append((b ^ self.HEX_KEY_BYTES[i]) & 0xFF)
            else:
                # 如果超出长度，只取b本身
                result.append(b & 0xFF)
        return result
    
    def encode_x3(self, bytes_data):
        """X3编码"""
        # 标准base64编码
        std_b64 = base64.b64encode(bytes_data).decode('utf-8')
        
        # 替换为X3 base64字母表
        x3_b64 = ''
        for ch in std_b64:
            if ch in self.STD_TO_X3_B64:
                x3_b64 += self.STD_TO_X3_B64[ch]
            else:
                x3_b64 += ch
        
        return x3_b64
    
    def b64_custom_encode(self, s):
        """自定义base64编码"""
        # 标准base64编码
        std_b64 = base64.b64encode(s.encode('utf-8')).decode('utf-8')
        
        # 替换为自定义base64字母表
        custom_b64 = ''
        for ch in std_b64:
            if ch in self.STD_TO_CUSTOM_B64:
                custom_b64 += self.STD_TO_CUSTOM_B64[ch]
            else:
                custom_b64 += ch
        
        return custom_b64
    
    def build_content_string(self, method, uri, payload):
        """构建内容字符串"""
        if payload is None:
            payload = {}
        elif isinstance(payload, str):
            # 如果payload是字符串，将其转换为字典（如果是JSON字符串）或空字典
            try:
                payload = json.loads(payload)
            except:
                payload = {}
        
        if method == "POST":
            return uri + json.dumps(payload, separators=(',', ':'))
        
        # 确保payload是字典类型
        if not isinstance(payload, dict):
            return uri
        
        entries = list(payload.items())
        if not entries:
            return uri
        
        parts = []
        for key, value in entries:
            if isinstance(value, list):
                val_str = ','.join(str(v) if v is not None else '' for v in value)
            else:
                val_str = str(value) if value is not None else ''
            
            val_str = val_str.replace('=', '%3D')
            parts.append(f"{key}={val_str}")
        
        return f"{uri}?{'&'.join(parts)}"
    
    def md5_hex(self, s):
        """生成MD5十六进制字符串"""
        return hashlib.md5(s.encode('utf-8')).hexdigest()
    
    def env_fingerprint_a(self, ts, xor_key):
        """环境指纹A生成"""
        data = list(self.struct_pack_little_endian_q(ts))
        
        sum1 = data[1] + data[2] + data[3] + data[4]
        sum2 = data[5] + data[6] + data[7]
        
        mark = ((sum1 & 0xFF) + sum2) & 0xFF
        data[0] = mark
        
        for i in range(len(data)):
            data[i] ^= xor_key
        
        return data
    
    def env_fingerprint_b(self, ts):
        """环境指纹B生成"""
        return list(self.struct_pack_little_endian_q(ts))
    
    def build_payload(self, d_hex, a1, app_id, content):
        """构建签名负载"""
        payload = []
        
        # 添加版本字节
        payload.extend(self.CONFIG["VERSION_BYTES"])
        
        # 添加种子
        seed = self.rand32()
        seed_bytes = list(self.int_to_le(seed, 4))
        payload.extend(seed_bytes)
        seed_byte0 = seed_bytes[0]
        
        # 当前时间戳
        timestamp = int(self.get_current_timestamp())
        
        # 添加环境指纹A
        payload.extend(self.env_fingerprint_a(timestamp, self.CONFIG["ENV_FINGERPRINT_XOR_KEY"]))
        
        # 添加环境指纹B
        time_offset = self.rand_byte(
            self.CONFIG["ENV_FINGERPRINT_TIME_OFFSET_MIN"],
            self.CONFIG["ENV_FINGERPRINT_TIME_OFFSET_MAX"]
        )
        payload.extend(self.env_fingerprint_b(timestamp - time_offset))
        
        # 添加序列值
        sequence_value = self.rand_byte(
            self.CONFIG["SEQUENCE_VALUE_MIN"],
            self.CONFIG["SEQUENCE_VALUE_MAX"]
        )
        payload.extend(list(self.int_to_le(sequence_value, 4)))
        
        # 添加window props长度
        window_props_length = self.rand_byte(
            self.CONFIG["WINDOW_PROPS_LENGTH_MIN"],
            self.CONFIG["WINDOW_PROPS_LENGTH_MAX"]
        )
        payload.extend(list(self.int_to_le(window_props_length, 4)))
        
        # 添加uri长度
        uri_length = len(content.encode('utf-8'))
        payload.extend(list(self.int_to_le(uri_length, 4)))
        
        # 添加MD5字节
        md5_bytes = bytes.fromhex(d_hex)
        for i in range(8):
            payload.append(md5_bytes[i] ^ seed_byte0)
        
        payload.append(52)
        
        # 添加a1
        a1_bytes = a1.encode('utf-8')[:52]
        padded_a1 = a1_bytes.ljust(52, b'\x00')
        payload.extend(padded_a1)
        
        payload.append(10)
        
        # 添加source
        source_bytes = app_id.encode('utf-8')[:10]
        padded_source = source_bytes.ljust(10, b'\x00')
        payload.extend(padded_source)
        
        payload.append(1)
        payload.append(self.CONFIG["CHECKSUM_VERSION"])
        payload.append(seed_byte0 ^ self.CONFIG["CHECKSUM_XOR_KEY"])
        payload.extend(self.CONFIG["CHECKSUM_FIXED_TAIL"])
        
        return payload
    
    def get_current_timestamp(self):
        """获取当前时间戳"""
        import time
        return str(int(time.time() * 1000))
    
    def crc32(self, data):
        """CRC32校验"""
        crc = 0xFFFFFFFF
        poly = 0xEDB88320
        
        # 生成CRC表
        crc_table = []
        for i in range(256):
            c = i
            for j in range(8):
                if c & 1:
                    c = (c >> 1) ^ poly
                else:
                    c >>= 1
            crc_table.append(c)
        
        # 计算CRC
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        for byte in data:
            crc = (crc >> 8) ^ crc_table[(crc & 0xFF) ^ byte]
            
        return crc ^ 0xFFFFFFFF
    
    def sign_xs(self, method, uri, a1_value, xsec_appid="xhs-pc-web", payload=None):
        """生成xs签名"""
        method = method.upper()
        content = self.build_content_string(method, uri, payload)
        d_val = self.md5_hex(content)
        
        payload_arr = self.build_payload(
            d_val,
            a1_value.strip(),
            xsec_appid.strip(),
            content
        )
        
        xor_bytes = self.xor_array(payload_arr)
        x3_body = self.encode_x3(bytes(xor_bytes[:124]))
        x3_full = self.CONFIG["X3_PREFIX"] + x3_body
        
        template = self.CONFIG["TEMPLATE"].copy()
        template["x3"] = x3_full
        json_compact = json.dumps(template, separators=(',', ':'))
        
        encoded = self.b64_custom_encode(json_compact)
        return self.CONFIG["XYS_PREFIX"] + encoded
    
    def get_xs_common(self, a1, xs, xt):
        """生成xs_common"""
        fff = "I38rHdgsjopgIvesdVwgIC+oIELmBZ5e3VwXLgFTIxS3bqwErFeexd0ekncAzMFYnqthIhJeSnMDKutRI3KsYorWHPtGrbV0P9WfIi/eWc6eYqtyQApPI37ekmR6QL+5Ii6sdneeSfqYHqwl2qt5B0DBIx++GDi/sVtkIxdsxuwr4qtiIhuaIE3e3LV0I3VTIC7e0utl2ADmsLveDSKsSPw5IEvsiVtJOqw8BuwfPpdeTFWOIx4TIiu6ZPwbPut5IvlaLbgs3qtxIxes1VwHIkumIkIyejgsY/WTge7eSqte/D7sDcpipedeYrDtIC6eDVw2IENsSqtlnlSuNjVtIvoekqt3cZ7sVo4gIESyIhE4NnquIxhnqz8gIkIfoqwkICZW8g3sdlOeVPw3IvAe0fged0YyIi5s3Mc52utAIiKsidvekZNeTPt4nAOeWPwEIvSzaAdeSVwXpnesDqwmI3TrIxE5Luwwaqw+rekhZANe1MNe0Pw9ICNsVLoeSbIFIkosSr7sVnFiIkgsVVtMIiudqqw+tqtWI30e3PwIIhoe3ut1IiOsjut3wutnsPwXICclI3Ir27lk2I5e1utCIES/IEJs0PtnpYIAO0JeYfD1IErPOPtKoqw3I3OexqtWQL5eiz0sVSEyIEJekd/skPtsnPwqICJeSPwiIh5eVAuLIv5eYo/e0PtSICKsVqwV4omqI3RIIkge0e0sYZ0si/7eiuwSIvTeIhqmGuwCIkrPIx0edUzbzbveTPw5IxI0yVwImZeedM0eWVwmeqt2IiM9IhhQLqwJPqtbIxZ="
        
        d = {
            "s0": 5,
            "s1": "",
            "x0": "1",
            "x1": "4.2.6",
            "x2": "Windows",
            "x3": "xhs-pc-web",
            "x4": "4.84.1",
            "x5": a1,
            "x6": xt,
            "x7": xs,
            "x8": fff,
            "x9": self.crc32(str(xt) + xs + fff),
            "x10": 0,
            "x11": "normal",
        }
        
        data_str = json.dumps(d, separators=(',', ':'))
        
        # 自定义base64编码实现
        def b64_encode(e):
            c = list(self.CONFIG["CUSTOM_BASE64_ALPHABET"])
            r = len(e)
            d = r % 3
            s = []
            f = 16383
            u = 0
            l = r - d
            
            def encode_chunk(e, a, r):
                d = []
                s = a
                while s < r:
                    if s + 2 < r:
                        e1 = e[s]
                        e2 = e[s + 1]
                        e3 = e[s + 2]
                        c_val = ((e1 << 16) & 0xff0000) + ((e2 << 8) & 65280) + (255 & e3)
                        d1 = c[(c_val >> 18) & 63]
                        d2 = c[(c_val >> 12) & 63]
                        d3 = c[(c_val >> 6) & 63]
                        d4 = c[63 & c_val]
                        d.append(d1 + d2 + d3 + d4)
                    s += 3
                return ''.join(d)
            
            while u < l:
                end = u + f
                if end > l:
                    end = l
                s.append(encode_chunk(e, u, end))
                u += f
                
            if d == 1:
                a = e[r - 1]
                s.append(c[a >> 2] + c[(a << 4) & 63] + "==")
            elif d == 2:
                a = (e[r - 2] << 8) + e[r - 1]
                s.append(c[a >> 10] + c[(a >> 4) & 63] + c[(a << 2) & 63] + "=")
                
            return ''.join(s)
        
        def encode_utf8(e):
            r = []
            for char in e:
                if ord(char) < 128:
                    r.append(ord(char))
                else:
                    # 简单的UTF-8编码实现
                    if ord(char) < 2048:
                        r.append(192 | (ord(char) >> 6))
                        r.append(128 | (ord(char) & 63))
                    elif ord(char) < 65536:
                        r.append(224 | (ord(char) >> 12))
                        r.append(128 | ((ord(char) >> 6) & 63))
                        r.append(128 | (ord(char) & 63))
                    else:
                        r.append(240 | (ord(char) >> 18))
                        r.append(128 | ((ord(char) >> 12) & 63))
                        r.append(128 | ((ord(char) >> 6) & 63))
                        r.append(128 | (ord(char) & 63))
            return r
        
        return b64_encode(encode_utf8(data_str))
    
    def get_request_headers_params(self, api, data, a1, method="POST"):
        """获取请求头参数"""
        import time
        xt = int(time.time() * 1000)
        xs = self.sign_xs(method, api, a1, "xhs-pc-web", data)
        xs_common = self.get_xs_common(a1, xs, xt)
        
        return {
            "xs": xs,
            "xt": str(xt),
            "xs_common": xs_common
        }
