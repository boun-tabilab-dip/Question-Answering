# -*- coding: utf-8 -*-

import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def tokenize(text):
    p = re.findall('\(([^()]*)\)', text);

    for p_item in p:
        text = text.replace('(' + p_item + ')', ' ');

    #res = re.findall('[0-9,a-z,ğ,ü,ş,ç,ö,ı,â,'',’,A-Z,Ğ,Ü,Ş,Ç,Ö,İ,Â,-]+', text.replace('i̇','i').replace('\'','').replace('’',''));

    res = text.replace('i̇','i').replace('\'','').replace('’','').split(' ');

    return [item.strip(',').strip('.').strip('?').strip('!').strip('.').strip(':').strip(';') for item in res];
