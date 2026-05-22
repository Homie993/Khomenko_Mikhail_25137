from flask import Flask, request, Response
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import List, Dict, Tuple, Optional, Any

# === Настройки Google Sheets ===
SPREADSHEET_ID: str = "1Jl0OhcH-LhXsI9fIo58pIfEPMrOuBKUHLq_-udr7OjA"
CREDENTIALS_FILE: str = "credentials.json"

def fetch_sheet_data() -> Tuple[List[str], List[List[str]]]:
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Итог'"
    ).execute()
    values = result.get("values", [])
    if not values:
        raise Exception("Лист 'Итог' пуст")
    headers = values[0]
    headers = headers[0:headers.index('Оценка')+1]

    len_h = len(headers)
    rows = []
    for i in values[1:]:
        if len(i) >= len_h:
            for j in range(1, len(i)):
                if not i[j]:
                    i[j] = '0'
            i = i[0:len_h]
            rows.append(i)

    return headers, rows

#Хард-код на Flask
app = Flask(__name__)


@app.route('/names')
def get_names() -> Dict[str, List[str]]:
    try:
        headers, rows = fetch_sheet_data()
        if "ФИ" not in headers:
            return {"error": "Колонка 'ФИ' не найдена"}, 500
        name_index = headers.index("ФИ")
        names = [row[name_index] for row in rows if len(row) > name_index and row[name_index]]
        return {"names": names}
    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/mean_score')
@app.route('/<hw_name>/<group_id>/mean_score')
@app.route('/<hw_name>/mean_score')
def mean_score_hw(hw_name: Optional[str] = None, group_id: Optional[str] = None) -> Response:
    try:
        if hw_name is None:
            hw_name = request.args.get('hw_name')
        if group_id is None:
            group_id = request.args.get('group_id')

        headers, rows = fetch_sheet_data()
        row_index = 0
        if hw_name in headers:
            row_index = headers.index(hw_name)

        if (row_index >= headers.index('Сумма') or row_index <= headers.index('Группа')):
            return Response(f'ДЗ {hw_name} не найдено, или оно расположено после столбца Сумма', mimetype='text/plain')
        else:
            total_sum, count = 0, 0
            if group_id:
                for i in rows:
                    if i[headers.index('Группа')] == group_id:
                        total_sum += int(i[row_index])
                        count += 1
                if count == 0:
                    return Response(f'Группа {group_id} пуста или не существует', mimetype='text/plain')
                return Response(f'Всего учеников в группе {group_id}: {count} \nСредний балл за {hw_name} в группе {group_id}: {(total_sum / count):.2f}', mimetype='text/plain')
            for i in rows:
                total_sum += int(i[row_index])
                count += 1
            return Response(f'Всего учеников: {count} \nСредний балл за {hw_name}: {(total_sum / count):.2f}', mimetype='text/plain')

    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/mark')
def mark() -> Response:
    try:
        headers, rows = fetch_sheet_data()
        student_id_str = request.args.get('student_id')
        group_id_str = request.args.get('group_id')

        if student_id_str:
            student_id = int(student_id_str)
            mark_val = rows[student_id - 1][headers.index('Оценка')]
            score = int(rows[student_id - 1][headers.index('Сумма')])
            real_mark = 2
            if score > 50:
                real_mark = 5
            elif 30 <= score <= 50:
                real_mark = 4
            elif score > 0:
                real_mark = 3
            
            name_st = rows[student_id - 1][headers.index('ФИ')]
            return Response(f'Student_id: {student_id}\nСтудент: {name_st}\nОценка: {mark_val}\nОценка по критериям: {real_mark}', mimetype='text/plain')
        elif group_id_str:
            sum1, count1, real_sum = 0, 0, 0
            group_in_table = headers.index('Группа')
            mark_in_table = headers.index('Оценка')
            score_in_table = headers.index('Сумма')
            for i in rows:
                if i[group_in_table] == group_id_str:
                    count1 += 1
                    sum1 += int(i[mark_in_table])
                    score_val = int(i[score_in_table])
                    if score_val > 50:
                        real_sum += 5
                    elif 30 <= score_val <= 50:
                        real_sum += 4
                    elif score_val > 0:
                        real_sum += 3
                    else:
                        real_sum += 2

            if count1 == 0:
                return Response(f'Группа {group_id_str} не найдена', mimetype='text/plain')
            return Response(f'Группа {group_id_str} \nЧеловек в группе: {count1}\nСредняя оценка: {(sum1 / count1):.2f}\nСредняя оценка по критериям: {(real_sum / count1):.2f}', mimetype='text/plain')
        else:
            return {"error": "Укажите student_id или group_id"}, 400

    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/course_table')
def course_table() -> str:
    hw_name = request.args.get('hw_name')
    group_id = request.args.get('group_id')

    if not hw_name:
        return {"error": "Parameter 'hw_name' is required"}, 400

    headers, rows = fetch_sheet_data()

    try:
        FI_in_table = headers.index('ФИ')
        group_in_table = headers.index('Группа')
        sum_in_table = headers.index('Сумма')
    except ValueError as e:
        return {"error": f"Required column missing: {e}"}, 500

    start_idx = group_in_table + 1
    end_idx = sum_in_table
    hw = None
    for i in range(start_idx, end_idx):
        if headers[i] == hw_name:
            hw = i
            break

    if hw is None:
        available = headers[start_idx:end_idx]
        return {
            "error": f"Column '{hw_name}' not found between 'Группа' and 'Сумма'. Available: {available}"
        }, 400

    filtered_rows = [
        row for row in rows
        if (not group_id) or (group_in_table < len(row) and row[group_in_table] == group_id)
    ]

    if not filtered_rows:
        return {"error": "No students match the criteria"}, 404

    html = f"""
    <html>
    <head><title>Course Table: {hw_name}</title></head>
    <body>
        <h2>Домашнее задание: {hw_name}</h2>
        <h3>Группа: {'все' if not group_id else group_id}</h3>
        <table border="1" cellpadding="8" cellspacing="0">
            <thead>
                <tr>
                    <th>ФИ</th>
                    <th>Группа</th>
                    <th>{hw_name}</th>
                </tr>
            </thead>
            <tbody>
    """

    for row in filtered_rows:
        fi = row[FI_in_table] if FI_in_table < len(row) else ''
        group = row[group_in_table] if group_in_table < len(row) else ''
        score = row[hw] if hw < len(row) else '0'
        score = score if score.isdigit() else '0'

        html += f"""
                <tr>
                    <td>{fi}</td>
                    <td>{group}</td>
                    <td>{score}</td>
                </tr>
        """

    html += """
            </tbody>
        </table>
    </body>
    </html>
    """

    return html


@app.route('/debug/sheets')
def debug_sheets() -> Dict[str, List[Dict[str, Any]]]:
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build("sheets", "v4", credentials=creds)
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = []
    for sheet in sheet_metadata['sheets']:
        title = sheet['properties']['title']
        gid = sheet['properties']['sheetId']
        sheets.append({"title": repr(title), "gid": gid})
    return {"sheets": sheets}


@app.route('/debug/headers')
def debug_headers() -> Dict[str, List[str]]:
    headers, _ = fetch_sheet_data()
    return {"raw_headers": [repr(h) for h in headers]}


@app.route('/debug/rows')
def debug_rows() -> Dict[str, List[str]]:
    _, rows = fetch_sheet_data()
    return {"raw_headers": [repr(r) for r in rows]}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, debug=True)