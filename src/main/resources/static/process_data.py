import os
import common
import csv
import datetime
import time
import pandas as pd
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


# 究竟是最近一次入院的影响，还是之前多次诊断的影响？
# 返回患者最后一次入院的visit_id
def get_readmission(path, patient_id_list=None):
    conn = common.get_connection()
    visit_dict = dict()
    discharged_time = dict()
    with conn.cursor() as cursor:
        # sql = "select patient_id, max(visit_id) from pat_visit where visit_id>=2 group by patient_id "
        # sql = "select patient_id,max(visit_id),discharge_date_time from pat_visit group by patient_id, discharge_date_time"
        sql = "select patient_id,max(visit_id),discharge_date_time from pat_visit where visit_id>=2 group by patient_id, discharge_date_time"
        for row in cursor.execute(sql):
            visit_dict[row[0]] = row[1]
            discharged_time[row[0]] = row[2]

    if patient_id_list is None:
        pass
    else:
        selected_dict = dict()
        for item in patient_id_list:
            selected_dict[item] = str(visit_dict[item])
        visit_dict = selected_dict

    with open(path, 'w', encoding='utf-8-sig', newline="") as file:
        matrix_to_write = []
        csv_write = csv.writer(file)
        head = ['pat_id', 'visit_id', 'discharged_time']
        matrix_to_write.append(head)
        for patient_id in visit_dict:
            line = list()
            line.append(patient_id)
            line.append(visit_dict[patient_id])
            line.append(discharged_time[patient_id])
            matrix_to_write.append(line)
        csv_write.writerows(matrix_to_write)
    return visit_dict


def get_id_list(p):
    id_l = pd.read_csv(p, encoding='UTF-8')
    col = ['pat_id']
    id_s = pd.DataFrame(id_l, columns=col)
    id_list = id_s['pat_id'].tolist()
    return id_list


def get_visit_id(p):
    visit_id = pd.read_csv(p, encoding='UTF-8')
    col = ['visit_id']
    visit_s = pd.DataFrame(visit_id, columns=col)
    visit_list = visit_s['visit_id'].tolist()
    return visit_list


def get_because_of_hf(id_list, visit_list, path):
    conn = common.get_connection()
    readmission_dict = dict()
    with conn.cursor() as cursor:
        sql = "select patient_id, max(visit_id), diagnosis_desc from diagnosis where diagnosis_type='A' and " \
              "REGEXP_LIKE(diagnosis_desc,'心|尖瓣|房颤|冠脉|冠状动脉|动脉|早搏') group by patient_id,diagnosis_desc"
        for row in cursor.execute(sql):
            if row[0] not in readmission_dict:
                if row[0] in id_list and row[1] in visit_list:
                    readmission_dict[row[0]] = 1

    with open(path, 'r', encoding='UTF-8', newline="") as file:
        csv_reader = csv.reader(file)
        lines = []
        for i, line in enumerate(csv_reader):
            if i == 0:
                line.append("是否心源性再入院")
            else:
                patient_id = line[0]
                line.append(str(readmission_dict.get(patient_id, -1)))
            lines.append(line)

    with open(path, 'w', encoding='UTF-8', newline="") as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    return readmission_dict


def get_pharmacy(id_list, mapping_file, path):
    conn = common.get_connection()
    angiotensin_name_map = dict()
    with open(mapping_file, 'r', encoding='gbk', newline='') as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            for i in range(1, len(line)):
                if len(line[i]) <= 1:
                    continue
                angiotensin_name_map[line[i]] = line[0]
#最后要返回的是angiotensin_dict
    angiotensin_dict = dict()
    for patient_id in id_list:
        angiotensin_dict[patient_id] = {'ACEI': 0, 'ARB': 0, 'ARNI': 0}
    cursor = conn.cursor()
    #开始修改emmm
    sql = "select patient_id, order_text from orders temp1 where order_class = 'A' and temp1.visit_id < (select temp2.maxid from (select patient_id, max(visit_id) as maxid from orders group by patient_id) temp2 where temp1.patient_id = temp2.patient_id) "
    for row in cursor.execute(sql):
        patient_id, order_text = row
        if patient_id in id_list:
            for item in angiotensin_name_map:
                if order_text is not None and item in order_text:
                    normalized_name = angiotensin_name_map[item]
                    if normalized_name == 'ACEI':
                        angiotensin_dict[patient_id]['ACEI'] = 1
                    if normalized_name == 'ARB':
                        angiotensin_dict[patient_id]['ARB'] = 1
                    if normalized_name == 'ARNI':
                        angiotensin_dict[patient_id]['ARNI'] = 1

    with open(path, 'r', encoding='utf-8', newline="") as file:
        csv_reader = csv.reader(file)
        lines = []
        for i, line in enumerate(csv_reader):
            if i == 0:
                line.append("ACEI")
                line.append("ARB")
                line.append("ARNI")
            else:
                patient_id = line[0]
                result = angiotensin_dict.get(patient_id, [-1, -1, -1])
                if isinstance(result, dict):
                    result = [result['ACEI'], result['ARB'], result['ARNI']]
                line.extend(result)
            lines.append(line)

    with open(path, 'w', encoding='UTF-8', newline="") as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    return angiotensin_dict


def get_diuretic(id_list, mapping_file, path):
    conn = common.get_connection()
    diuretic_name_map = dict()
    with open(mapping_file, 'r', encoding='gbk', newline="") as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            for i in range(1, len(line)):
                if len(line[i]) <= 1:
                    continue
                diuretic_name_map[line[i]] = line[0]

    diuretic_dict = dict()
    for patient_id in id_list:
        # diuretic_dict[patient_id] = {'保钾利尿剂': 0, '袢利尿剂': 0, '噻嗪类利尿剂': 0, '受体拮抗剂': 0}
        diuretic_dict[patient_id] = {'Potassium diuretic': 0, 'Urine diuretic': 0, 'Thiazide diuretic': 0, 'Receptor antagonist': 0}
    cursor = conn.cursor()
    sql = "select patient_id, order_text from orders temp1 where order_class = 'A' and " \
          "temp1.visit_id < (select temp2.maxid from (select patient_id, max(visit_id) as maxid " \
          "from orders group by patient_id) temp2 where temp1.patient_id = temp2.patient_id) "
    for row in cursor.execute(sql):
        patient_id, order_text = row
        if patient_id in id_list:
            for item in diuretic_name_map:
                if order_text is not None and item in order_text:
                    normalized_name = diuretic_name_map[item]
                    if normalized_name == 'Potassium diuretic':
                        diuretic_dict[patient_id]['Potassium diuretic'] = 1
                    if normalized_name == 'Urine diuretic':
                        diuretic_dict[patient_id]['Urine diuretic'] = 1
                    if normalized_name == 'Thiazide diuretic':
                        diuretic_dict[patient_id]['Thiazide diuretic'] = 1
                    if normalized_name == 'Receptor antagonist':
                        diuretic_dict[patient_id]['Receptor antagonist'] = 1

    with open(path, 'r', encoding='utf-8', newline="") as file:
        csv_reader = csv.reader(file)
        lines = []
        for i, line in enumerate(csv_reader):
            if i == 0:
                line.append("Potassium diuretic")
                line.append("Urine diuretic")
                line.append("Thiazide diuretic")
                line.append("Receptor antagonist")
            else:
                patient_id = line[0]
                result = diuretic_dict.get(patient_id, [-1, -1, -1, -1])
                if isinstance(result, dict):
                    result = [result['Potassium diuretic'], result['Urine diuretic'], result['Thiazide diuretic'], result['Receptor antagonist']]
                line.extend(result)
            lines.append(line)

    with open(path, 'w', encoding='UTF-8', newline="") as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    return diuretic_dict


def get_beta(id_list, mapping_file, path):
    conn = common.get_connection()
    beta_name_map = dict()
    with open(mapping_file, 'r', encoding='gbk', newline="") as file:
        csv_reader = csv.reader(file)
        for line in csv_reader:
            for i in range(1, len(line)):
                if len(line[i]) <= 1:
                    continue
                beta_name_map[line[i]] = line[0]

    beta_dict = dict()
    for patient_id in id_list:
        beta_dict[patient_id] = {'Metoprolol': 0, 'Bisoprol': 0, '卡维地洛': 0}
    cursor = conn.cursor()
    sql = "select patient_id, order_text from orders temp1 where order_class = 'A' and " \
          "temp1.visit_id < (select temp2.maxid from (select patient_id, max(visit_id) as maxid " \
          "from orders group by patient_id) temp2 where temp1.patient_id = temp2.patient_id) "
    for row in cursor.execute(sql):
        patient_id, order_text = row
        if patient_id in id_list:
            for item in beta_dict:
                if order_text is not None and item in order_text:
                    normalized_name = beta_name_map[item]
                    if normalized_name == 'Metoprolol':
                        beta_dict[patient_id]['Metoprolol'] = 1
                    if normalized_name == 'Bisoprol':
                        beta_dict[patient_id]['Bisoprol'] = 1
                    if normalized_name == 'Carvedilol':
                        beta_dict[patient_id]['Carvedilol'] = 1

    with open(path, 'r', encoding='utf-8', newline="") as file:
        csv_reader = csv.reader(file)
        lines = []
        for i, line in enumerate(csv_reader):
            if i == 0:
                line.append("Metoprolol")
                line.append("Bisoprol")
                line.append("Carvedilol")
            else:
                patient_id = line[0]
                result = beta_dict.get(patient_id, [-1, -1, -1, -1])
                if isinstance(result, dict):
                    result = [result['Metoprolol'], result['Bisoprol'], result['Carvedilol']]
                line.extend(result)
            lines.append(line)

    with open(path, 'w', encoding='UTF-8', newline="") as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    return beta_dict


def get_admission_date(id_list, path):
    conn = common.get_connection()
    admission_date_dict = dict()
    with conn.cursor() as cursor:
        sql = "select patient_id,visit_id,discharge_date_time from pat_visit where visit_id = 1"
        for row in cursor.execute(sql):
            if row[0] not in admission_date_dict:
                if row[0] in id_list:
                    admission_date_dict[row[0]] = row[2]

    with open(path, 'r', encoding='UTF-8', newline="") as file:
        csv_reder = csv.reader(file)
        lines = []
        for i, line in enumerate(csv_reder):
            if i == 0:
                line.append("admission_date_time")
            else:
                patient_id = line[0]
                line.append(str(admission_date_dict.get(patient_id, -1)))
            lines.append(line)
    with open(path, 'w', encoding='UTF-8', newline="") as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    return admission_date_dict


def get_discharge_date(id_list, visit_list, path):
    conn = common.get_connection()
    admission_date_dict = dict()
    with conn.cursor() as cursor:
        sql = "select patient_id,max(visit_id),discharge_date_time from pat_visit group by patient_id, discharge_date_time"
        for row in cursor.execute(sql):
            if row[0] not in admission_date_dict:
                if row[0] in id_list and row[1] in visit_list:
                    admission_date_dict[row[0]] = row[2]

    with open(path, 'r', encoding='UTF-8', newline="") as file:
        csv_reder = csv.reader(file)
        lines = []
        for i, line in enumerate(csv_reder):
            if i == 0:
                line.append("discharge_date_time")
            else:
                patient_id = line[0]
                line.append(str(admission_date_dict.get(patient_id, -1)))
            lines.append(line)
    with open(path, 'w', encoding='UTF-8', newline="") as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    return admission_date_dict


def get_interval(path):
    with open(path, 'r', encoding='ISO-8859-1', newline="") as file:
        csv_reader = csv.reader(file)
        lines = []
        for i, line in enumerate(csv_reader):
            if i == 0:
                line.append("interval")
            elif line[4] != '-1':
                if line[2].count(":") == 2:
                    date1 = datetime.datetime.strptime(line[2], "%Y/%m/%d %H:%M:%S")
                elif line[2].count(":") == 1:
                    date1 = datetime.datetime.strptime(line[2], "%Y/%m/%d %H:%M")
                else:
                    date1 = datetime.datetime.strptime(line[2], "%Y/%m/%d")
                if line[4].count(":") == 2:
                    date2 = datetime.datetime.strptime(line[4], "%Y/%m/%d %H:%M:%S")
                elif line[4].count(":") == 1:
                    date2 = datetime.datetime.strptime(line[4], "%Y/%m/%d %H:%M")
                else:
                    date2 = datetime.datetime.strptime(line[4], "%Y/%m/%d")
                interval = date1 - date2
                line.append(interval.days)
            else:
                line.append(-1)
            lines.append(line)

    with open(path, 'w', encoding='UTF-8', newline="") as file:
        writer = csv.writer(file)
        writer.writerows(lines)

path = 'G:\\plahf_OR\\Resources\\java_python.csv'
# path = 'I:\\plahf_OR\\Resources\\patient_visit.csv'
get_readmission(path)
get_because_of_hf(get_id_list(path), get_visit_id(path), path)
get_admission_date(get_id_list(path), path)
mapping_file = 'G:\\plahf_OR\\Resources\\药品名称映射.csv'
get_pharmacy(get_id_list(path), mapping_file, path)
get_diuretic(get_id_list(path), mapping_file, path)
get_beta(get_id_list(path), mapping_file, path)
get_interval(path)
