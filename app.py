#如果后期gmail邮件阻止访问，则点击链接，确认 https://accounts.google.com/DisplayUnlockCaptcha
#此处通过flask框架搭建网页，具体细节在书签flask中有介绍
#通过导入SQLAlchemy(类似psycopg2)来链接数据库PostgreSql

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from send_email import send_email
from sqlalchemy.sql import func 


app=Flask(__name__)

#此处为后期添加的heroku_postgresql_database_url. 另外 <?sslmode=require> 为后加入的部分，SSL接続のみ試行（规定接续类型？）
app.config['SQLALCHEMY_DATABASE_URI']='postgresql:/(the address of postgresql database in heroku)?sslmode=require'

#create an sqlalchemy object for flask application
db=SQLAlchemy(app)

class Data(db.Model):
    __tablename__="data"                                   
    id=db.Column(db.Integer, primary_key=True)                                     #创建主键，并定义类型
    email_=db.Column(db.String(120), unique=True)                                  #创建数据库的column，限制范围，并定义类型
    height_=db.Column(db.Integer)                                                  #创建数据库的column，并定义数据类型

    def __init__(self, email_, height_):                                           # 初始化
        self.email_=email_
        self.height_=height_

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success", methods=['POST'])
def success():
    if request.method=='POST':                                                      #request.method_ 'post', to submit the data to serve 
        email=request.form["email_name"]
        height=request.form["height_name"]
        if db.session.query(Data).filter(Data.email_==email).count() == 0:          #以下为数据库操作部分
            data=Data(email,height)
            db.session.add(data)
            db.session.commit()
            average_height=db.session.query(func.avg(Data.height_)).scalar()         #给数据库增加平均值一项并 scalar只提取数值。
            average_height=round(average_height,1)                                   #设定平均值小数点后一位，也可以设置2，或3
            count=db.session.query(Data.height_).count()                              #计算统计的总人数，一起发送给用户
            send_email(email, height, average_height, count)       
            return render_template("success.html")
    return render_template('index.html', 
    text="Seems like we've got something from that email address already!")

if __name__ == '__main__':
    app.debug=True
    app.run()
