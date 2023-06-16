import time
from dash import html
from pandas import DataFrame


def log(info):
    f = open('log.txt', 'a')
    f.write('{}\n'.format(info))
    f.close()


def get_current_shift():
    shift_duration = 12
    current_time_sec = int(time.time())
    if int(time.strftime("%H", time.localtime(current_time_sec))) >= 8:
        current_date = time.strftime("%d.%m.%Y", time.localtime(current_time_sec))
    else:
        current_date = time.strftime("%d.%m.%Y", time.localtime(current_time_sec - shift_duration * 60 * 60))

    start_time = int(time.mktime(time.strptime('08:00:00 {}'.format(current_date), '%H:%M:%S %d.%m.%Y')))
    next_day_shift_start_time = start_time + 24 * 60 * 60 
    #start_time_str = time.strftime("%H:%M %d.%m.%Y", time.localtime(start_time))
    end_time = start_time + shift_duration * 60 * 60
    if current_time_sec > end_time and current_time_sec < next_day_shift_start_time:
        shift = 'Ночь'
    else:
        shift = 'День'

    return shift, current_date


def mongo_count_saw(db, THEME, saw, start, end):
    l = []
    d = []

    out = dict()
    named_entities = {}
    start_sec = start
    end_sec = end
    #start_sec = time.mktime(time.strptime(start, '%H:%M:%S %d.%m.%Y'))
    #end_sec = time.mktime(time.strptime(end, '%H:%M:%S %d.%m.%Y'))
    named_entities['sec_time'] = {'$gt': start_sec, '$lt': end_sec}
    named_entities['saw'] = saw
    answer_field = ['L', 'L_uch', 'D']
    answer = db.find_manual(theme=THEME,
                            named_entities=named_entities,
                            answer_field=answer_field)
    out['count'] = len(answer)

    for rec in answer:
        l.append(rec['L'])
        d.append(rec['D'])
    
    if len(l) != 0:
        out['L'] = round(sum(l)/len(l), 2)
    else:
        out['L'] = 0

    if len(d) != 0:
        out['D'] = round(sum(d)/len(d), 2)
    else:
        out['D'] = 0

    return out


def mongo_last_records_df(db, THEME, limit, start_sec, end_sec, rev = True):
    out = dict()
    named_entities = {}
    date_str = time.strftime("%d.%m.%Y", time.localtime())
    #start_sec = time.mktime(time.strptime('00:00:00 01.07.2022', '%H:%M:%S %d.%m.%Y'))
    #end_sec = time.mktime(time.strptime('00:00:00 01.08.2022', '%H:%M:%S %d.%m.%Y'))
    #start_sec = time.mktime(time.strptime('00:00:00 {}'.format(date_str), '%H:%M:%S %d.%m.%Y'))
    #end_sec = time.mktime(time.strptime('23:59:59 {}'.format(date_str), '%H:%M:%S %d.%m.%Y'))
    named_entities['sec_time'] = {'$gt': start_sec, '$lt': end_sec}
    answer_field = ['date', 'time', 'saw', 'L', 'L_uch', 'D', 'sec_time']
    answer = db.find_manual(theme=THEME,
                            named_entities=named_entities,
                            answer_field=answer_field)

    sort = []
    for i in range(len(answer)):
        sort.append(sorted(answer[i].items(), key=lambda x: x[0]))

    if rev:
        sort.reverse()

    header = ['Дата', 'Время', 'Пила', 'L, мм', 'Lуч, мм', 'D, мм']
    d, t, saw, L, L_uch, diam = [], [], [], [], [], []

    for i in range(limit if (limit != -1) and (len(sort) >= limit) else len(sort)):
        d.append(sort[i][3][1])
        t.append(sort[i][6][1])
        saw.append(sort[i][4][1])
        L.append(sort[i][1][1])
        L_uch.append(sort[i][2][1])
        diam.append(sort[i][0][1])

    data = dict()
    #data[header[0]] = d
    data[header[1]] = t
    data[header[2]] = saw
    #data[header[3]] = L
    data[header[4]] = L_uch
    data[header[5]] = diam

    df = DataFrame(data)

    return df

def mongo_report(db, THEME, limit, start_sec, end_sec, rev = True):
    out = dict()
    named_entities = {}
    named_entities['sec_time'] = {'$gt': start_sec, '$lt': end_sec}
    answer_field = ['date', 'time', 'saw', 'L', 'L_uch', 'D', 'sec_time', 'mode', 'auto', 'plc_saw']
    answer = db.find_manual(theme=THEME,
                            named_entities=named_entities,
                            answer_field=answer_field)

    sort = []
    for i in range(len(answer)):
        sort.append(sorted(answer[i].items(), key=lambda x: x[0]))

    if rev:
        sort.reverse()

    d, t, saw, L, L_uch, diam, mode, auto, plc_saw = [], [], [], [], [], [], [], [], []
    for i in range(limit if limit != -1 else len(sort)):
        for j in range(len(sort[i])):
            if sort[i][j][0] == 'D':
                diam.append(sort[i][j][1])
            elif sort[i][j][0] == 'L':
                L.append(sort[i][j][1])
            elif sort[i][j][0] == 'L_uch':
                L_uch.append(sort[i][j][1])
            elif sort[i][j][0] == 'date':
                d.append(sort[i][j][1])
            elif sort[i][j][0] == 'time':
                t.append(sort[i][j][1])
            elif sort[i][j][0] == 'saw':
                saw.append(sort[i][j][1])
            elif sort[i][j][0] == 'mode':
                mode.append(sort[i][j][1])
            elif sort[i][j][0] == 'auto':
                auto.append(sort[i][j][1])
            elif sort[i][j][0] == 'plc_saw':
                plc_saw.append(sort[i][j][1])

    return d, t, saw, L, L_uch, diam, mode, auto, plc_saw

def mongo_report_old(db, THEME, limit, start_sec, end_sec, rev = True):
    out = dict()
    named_entities = {}
    named_entities['sec_time'] = {'$gt': start_sec, '$lt': end_sec}
    answer_field = ['date', 'time', 'saw', 'L', 'L_uch', 'D', 'sec_time', 'mode']
    answer = db.find_manual(theme=THEME,
                            named_entities=named_entities,
                            answer_field=answer_field)

    sort = []
    for i in range(len(answer)):
        sort.append(sorted(answer[i].items(), key=lambda x: x[0]))

    if rev:
        sort.reverse()

    d, t, saw, L, L_uch, diam, mode = [], [], [], [], [], [], []
    for i in range(limit if limit != -1 else len(sort)):
        d.append(sort[i][3][1])
        t.append(sort[i][7][1])
        saw.append(sort[i][5][1])
        L.append(sort[i][1][1])
        L_uch.append(sort[i][2][1])
        diam.append(sort[i][0][1])
        mode.append(sort[i][4][1])

    return d, t, saw, L, L_uch, diam, mode


def generate_table(dataframe, max_rows=25):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def generate_links_list(links, max_rows=15):
    #return html.A(line for line in links) # for i in range(min(len(links), max_rows))
    return html.Table(
        # Header
        [html.Tr([html.Th('')])] +
        #[html.Tr([html.Th('Залом')])] +
        # Body
        [html.Tr([
            #html.Td('{}'.format(links[i]))
            html.Td(html.A('Риск залома {}'.format(links[i].split('/')[2].replace('-',':').replace('_',' ')[:-4]), 
                            href = '{}'.format(links[i])))
        ]) for i in range(min(len(links), max_rows))]
    )


def mongo_get_load_per_shift(shift=0):
    current_date = time.strftime("%d.%m.%Y", time.localtime())
    if shift == 0:
        start_time = '09:00:00'
        end_time = '21:00:00'
    elif shift == 1:
        start_time = '21:00:00'
        end_time = '09:00:00'

    named_entities = {}
    list = []
    miss = []

    # named_entities = {'date': current_date}
    start = time.mktime(time.strptime('{} {}'.format(start_time, current_date), '%H:%M:%S %d.%m.%Y'))
    end = time.mktime(time.strptime('{} {}'.format(end_time, current_date), '%H:%M:%S %d.%m.%Y'))
    named_entities['sec_time'] = {'$gt': start - 1, '$lt': end + 1}
    answer_field = ['list_num', 'miss_num']

    # print(named_entities, answer_field)
    answer = db.find_manual(theme=THEME,
                            named_entities=named_entities,
                            answer_field=answer_field)

    for el in answer:
        miss.append(el['miss_num'])
        list.append(el['list_num'])

    if list:
        load = (round(sum(list) / (sum(list) + sum(miss)) * 100))
    else:
        load = 0

    return load, sum(list), (sum(list) + sum(miss))


def mongo_get_load_per_hour():
    current_time = time.strftime("%H:%M:%S %d.%m.%Y", time.localtime())

    named_entities = {}
    list = []
    miss = []

    start = time.mktime(time.strptime('{}'.format(current_time), '%H:%M:%S %d.%m.%Y')) - 60 * 60
    end = time.mktime(time.strptime('{}'.format(current_time), '%H:%M:%S %d.%m.%Y'))

    named_entities['sec_time'] = {'$gt': start - 1, '$lt': end + 1}
    answer_field = ['list_num', 'miss_num']

    answer = db.find_manual(theme=THEME,
                            named_entities=named_entities,
                            answer_field=answer_field)

    for el in answer:
        miss.append(el['miss_num'])
        list.append(el['list_num'])

    if list:
        hload = (round(sum(list) / (sum(list) + sum(miss)) * 100))
    else:
        hload = 0
    return hload, sum(list), (sum(list) + sum(miss))


colors = {
    'background': 'rgb(250, 250, 250)',
    'text': 'black'
}


def get_current_shift():
    current_time_sec = int(time.time())
    if int(time.strftime("%H", time.localtime(current_time_sec))) >= 9:
        current_date = time.strftime("%d.%m.%Y", time.localtime(current_time_sec))
    else:
        current_date = time.strftime("%d.%m.%Y", time.localtime(current_time_sec - 12 * 60 * 60))

    shift_duration = 12
    start_time = int(time.mktime(time.strptime('09:00:00 {}'.format(current_date), '%H:%M:%S %d.%m.%Y')))
    next_day_shift_start_time = start_time + 24 * 60 * 60 
    #start_time_str = time.strftime("%H:%M %d.%m.%Y", time.localtime(start_time))
    end_time = start_time + shift_duration * 60 * 60
    if current_time_sec > end_time and current_time_sec < next_day_shift_start_time:
        shift = 'Ночь'
    else:
        shift = 'День'

    return shift, current_date

# warnings
def mongo_make_warnings_table():  # date_str):
    start_time = '09:00:00'
    end_time = '21:00:00'

    date_str = time.strftime("%d.%m.%Y", time.localtime())
    out = dict()
    for warn in WARNINGS:
        named_entities = {'date': date_str}
        named_entities['warning_message'] = {'$all': [warn]}
        start = time.mktime(time.strptime('{} {}'.format(start_time, date_str), '%H:%M:%S %d.%m.%Y'))
        end = time.mktime(time.strptime('{} {}'.format(end_time, date_str), '%H:%M:%S %d.%m.%Y'))
        named_entities['sec_time'] = {'$gt': start - 1, '$lt': end}
        # print(named_entities)

        answer_field = ['time']
        answer = db.find_manual(theme=THEME,
                                named_entities=named_entities,
                                answer_field=answer_field)

        out[warn] = answer

    names, vals = [], []
    for key, item in out.items():
        names.append(key)
        vals.append(item)
    vals[0].reverse()
    vals[1].reverse()

    LIST_LEN = 12
    ls = [['' for i in range(LIST_LEN)], ['' for i in range(LIST_LEN)]]
    for v in reversed(vals[0][:LIST_LEN]):
        ls[0].insert(0, '{}'.format(v['time']))
        ls[0].pop(len(ls[0])-1)
    for v in reversed(vals[1][:LIST_LEN]):
        ls[1].insert(0, '{}'.format(v['time']))
        ls[1].pop(len(ls[1])-1)

    df = pd.DataFrame({
        "Риск залома": ls[0][:LIST_LEN],
        "Пропуск": ls[1][:LIST_LEN],
    })
    return df


# for txt db


def get_load_per_shift():

    shift, current_date = get_current_shift()
    
    if shift == 'День':
        daytime = 1
    elif shift == 'Ночь':
        daytime = 2

    list = []
    miss = []

    database_path = 'data/database'
    file_name = '{}_Смена_{}.txt'.format(current_date.replace('.','-'), daytime)

    with open("{}/{}".format(database_path, file_name), "r") as file:
        for line in file:
            sec_time, load, load_perc, list_num, miss_num, warn, _ = line.split(';')
            miss.append(int(miss_num))
            list.append(int(list_num))

    if list:
        load = (round(sum(list) / (sum(list) + sum(miss)) * 100))
    else:
        load = 0

    return load, sum(list), (sum(list) + sum(miss))


def get_load_per_hour():

    shift, current_date = get_current_shift()
    current_time_sec = int(time.time())

    current_hour = time.strftime("%H", time.localtime(current_time_sec))
    current_hour_sec = time.mktime(time.strptime('{}:00:00 {}'.format(current_hour, current_date), '%H:%M:%S %d.%m.%Y'))

    if shift == 'День':
        daytime = 1
    elif shift == 'Ночь':
        daytime = 2

    list = []
    miss = []

    database_path = 'data/database'
    file_name = '{}_Смена_{}.txt'.format(current_date.replace('.','-'), daytime)

    if True:
        with open("{}/{}".format(database_path, file_name), "r") as file:
            for line in file:
                sec_time, load, load_perc, list_num, miss_num, warn, _ = line.split(';')
                if int(sec_time) > current_hour_sec and int(sec_time) < current_hour_sec + 60 * 60:
                    miss.append(int(miss_num))
                    list.append(int(list_num))
    else:
        with open("{}/{}".format(database_path, file_name), "r") as file:
            for line in file:
                sec_time, load, load_perc, list_num, miss_num, warn, _ = line.split(';')
                if int(sec_time) > current_time_sec - 60 * 60:
                    miss.append(int(miss_num))
                    list.append(int(list_num))

    if list:
        load = (round(sum(list) / (sum(list) + sum(miss)) * 100))
    else:
        load = 0

    return load, sum(list), (sum(list) + sum(miss))



def get_rz_link_list(date, daytime):

    links = []
    str_times = []

    database_path = 'data/database'
    file_name = '{}_Смена_{}.txt'.format(date.replace('.','-'), daytime)

    database_path = 'data/database'
    file_name = '{}_Смена_{}.txt'.format(date.replace('.','-'), daytime)

    with open("{}/{}".format(database_path, file_name), "r") as file:
        for line in file:
            sec_time, load, load_perc, list_num, miss_num, warning, path = line.split(';')
            if 'edge' in warning:
                links.append(path[1:-1])
    
    links.reverse()

    return links


def get_rz_time(date, daytime):

    times = []
    str_times = []

    database_path = 'data/database'
    file_name = '{}_Смена_{}.txt'.format(date.replace('.','-'), daytime)

    database_path = 'data/database'
    file_name = '{}_Смена_{}.txt'.format(date.replace('.','-'), daytime)

    with open("{}/{}".format(database_path, file_name), "r") as file:
        for line in file:
            sec_time, load, load_perc, list_num, miss_num, warning, _ = line.split(';')
            if 'edge' in warning:
                times.append(int(sec_time))

    for t in times:
        str_t = time.strftime("%H:%M:%S", time.localtime(t))
        str_times.append(str_t)

    return times, str_times



def get_average_load_per_shift(date, daytime):

    list = []
    miss = []

    database_path = 'data/database'
    file_name = '{}_Смена_{}.txt'.format(date.replace('.','-'), daytime)

    with open("{}/{}".format(database_path, file_name), "r") as file:
        for line in file:
            sec_time, load, load_perc, list_num, miss_num, warn, _ = line.split(';')
            miss.append(int(miss_num))
            list.append(int(list_num))

    if list:
        load = (round(sum(list) / (sum(list) + sum(miss)) * 100))
    else:
        load = 0

    return load, sum(list), (sum(list) + sum(miss))


def get_average_load_per_hour(date, daytime, hour_ind):

    list = []
    miss = []

    database_path = 'data/database'
    file_name = '{}_Смена_{}.txt'.format(date.replace('.','-'), daytime)

    start = time.mktime(time.strptime('{}:00:00 {}'.format(9 + hour_ind, date), '%H:%M:%S %d.%m.%Y'))
    if daytime == 2:
        start += 12 * 60 * 60
    end = start + 60 * 60

    with open("{}/{}".format(database_path, file_name), "r") as file:
        for line in file:
            sec_time, load, load_perc, list_num, miss_num, warn, _ = line.split(';')
            if int(sec_time) > start and int(sec_time) < end:
                miss.append(int(miss_num))
                list.append(int(list_num))

    if list:
        load = (round(sum(list) / (sum(list) + sum(miss)) * 100))
    else:
        load = 0

    return load, sum(list), (sum(list) + sum(miss))
