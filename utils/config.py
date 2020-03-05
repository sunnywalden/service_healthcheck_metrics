# !/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser as ConfigParser
import os, re, io


def format_config(filename):
    file_data = ""
    dir = os.path.dirname(os.path.abspath(__file__))
    path = "%s/" % dir
    filepath = path + filename
    # print filepath
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip().replace("\t", " ")
            if re.match(r"\[.*\]", line):
                file_data = "%s%s\n" % (file_data, line)
            elif re.match(r"^.*=.*$", line):
                file_data = "%s%s\n" % (file_data, line)
            else:
                newlinelist = line.split(' ')
                newlinelist = filter(None, newlinelist)
                if len(newlinelist) == 0: continue
                if '\n' in newlinelist: newlinelist.remove('\n')
                if not len(newlinelist) == 2:
                    raise Exception("check config file failed: %s" % line)
                newline = ' = '.join(newlinelist)
                file_data = "%s%s\n" % (file_data, newline)
    with open(filepath, "w") as f:
        f.write(file_data)


class config:
    def __init__(self, filename):
        self.config = ConfigParser.RawConfigParser(allow_no_value=True)
        dir = os.path.dirname(os.path.abspath(__file__))
        path = "%s/../" % dir
        filepath = path + filename
        if not os.path.exists(filepath):
            raise Exception("ERROR: %s该配置文件不存在！" % filepath)
        f = open(filepath)
        # content = f.read()
        # self.config.readfp(io.BytesIO(str(content)))
        self.config.read_file(f)
        f.close()

    def checkArg(self, str, info):
        '''检查参数是否为空'''
        # if check.nullCheck(str):
        if str is None or str == '':
            raise Exception(info)

    def checkSection(self, section):
        '''检查配置文件的section是否存在'''
        if not self.config.has_section(section):
            raise Exception("No section %s" % section)

    def getOption(self, section, option, type="str", default=None):
        '''检查配置文件的option是否存在'''
        returnStr = ""

        # self.checkSection(section)
        # print(self.config.get(section, option))

        if not self.config.has_option(section, option):
            # 如果对应section中没有找到option则到通用的section中查找option
            if not self.config.has_option("common", option):
                if default is not None:
                    return default
                else:
                    raise Exception("No %s option in section %s" % (option, section))
                # return None
            else:
                if type == "bool":
                    returnStr = self.config.getboolean("common", option)
                elif type == "int":
                    returnStr = self.config.getint("common", option)
                elif type == "float":
                    returnStr = self.config.getfloat("common", option)
                else:
                    returnStr = self.config.get("common", option)
        else:
            if type == "bool":
                print('Debug')
                returnStr = self.config.getboolean(section, option)
            elif type == "int":
                returnStr = self.config.getint(section, option)
            elif type == "float":
                returnStr = self.config.getfloat(section, option)
            else:
                returnStr = self.config.get(section, option)
        return returnStr
