# app.py
import preprocess

from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import numpy
import datetime
import os
import glob
import cv2
import easyocr

from jamo import h2j, j2hcj  # 단어를 자모음으로 분리
from jamo import j2h  # 자모음을 단어로 합치기
from jamo import hangul_to_jamo
from fuzzywuzzy import fuzz
import han2jamo
from han2jamo.han2jamo import Han2Jamo
import re
#from IPython.display import Image
import PIL
from PIL import ImageDraw
from PIL import Image


# Flask 객체 인스턴스 생성
app = Flask(__name__)

# db연결
app.config['MYSQL_HOST'] = 'capstone.chixozeplgcc.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'gani'
app.config['MYSQL_PASSWORD'] = 'capstone'
app.config['MYSQL_DB'] = 'capstone'

mysql = MySQL(app)

@app.route('/') # 접속하는 url
def index():
   # db연결
   cur = mysql.connection.cursor()
   cur.execute("select material from vegan1 where vegan=0;")
   fetchdata = cur.fetchall()
   #print(fetchdata)
   #print(type(fetchdata))
   cur.close()
   return render_template('index.html', data=fetchdata)


@app.route('/crop', methods=['POST'])
def upload_done():
   global type

   #입력받은 이미지 저장
   uploaded_files = request.files["image"]
   nowDate = datetime.datetime.now()
   save_name = "assets/img/user/{}.jpg".format(nowDate.strftime("%Y%m%d%H%M"))
   uploaded_files.save("static/"+save_name)

   #채식단계 저장
   type = request.form['type']
   #print(type)

   return render_template('crop.html',image_file = save_name)
"""
   #사이즈조절 
   uploaded_files= Image.open('static/'+save_name)
   w,h = uploaded_files.size
   #print('height: ', h)
   #print('weight: ',w)
   re_h = (500*h)/w
   #print('re_h: ',re_h)
   uploaded_files = uploaded_files.resize((500,int(re_h)))

   nowDate = datetime.datetime.now()
   save_name = "assets/img/user/{}.jpg".format(nowDate.strftime("%Y%m%d%H%M"))
   uploaded_files.save("static/"+save_name)
"""






@app.route('/predict', methods=['POST']) # 접속하는 url
def predict():
   global type
   if request.method=='POST':

      list_of_files = glob.glob('static/assets/img/user/*.jpg')
      latest_file = max(list_of_files, key=os.path.getctime)
      #print (latest_file)

      #f = cv2.imread(latest_file)
      reader = easyocr.Reader(['ko'])

      '''

      # Draw bounding boxes
      def draw_boxes(image_name, bounds, color='yellow', width=2):
         img = cv2.imread(image_name)
         draw = ImageDraw.Draw(PIL.Image.open(image_name))
         for bound in bounds:
            p0, p1, p2, p3 = bound[0]
            draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
            # cv2_imshow(img[p0[1]:p2[1],p0[0]:p2[0]])
            print(reader.readtext(img[p0[1]:p2[1], p0[0]:p2[0]])[0][1])

      img_name = '갈비탕원재료명.png'
      output = reader.readtext(img_name)
      draw_boxes(img_name, output)
      ###################
      
      def draw_boxes(img, bounds,):
         for bound in bounds:
            p0, p1, p2, p3 = bound[0]
            # cv2_imshow(img[p0[1]:p2[1],p0[0]:p2[0]])
            print(reader.readtext(img[p0[1]:p2[1], p0[0]:p2[0]])[0][1])
      '''
      #img = cv2.imdecode(numpy.fromstring(request.files['image'].read(),numpy.uint8),cv2.IMREAD_UNCHANGED)

      output = reader.readtext(latest_file)

      print(request.form['crop_location'])
      lo = request.form['crop_location'].split(",")
      org_pts = [[lo[0],lo[1]], [lo[2],lo[3]], [lo[6],lo[7]] , [lo[4],lo[5]] ]
      prep = preprocess.Preprocess(cv2.imread(latest_file), org_pts)
      prep_result = prep.allResult()
      
      output_text_list = [a[1] for a in output]
      output_text=''.join(output_text_list)
      print("인식 결과 : ")
      print(prep_result)
      print(type)


      ##후처리
      han2jamo = Han2Jamo()

      # 1차 수정 : i, I=> 1 /////// O=>0
      prep_result = re.sub('i', '1', prep_result)
      prep_result = re.sub('I', '1', prep_result)
      prep_result = re.sub('O', '0', prep_result)
      prep_result = re.sub(r'([^\u3131-\u3163\uac00])}', '\\1, ', prep_result)

      # 2차 수정 : 숫자, %, 닫는 괄호 제거
      pattern2 = ['\)', ']', r'{[^a-zA-Z]{\d+}}', r'\d+[.]\d+', r'\d+[,]\d+',
               r'[\u3131-\u3163\uac00-\ud7a3]+\d+', r'\d+[\u3131-\u3163\uac00-\ud7a3]',
               r' \d+', r'^\d+', '%', r', {2,}']

      for pat in pattern2:
         prep_result = re.sub(pat, ' ', prep_result)

      # 3차 수정 : 공백 제거
      prep_result = re.sub(' ', '', prep_result)
      picture_words = re.split(r'[,\({|]', prep_result)

      # db에서 성분명 가져오기
      cur = mysql.connection.cursor()
      cur.execute('select material from vegan1')
      fetchdata = cur.fetchall()
      db_words = [data[0] for data in fetchdata]
      #print(db_words)

      db_jamo = [j2hcj(h2j(x)) for x in db_words]  # db에 있는 단어 자모 분리해서 리스트에
      db_jamo = [re.sub('ㅚ', 'ㅗㅣ', word) for word in db_jamo] # ㅚ를 ㅗㅣ로

      picture_jamo = [j2hcj(h2j(x)) for x in picture_words]  # 사진으로 찍은 단어 자모 분리해서 리스트에
      picture_jamo = [re.sub('ㅚ', 'ㅗㅣ', word) for word in picture_jamo] # ㅚ를 ㅗㅣ로

      final_list = [db_word for db_word in db_jamo for pic_word in picture_jamo if
      fuzz.ratio(db_word, pic_word) >= 70]
      final_list = [re.sub('ㅗㅣ', 'ㅚ', word) for word in final_list]
      accuracy70_word = [han2jamo.jamo_to_str(x) for x in final_list]
      temp = set(accuracy70_word)

      accuracy70_word = list(temp)  # accuracy70_word에서 중복 제거된 것


      # 데이터베이스 부분
      if type == 'vegan':
      	typestr = '비건'
      elif type == 'ovo':
      	typestr = '오보'
      elif type == 'lacto':
      	typestr = '락토'
      elif type == 'lactoovo':
      	typestr = '락토오보'
      elif type == 'pesco':
      	typestr = '페스코'
      else:
      	typestr = '폴로/세미'


      vegan_yn = typestr + ' 단계에서 섭취할 수 있습니다'
      cur = mysql.connection.cursor()
      vegan_step = type
      statement = 'select material from vegan1 where {step}=0;'.format(step=vegan_step)
      cur.execute(statement)
      fetchdata = cur.fetchall()
      for i in fetchdata:
      	if (i[0] in prep_result):
      		vegan_yn = typestr + ' 단계에서 섭취할 수 없습니다'
      		print(i[0])
      		break 
      	elif (i[0] in accuracy70_word):
      		vegan_yn = typestr + ' 단계에서 섭취할 수 없습니다'
      		print(i[0])
      		break
      print(vegan_yn)
      cur.close()


   return render_template('predict.html',data=vegan_yn)

if __name__=="__main__":
   app.run(debug=True)
# host 등을 직접 지정하고 싶다면
# app.run(host="127.0.0.1", port="8000", debug=True)