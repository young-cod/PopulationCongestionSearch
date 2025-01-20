from flask import Flask
from flask import url_for
from flask import render_template # html 문서 로드
from flask import request # 요청 관련 라이브러리
from werkzeug.utils import secure_filename

import Label # Detect label
import Compare # Compare face
import os # system 관련 라이브러리

app = Flask(__name__)

if not os.path.exists('static/imgs'):
    os.mkdir('static/imgs')

@app.route('/')
def home():
    return render_template('index.html')

# get, post 등 데이터를 수신하는 route에는 전송 방식을 명시!!
@app.route('/add', methods = ['GET', 'POST'])
def add():
    # 2개의 get으로 온 값을 받아서 더해서 출력!!
    # args : get방식 수신
    # form : post방식 수신

    num1 = int(request.args['num1'])
    num2 = int(request.args['num2'])
    s = '{} + {} = {}'.format(num1, num2, num1 + num2)
    return s


@app.route('/label', methods = ['POST'])
def label():
    # 전송방식 약한 체크
    if request.method == 'POST':
        f = request.files['label']
        filename = secure_filename(f.filename)
        f.save('static/imgs/' + filename) 

    # 도착한 사진의 경로 r을 전달하자
    r = 'static/imgs/' + filename
    result = Label.detect_labels_local_file(r)
    return result

@app.route('/compare',methods=['POST'])
def compare():
    if request.method == 'POST':
        sourceFile = request.files['sourceFile']
        sourceFilename = secure_filename(sourceFile.filename)
        targetFile = request.files['targetFile']
        targetFilename = secure_filename(targetFile.filename)
        
        sourceFile.save('static/imgs/' + sourceFilename)
        targetFile.save('static/imgs/' + targetFilename)
        
        sf = 'static/imgs/' + sourceFilename
        tf = 'static/imgs/' + targetFilename

        result = Compare.compare_faces(sf,tf)
        
        return render_template('compare_result.html', 
                               result=result,
                               source_image=url_for('static', filename='imgs/' + sourceFilename),
                               target_image=url_for('static', filename='imgs/' + targetFilename))
        return result
    
if __name__ == '__main__':
    app.run()