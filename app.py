"""
Загрузка файлов в базу данных и
Загрузка файла из базы данных flask
"""

import sqlalchemy
from flask import Flask, render_template, request, flash, send_file
from flask_sqlalchemy import SQLAlchemy  # Модуль для подключенния к базе данных.
from io import BytesIO

UPLOAD_FOLDER = '/Pictures/Uplay/'  # Путь по которому загружаем файлы.

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog2.db'  # Путь до базы данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'fgvfhghyhgddfrrghghg'  # Секретный ключ для передачи собщений.
db = SQLAlchemy(app)


class File(db.Model):
    # Создаем таблицу в базе данных
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        # Обрабатываем метод POST
        file = request.files['file'] # Получаем файл из формы.
        newfile = File(name=file.filename, data=file.read()) # Приописываем параметры
        try:
            db.session.add(newfile)
            db.session.commit()
        except:
            return 'Не удалось загрузить файл в базу данных.'

        return 'Файл загружен в базу данных.'
    else:

        return render_template('file.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    try:
        images = File.query.all()  # Список файлов в базе данных.
    except sqlalchemy.exc.OperationalError:
        images = []
    if request.method == 'POST':  # Обрабатываем метод POST
        try:
            name_file = request.form.get('sel')  # Получаем мя файла который хотим скачать из базы данных.
            try:
                file = File.query.filter_by(name=name_file).first()
                file = (BytesIO(file.data))
                with open(f'{UPLOAD_FOLDER}{name_file}', 'bw')as f:  # Читаем файл из базы данных ,потом записываем его с нужную деректорию
                    f.write(file.read())
                flash(f'Файл сохранен в { UPLOAD_FOLDER} ')  # Сообщаем что файл скачан.
                return render_template('download.html', images=images)
                #return send_file(BytesIO(file.data), attachment_filename='rrr.png', as_attachment=True)
            except FileNotFoundError:
                flash('Ошибка скачавиния(такого файла нет)')  # Сообщаем что файл скачан.
                return render_template('download.html', images=images)
        except sqlalchemy.exc.OperationalError:
            pass
    else:
        # Если в базе данный нет файлов,сообщаем об этом
        if len(images) == 0:
            flash('Файлы отсутсвуют')
            return render_template('download.html')
        else:
            return render_template('download.html', images=images)


if __name__ == '__main__':
    app.run(debug=True)
