from flask import Flask, render_template, request
import os
import json
from datetime import datetime

app = Flask(__name__)

# Определение текущей директории
base_dir = os.path.dirname(os.path.abspath(__file__))
etalon_dir = os.path.join(base_dir, 'ResultEtalon')
test_dir = r'C:\Users\TEMP.HOME-PC.004\PycharmProjects\SQL_Tester_new_Version_v1\Тестируемые'

def load_etalon_data():
    etalon_data = {}
    for filename in os.listdir(etalon_dir):
        if filename.startswith('Task_'):
            task_id = filename.replace('Task_', '').replace('.json', '')
            with open(os.path.join(etalon_dir, filename), 'r', encoding='utf-8') as file:
                etalon_data[task_id] = json.load(file)
    return etalon_data

def compare_results(user_result, etalon_result):
    return user_result == etalon_result

@app.route('/')
def index():
    etalon_data = load_etalon_data()
    test_results = {}

    for user_dir in os.listdir(test_dir):
        user_path = os.path.join(test_dir, user_dir)
        if os.path.isdir(user_path):
            creation_time = datetime.fromtimestamp(os.path.getctime(user_path))
            creation_date_str = creation_time.strftime('%Y-%m-%d')
            results = {}
            total = 0
            for task_id in etalon_data:
                user_file = os.path.join(user_path, f'Task_{task_id}.json')
                if os.path.exists(user_file):
                    with open(user_file, 'r', encoding='utf-8') as file:
                        user_data = json.load(file)
                    match = compare_results(user_data["result"], etalon_data[task_id]["result"])
                    results[task_id] = match
                    total += int(match)  # Суммируем количество совпадений
                else:
                    results[task_id] = False
            test_results[user_dir] = {'results': results, 'total': total, 'creation_date': creation_date_str}

    return render_template('index.html', test_results=test_results)

@app.route('/details')
def details():
    user = request.args.get('user')
    task_id = request.args.get('task')
    etalon_data = load_etalon_data()

    user_file_path = os.path.join(test_dir, user, f'Task_{task_id}.json')
    if os.path.exists(user_file_path):
        with open(user_file_path, 'r', encoding='utf-8') as file:
            user_data = json.load(file)
    else:
        user_data = {"query": "Файл не найден", "result": [], "error": None}

    etalon_data = etalon_data.get(task_id, {"query": "Эталон не найден", "result": [], "error": None})

    # Убеждаемся, что у нас всегда есть список результатов
    user_results = user_data.get('result', []) if user_data.get('result') is not None else []
    etalon_results = etalon_data.get('result', []) if etalon_data.get('result') is not None else []

    return render_template('detail.html', user=user, task_id=task_id, user_data=user_data, etalon_data=etalon_data, user_results=user_results, etalon_results=etalon_results)


if __name__ == '__main__':
    app.run(debug=True)
