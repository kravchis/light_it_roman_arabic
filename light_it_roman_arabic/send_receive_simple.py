from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import re
import os
import datetime
app = Flask(__name__)

id_=0                             #Почти датабаза :)
dir_ = os.path.abspath(os.path.dirname('send_receive_simple.py'))
filename = os.path.join(dir_, 'conversion_history.txt')

def write_to_db(inquiry_, response_):           # Функция записи в текстовый файл 
    global id_
    f = open(filename, 'a+')
    line = '{}, {}, {}, {} \n'.format(id_, inquiry_, response_, datetime.datetime.now())
    f.write(line)
    id_+=1
    f.close()

romanNumeralMap = (('M',  1000),
                   ('CM', 900),
                   ('D',  500),
                   ('CD', 400),
                   ('C',  100),
                   ('XC', 90),
                   ('L',  50),
                   ('XL', 40),
                   ('X',  10),
                   ('IX', 9),
                   ('V',  5),
                   ('IV', 4),
                   ('I',  1))

def toRoman(n):
    """convert integer to Roman numeral"""
    result = ''
    for numeral, integer in romanNumeralMap:
        while n >= integer:
            result += numeral
            n -= integer
    return result

#Паттерн правильного формата
romanNumeralPattern = re.compile("""
    ^                   # beginning of string
    M{0,4}              # thousands - 0 to 4 M's
    (CM|CD|D?C{0,3})    # hundreds - 900 (CM), 400 (CD), 0-300 (0 to 3 C's),
                        #            or 500-800 (D, followed by 0 to 3 C's)
    (XC|XL|L?X{0,3})    # tens - 90 (XC), 40 (XL), 0-30 (0 to 3 X's),
                        #        or 50-80 (L, followed by 0 to 3 X's)
    (IX|IV|V?I{0,3})    # ones - 9 (IX), 4 (IV), 0-3 (0 to 3 I's),
                        #        or 5-8 (V, followed by 0 to 3 I's)
    $                   # end of string
    """ ,re.VERBOSE)

def fromRoman(s):
    """convert Roman numeral to integer"""
    result = 0
    index = 0
    for numeral, integer in romanNumeralMap:
        while s[index:index+len(numeral)] == numeral:
            result += integer
            index += len(numeral)
    return result

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

@app.route('/convert', methods=['POST'])
def convert():
    rf=request.form
    target=rf['number']

    if not target or target=='NaN':                                 # Если ввод не произведен 
        res = jsonify({'conv':'', 'msg':'Input can not be blank'})   
        res.headers['Access-Control-Allow-Origin']='*'
        write_to_db('NaN', 'Input can not be blank')
        return res                                                  
        
    if target.isdigit():                                            # Если было введено число
        if not (0 < int(target) < 5000):
            resp = jsonify({'conv':'', 'msg':'number out of range (must be 1..4999)'})
            resp.headers['Access-Control-Allow-Origin']='*'
            write_to_db(target, 'number out of range (must be 1..4999)')
            return resp

        resp = jsonify({'conv':toRoman(int(target)), 'msg':'conversion performed'})
        resp.headers['Access-Control-Allow-Origin']='*'
        write_to_db(target, toRoman(int(target)))
        return resp

    if not romanNumeralPattern.search(target):                      # Если было введено Римское число в неправильном формате
        resp = jsonify({'conv':'', 'msg':'Invalid'})
        resp.headers['Access-Control-Allow-Origin']='*'
        write_to_db(target, 'Invalid')
        return resp
    else: 
        resp = jsonify({'conv':fromRoman(str(target)), 'msg':'conversion performed'})   # Если было введено Римское число в правильном формате
        resp.headers['Access-Control-Allow-Origin']='*'
        write_to_db(target, fromRoman(str(target)))
        return resp
    