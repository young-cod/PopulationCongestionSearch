from flask import Flask
from flask import url_for
from flask import render_template # html 문서 로드
from flask import request # 요청 관련 라이브러리
from flask import jsonify  # jsonify 추가
from flask import Response  # Response 추가
from flask import flash, redirect  # flash와 redirect 추가
from werkzeug.utils import secure_filename
from urllib.parse import quote

import Label # Detect label
import Analyze # Analyze face
import Compare # Compare face
import Celebrity # Celebrities search
import Wikipedia # Wikipedia Search
import os # system 관련 라이브러리

# app.py에 정적 파일 설정 추가
app = Flask(__name__, static_url_path='', static_folder='static')


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

    return render_template("label.html", result=result)

@app.route('/analyze', methods = ['POST'])
def analyze():
    if request.method == 'POST':
        f = request.files['analyze']
        filename = secure_filename(f.filename)
        f.save('static/imgs/' + filename) 

        # 도착한 사진의 경로 r을 전달하자
        r = 'static/imgs/' + filename
        result = Analyze.detect_faces(r)

        # analyze.html 템플릿에 맞게 데이터 구조화
        formatted_result = []
        for face in result:
            item = {
                'name': '감정 분석',
                'confidence': round(face['Confidence'], 2),
                'tags': [
                    f"나이: {face['AgeRange']['Low']}-{face['AgeRange']['High']}",
                    f"성별: {face['Gender']['Value']}",
                    f"감정: {face['Emotions'][0]['Type']}",
                    f"표정: {', '.join([e['Type'] for e in face['Emotions']])}"
                ]
            }
            formatted_result.append(item)

        return render_template("analyze.html",
                            result=formatted_result,
                            image_url=url_for('static', filename='imgs/' + filename))

@app.route('/compare',methods=['POST'])
def compare():
    if request.method == 'POST':
        sourceFile = request.files['compare1']
        sourceFilename = secure_filename_with_hangul(sourceFile.filename)
        targetFile = request.files['compare2']
        targetFilename = secure_filename_with_hangul(targetFile.filename)
        
        print(targetFile.filename)
        print(sourceFile.filename)

        sourceFile.save('static/imgs/' + sourceFilename)
        targetFile.save('static/imgs/' + targetFilename)
        
        sf = 'static/imgs/' + sourceFilename
        tf = 'static/imgs/' + targetFilename

        result = Compare.compare_faces(sf,tf)
        
        return render_template('compare_result.html', 
                               result=result,
                               source_image=url_for('static', filename='imgs/' + sourceFilename),
                               target_image=url_for('static', filename='imgs/' + targetFilename))
    
@app.route('/celebrity',methods=['POST','GET'])
def celebrites():
     if request.method == 'POST':
        targetFile = request.files['celebrity']
        targetFilename = secure_filename(targetFile.filename)

        targetFile.save('static/imgs/' + targetFilename)

        tf = 'static/imgs/' + targetFilename

        result = Celebrity.recognize_celebrities(tf)
        
        if result is None:
                flash("닮은 사람을 찾을 수 없습니다.")
                return redirect(request.url)
        
        # 위키 검색 결과
        keyword = result['Name']
        text, imgs = Wikipedia.search(keyword)
        print("결과 : ", Response(imgs,mimetype='text/plain'))
        # s = f'닮은 사람 : {result["Name"]} \n닮은 정도 : {result["MatchConfidence"]} \n url : {result["Urls"][0]}'

        return render_template('celebrity.html', 
                               target_image=url_for('static', filename='imgs/' + targetFilename),
                               name=result['Name'],
                               MatchConfidence=round(result['MatchConfidence'],2),
                               celebritesUrl=result['Urls'][0],
                               img_url=imgs[0] if imgs else None,
                               text=text if text else None
                               )

@app.route('/wiki', methods=['POST', 'GET'])
def wiki():
    keyword = request.args['keyword']
    if not keyword:
        return jsonify({"error": "No keyword provided"}), 400
    
    text, imgs = Wikipedia.search(keyword)
    
    # 이미지 URL 목록만 반환
    # {url1
    #  url2
    #  url3
    #  .
    #  .
    #  .}
    url_string = '\n'.join(imgs)

    # 일반 텍스트로 응답을 반환합니다.
    return Response(url_string, mimetype='text/plain')

def secure_filename_with_hangul(filename):
    """한글 파일명을 안전하게 처리하는 함수"""
    # 확장자 분리
    name, ext = os.path.splitext(filename)
    # URL 인코딩 (한글 보존)
    safe_name = quote(name)
    return safe_name + ext

if __name__ == '__main__':
    app.run()