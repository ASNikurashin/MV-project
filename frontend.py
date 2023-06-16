import time
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import date, datetime
from pprint import pprint
import json
from math import pi
from flask import request

import openpyxl
from openpyxl.styles.borders import Border, Side, BORDER_THIN
import os

from config import settings as conf
from modules.frontend_functions import *


#'''
if conf['DB_USE']:
    if not conf['DB_TXT']:
        from modules.mongo_functions import *
        db = DB(ip=conf['DB_IP'], port=conf['DB_PORT'], 
                                database=conf['DB_DATABASE']) # standart mongodb port 27017
        THEME = conf['DB_THEME']
        #db.knowledge_base[THEME].create_index([('sec_time', DESCENDING)])
#'''


with open(r'data/settings.json', 'r', encoding='utf-8') as f:
    settings = json.load(f)


with open(r'data/current_mode.json', 'r', encoding='utf-8') as f:
    curr = json.load(f)


store_dict = dict()
store_dict['name'] = curr['name']
store_dict['koef'] = curr['koef']

names = []
for key in settings:
    names.append(key)

store_dict['options'] = names
 
print(names)
mode_template = {"name": "Режим", "saw_1": {"drop_len": [3.2, 4.8], "d_min":200, "d_max":500}, 
                                  "saw_2": {"drop_len": [2.6, 3.9, 5.2], "d_min":0, "d_max":500}, 
                                  "saw_3": {"drop_len": [3.2, 4.8], "d_min":0, "d_max":200}}

d = time.strftime("%d.%m.%Y", time.localtime(time.time()))
d = d.split('.')
d = [int(i) for i in d]

t = time.strftime("%H:%M:%S", time.localtime(time.time()))
t = t.split(':')
t = [int(i) for i in t]

# external_stylesheets = ['templates/form.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__)

app._favicon = ("run.ico")
app.title = 'Машинное зрение на линии раскряжевки'

app.layout = html.Div([

        html.Div([
            html.Div([
                        dcc.Tabs(id="tabs-video", value="Stream",
                                 #parent_className='custom-tabs',
                                 className='custom-tabs-container',
                                 style={'padding-top': '0%', 'padding-left': '0%', 'padding-right': '0%'},
                                 children=[

                                    dcc.Tab(label='Главный вид', value='Stream', className='custom-tab',
                                            selected_className='custom-tab--selected',
                                            children=[

                                                html.Div([
                                                    html.Div([

                                                            html.H4('Активный режим: _', id='active_mode',
                                                                     style={'padding-top': '3%', 
                                                                    'padding-left': '7.9%'}),

                                                            html.Div([    

                                                                dcc.Store(id='info_void', data=[]),

                                                                html.Div([
                                                                       html.H4("Пила 1"),
                                                                       html.Div('Количество: _', id='q_1'),
                                                                       html.Div('Ср. диаметр: _', id='ad_1'),
                                                                       html.Div('Ср. длина: _', id='al_1'),
                                                                     ], style={'padding-top': '0%', 'padding-left': '0%', 'flex': 1}),
                                                                html.Div([
                                                                       html.H4("Пила 2"),
                                                                       html.Div('Количество: _', id='q_2'),
                                                                       html.Div('Ср. диаметр: _', id='ad_2'),
                                                                       html.Div('Ср. длина: _', id='al_2'),
                                                                     ], style={'padding-top': '0%', 'padding-bottom': '1%', 'padding-left': '0%', 'flex': 1}),
                                                                html.Div([
                                                                       html.H4("Пила 3"),
                                                                       html.Div('Количество: _', id='q_3'),
                                                                       html.Div('Ср. диаметр: _', id='ad_3'),
                                                                       html.Div('Ср. длина: _', id='al_3'),
                                                                     ], style={'padding-top': '0%', 'padding-bottom': '1%', 'padding-left': '0%', 'flex': 1}),
                                                                 dcc.Interval(
                                                                       id='load_interval',
                                                                       interval=2*1000,
                                                                       n_intervals=0
                                                                   )
                        
                                                                ], style={'padding-top': '1%', 'display': 'flex', 'flex-direction': 'row', 'padding-left': '7.9%', 'padding-right': '7.9%'}),

                                                            # -------------------------------------------------------
                                                            html.Div([
                                                                html.Center(html.Iframe(src='http://{}:58800/'.format(conf['STREAMER_IP_FRONT']),
                                                                            style={'width': '84%', 'height': '685px'}))
                                                                ], style={'padding-top': '2%'})
                                                        ], style={'flex': 3}),

                                                    html.Div([
                                                            
                                                            html.Div([

                                                                html.Img(src='static/sveza-logo.png',
                                                                            style={'width': '85%', 'padding-top': '10%'},
                                                                            alt="Logo"),
                                                                
                                                                html.Br(),

                                                                html.H4("Выгрузить отчёт:", style={'padding-top': '7%'}),


                                                                html.Div([                                                                
                                                                    html.Div([
                                                                        dcc.Input(id='time1h', type='number', min=0, max=23, step=1, placeholder='Часы', value=t[0], style={'flex': 1, 'width': '60px'}),
                                                                        html.Div(html.Center(":"), style={'flex': 1}),
                                                                        dcc.Input(id='time1m', type='number', min=0, max=59, step=1, placeholder='Минута', value=t[1], style={'flex': 1, 'width': '60px'}),
                                                                        ], style = {'display': 'flex', 'flex-direction': 'row', 'flex': 2}),
                                                                    html.Div(html.Center(" "), style={'flex': 1}),
                                                                    html.Div([
                                                                        dcc.Input(id='time2h', type='number', min=0, max=23, step=1, placeholder='Час', value=t[0], style={'flex': 1, 'width': '60px'}),
                                                                        html.Div(html.Center(":"), style={'flex': 1}),
                                                                        dcc.Input(id='time2m', type='number', min=0, max=59, step=1, placeholder='Минуты', value=t[1], style={'flex': 1, 'width': '60px'}),
                                                                        ], style = {'display': 'flex', 'flex-direction': 'row','flex': 2}),
                                                                    ], style = {'display': 'flex', 'flex-direction': 'row', 'width':'60%'}),

                                                                dcc.DatePickerRange(
                                                                        id='date_pick_range',
                                                                        min_date_allowed=date(2000, 1, 1),
                                                                        max_date_allowed=date(2500, 1, 1),
                                                                        initial_visible_month=date(d[2], d[1], d[0]),
                                                                        start_date_placeholder_text='DD.MM.YY',
                                                                        end_date_placeholder_text='DD.MM.YY',
                                                                        start_date=date(d[2], d[1], d[0]),
                                                                        end_date=date(d[2], d[1], d[0]),
                                                                        display_format='DD.MM.YY',
                                                                    ),

                                                                dcc.ConfirmDialogProvider(
                                                                                children=html.Button(id='get_report', n_clicks=0, 
                                                                                                     children='Отчёт',
                                                                                                     style={"width": "60%"}),
                                                                                id='report_provider',
                                                                                message='Сохранить отчёт?'
                                                                    ),

                                                                dcc.Download(id="download_report"),

                                                                html.Br(),

                                                                #html.H4("Последние записи:", style={'padding-top': '7%'}),
                                                                html.Div(id='load_table',
                                                                         style={'padding-top': '0%', 'padding-right': '10%'}),

                                                                ], style={'flex': 1}),

                                                        ], style={'display': 'flex', 'flex-direction': 'column', 'flex': 1}),

                                                    ], style = {'display': 'flex', 'flex-direction': 'row'})

                                              ], style={'padding-top': '0%', 'padding-left': '0%'}),

                                dcc.Tab(label='Настройки', value='Settings', className='custom-tab',
                                        selected_className='custom-tab--selected',
                                        children=[
                                                html.Div([
                                                    html.Br(),
                                                    #html.Center([
                                                        html.Img(src="static/sveza-logo.png",
                                                                 style={'width': '20%'},
                                                                 alt="Logo"),
                                                    #]),
                                                    
                                                    html.Br(),
                                                    
                                                    html.H4('Режим работы:'),
                                                    dcc.Store(id='curr_user', data=''),

                                                    dcc.Interval(
                                                                   id='mode_interval',
                                                                   interval=2*1000,
                                                                   n_intervals=0
                                                               ),

                                                    html.Div([
                                                                dcc.Dropdown(
                                                                    options=store_dict['options'],
                                                                    value=store_dict['name'],
                                                                    placeholder="Выберите режим работы",
                                                                    id='set'
                                                                    ),

                                                            ], style={"width": "28%", "height": "38px", "padding-left": "3%"}),

                                                    html.Div([
                                                                dcc.Input(id='password', value="", type='password', placeholder='Для изменения параметров введите пароль',
                                                                          maxLength = 10, style={"width": "28.85%", "height": "38px"}),
                                                            ], style={"padding-left": "3%"}),

                                                    html.Br(),
                                                    html.Div([
                                                                'Коэффициент калибровки оценки диаметра:   ',
                                                                dcc.Input(id='koef', value=store_dict['koef'], type='number', min=0, max=10, # debounce=True, # value=0.687
                                                                          style={"width": "92px", "height": "38px"}),
                                                            ], style={"padding-left": "3%"}),

                                                    html.Br(),

                                                    html.Div([
                                                        html.Div([
                                                            html.H4('Параметры кряжа (Пила 1):', style={"padding-left": "3%"}),

                                                            html.Div([
                                                                        'Учетные длины:    ',
                                                                        dcc.Dropdown([2.6, 3.2, 3.9, 4.8, 5.2], 
                                                                                     id='drop_len_1', 
                                                                                     multi=True,
                                                                                     style={"width": "100%", 'flex': 1}),
                                                                    ], style={"padding-left": "4%", "padding-right": "5%"}),

                                                            html.Br(),
                                                            html.Div([
                                                                        'Интервал диаметров для сортировки:   ',
                                                                        html.Br(),
                                                                        'От ',
                                                                        dcc.Input(id='d_min_1', value=140, type='number', min=0, max=4000,
                                                                                  style={"width": "92px", "height": "38px"}),                         
                                                                        '   мм.  до  ',                            
                                                                        dcc.Input(id='d_max_1', value=200, type='number', min=0, max=4000,
                                                                                  style={"width": "92px", "height": "38px"}),                         
                                                                        '   мм.  ',        
                                                                    ], style={"padding-left": "4%", "padding-right": "5%"}),                    
                                                            ], style = {'flex': 1}),

                                                        html.Div([
                                                            html.H4('Параметры кряжа (Пила 2):', style={"padding-left": "3%"}),

                                                            html.Div([
                                                                        'Учетные длины:    ',
                                                                        dcc.Dropdown([2.6, 3.2, 3.9, 4.8, 5.2], 
                                                                                     id='drop_len_2', 
                                                                                     multi=True,
                                                                                     style={"width": "100%", 'flex': 1}),
                                                                    ], style={"padding-left": "4%", "padding-right": "5%"}),

                                                            html.Br(),
                                                            html.Div([
                                                                        'Интервал диаметров для сортировки:   ',
                                                                        html.Br(),
                                                                        'От ',
                                                                        dcc.Input(id='d_min_2', value=140, type='number', min=0, max=4000,
                                                                                  style={"width": "92px", "height": "38px"}),
                                                                        '   мм.  до  ',                            
                                                                        dcc.Input(id='d_max_2', value=200, type='number', min=0, max=4000,
                                                                                  style={"width": "92px", "height": "38px"}),                         
                                                                        '   мм.  ',        
                                                                    ], style={"padding-left": "4%", "padding-right": "5%"}),                    
                                                            ], style = {'flex': 1}),

                                                        html.Div([
                                                            html.H4('Параметры кряжа (Пила 3):', style={"padding-left": "3%"}),

                                                            html.Div([
                                                                        'Учетные длины:    ',
                                                                        dcc.Dropdown([2.6, 3.2, 3.9, 4.8, 5.2], 
                                                                                     id='drop_len_3', 
                                                                                     multi=True,
                                                                                     style={"width": "100%", 'flex': 1}),
                                                                    ], style={"padding-left": "4%", "padding-right": "5%"}),

                                                            html.Br(),

                                                            html.Div([
                                                                        'Интервал диаметров для сортировки:   ',
                                                                        html.Br(),
                                                                        'От ',
                                                                        dcc.Input(id='d_min_3', value=140, type='number', min=0, max=4000,
                                                                                  style={"width": "92px", "height": "38px"}),                         
                                                                        '   мм.  до  ',                            
                                                                        dcc.Input(id='d_max_3', value=200, type='number', min=0, max=4000,
                                                                                  style={"width": "92px", "height": "38px"}),                         
                                                                        '   мм.  ',        
                                                                    ], style={"padding-left": "4%", "padding-right": "5%"}),                    
                                                            ], style = {'flex': 1}),
                                                        ], style = {'display': 'flex', 'flex-direction': 'row'}),

                                                    html.Br(),
                                                    html.H4('Сохранение нового режима:'),
                                                    
                                                    html.Div([
                                                                'Название режима:   ',
                                                                dcc.Input(id='mode_name', value="", type='text', maxLength = 18,
                                                                          style={"width": "16.5%", "height": "38px"}),
                                                            ], style={"padding-left": "3.5%"}), 


                                                    html.Div([                         
                                                                html.Button(id='save_mode', 
                                                                            n_clicks=0, 
                                                                            children='Сохранить режим',
                                                                            style={"width": "28.9%"}),
                                                            ], style={"padding-left": "3%"}),
                                                    html.Div([
                                                                dcc.ConfirmDialogProvider(
                                                                            children=html.Button(id='delete_mode', 
                                                                                                 n_clicks=0, 
                                                                                                 children='Удалить выбранный режим',
                                                                                                 style={"width": "28.9%"}),
                                                                            id='del_provider',
                                                                            message='Вы уверены что хотите удалить режим?'), 
                                                            ], style={"padding-left": "3%"}),

                                                    html.Div([                         
                                                                html.Button(id='clear_report_folder', 
                                                                            n_clicks=0, 
                                                                            children='Очистить папку с отчётами',
                                                                            style={"width": "28.9%"}),
                                                            ], style={"padding-left": "3%"}),

                                                    html.Div([                         
                                                                html.Button(id='reboot', 
                                                                            n_clicks=0, 
                                                                            children='Перезапустить систему',
                                                                            style={"width": "28.9%"}),
                                                            ], style={"padding-left": "3%"}),

                                                ], style={'padding-left': '2%'})
                                              ], 
                                              style={'padding-top': '0%', 'padding-left': '0%'}),

                                              ]
                                        )
            ], style={'padding-top': '0%', 'padding-left': '0%', 'flex': 1}),

        ], style={'display': 'flex', 'flex-direction': 'row', 'flex': 7})
        
], style={'display': 'flex', 'flex-direction': 'column'})


@app.callback(Output('load_table', 'children'),
              Output('q_1', 'children'),
              Output('ad_1', 'children'),
              Output('al_1', 'children'),
              Output('q_2', 'children'),
              Output('ad_2', 'children'),
              Output('al_2', 'children'),
              Output('q_3', 'children'),
              Output('ad_3', 'children'),
              Output('al_3', 'children'),
              Input('load_interval', 'n_intervals'))

def update_load(n):

    # За сутки
    '''
    date_str = time.strftime("%d.%m.%Y", time.localtime())
    start_sec = time.mktime(time.strptime('00:00:00 {}'.format(date_str), '%H:%M:%S %d.%m.%Y'))
    end_sec = time.mktime(time.strptime('23:59:59 {}'.format(date_str), '%H:%M:%S %d.%m.%Y'))

    saw_1 = mongo_count_saw(db, THEME, 1, start_sec, end_sec)
    saw_2 = mongo_count_saw(db, THEME, 2, start_sec, end_sec)
    saw_3 = mongo_count_saw(db, THEME, 3, start_sec, end_sec)
    #print(saw_1, saw_2, saw_3)

    df = mongo_last_records_df(db, THEME, 10, start_sec, end_sec)
    table = generate_table(df, 15)
    '''

    # За смену
    #'''
    shift_duration = 12
    shift, current_date = get_current_shift()
    
    if shift == 'День':
        start_sec = time.mktime(time.strptime('08:00:00 {}'.format(current_date), '%H:%M:%S %d.%m.%Y'))
    elif shift == 'Ночь':
        start_sec = time.mktime(time.strptime('20:00:00 {}'.format(current_date), '%H:%M:%S %d.%m.%Y'))
    end_sec = start_sec + shift_duration * 60 * 60

    saw_1 = mongo_count_saw(db, THEME, 1, start_sec, end_sec)
    saw_2 = mongo_count_saw(db, THEME, 2, start_sec, end_sec)
    saw_3 = mongo_count_saw(db, THEME, 3, start_sec, end_sec)
    
    df = mongo_last_records_df(db, THEME, 10, start_sec, end_sec,rev = False)
    table = generate_table(df, 15)
    #'''
    return table, 'Количество: {}'.format(saw_1['count']), 'Ср. диаметр: {}'.format(saw_1['D']), 'Ср. длина: {}'.format(saw_1['L']), 'Количество: {}'.format(saw_2['count']), 'Ср. диаметр: {}'.format(saw_2['D']), 'Ср. длина: {}'.format(saw_2['L']), 'Количество: {}'.format(saw_3['count']), 'Ср. диаметр: {}'.format(saw_3['D']), 'Ср. длина: {}'.format(saw_3['L'])


# Окно настроек, сохранение нового режима, удаление режимов
@app.callback(Output('set', 'value'),
              Output('active_mode', 'children'),
              Output('set', 'options'),
              Output('drop_len_1', 'value'),
              Output('drop_len_2', 'value'),
              Output('drop_len_3', 'value'),
              Output('d_min_1', 'value'),
              Output('d_max_1', 'value'),
              Output('d_min_2', 'value'),
              Output('d_max_2', 'value'),
              Output('d_min_3', 'value'),
              Output('d_max_3', 'value'),
              Output('koef', 'value'),
              #Output('curr_user', 'data'), active_mode
              #Output('password', 'value'),

              Input('set', 'value'), 
              Input('save_mode', 'n_clicks'),
              Input('del_provider', 'submit_n_clicks'),
              Input('koef', 'value'),
              Input('mode_interval', 'n_intervals'),

              State('mode_name', 'value'),
              State('set', 'options'),
              State('set', 'value'),
              State('drop_len_1', 'value'),
              State('drop_len_2', 'value'),
              State('drop_len_3', 'value'),
              State('d_min_1', 'value'),
              State('d_max_1', 'value'),
              State('d_min_2', 'value'),
              State('d_max_2', 'value'),
              State('d_min_3', 'value'),
              State('d_max_3', 'value'),
              State('curr_user', 'data'),
              State('password', 'value'))

def save_settings(set_m, save_clicks, 
                  del_clicks, 
                  koef, mode_interval, new_name, options, value,
                  drop_len_1, drop_len_2, drop_len_3, 
                  d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, curr_user,
                  pas):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    print('Save|Del|Set: ', button_id)
    print('Текущий режим: ', set_m)
    print('Введенный пароль: ', pas)
    print('')

    #if (button_id == 'mode_interval') and (pas == conf['PASSWORD']) and (curr_user == ''):
    #    ip_address = request.remote_addr
    #    print('Редактирование параметров:', ip_address)
    #    print('------------')

    #    return set_m, options, drop_len_1, drop_len_2, drop_len_3, d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, koef, ip_address#, pas

    if (button_id == 'mode_interval') and (pas != conf['PASSWORD']):
        with open(r"data/current_mode.json", "r", encoding='utf-8') as f:
            current = json.load(f)
        with open(r"data/settings.json", "r", encoding='utf-8') as f:
            mods = json.load(f)

        options = []
        for key in mods:
            options.append(key)

        if current is not None:
            drop_len_1 = current['saw_1']['drop_len']
            drop_len_2 = current['saw_2']['drop_len']
            drop_len_3 = current['saw_3']['drop_len']
            d_min_1 = current['saw_1']['d_min']
            d_max_1 = current['saw_1']['d_max']
            d_min_2 = current['saw_2']['d_min']
            d_max_2 = current['saw_2']['d_max']
            d_min_3 = current['saw_3']['d_min']
            d_max_3 = current['saw_3']['d_max']
            koef = current['koef']

            print(current)
            print('------------')

        return current['name'], 'Активный режим: {}'.format(current['name']), options, drop_len_1, drop_len_2, drop_len_3, d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, koef#, curr_user #, pas

    elif (button_id == 'set') and (pas == conf['PASSWORD']):
        if set_m is not None:
            drop_len_1 = settings[set_m]['saw_1']['drop_len']
            drop_len_2 = settings[set_m]['saw_2']['drop_len']
            drop_len_3 = settings[set_m]['saw_3']['drop_len']
            d_min_1 = settings[set_m]['saw_1']['d_min']
            d_max_1 = settings[set_m]['saw_1']['d_max']
            d_min_2 = settings[set_m]['saw_2']['d_min']
            d_max_2 = settings[set_m]['saw_2']['d_max']
            d_min_3 = settings[set_m]['saw_3']['d_min']
            d_max_3 = settings[set_m]['saw_3']['d_max']

            new_current = settings.copy()
            new_current[set_m]['koef'] = koef # curr_mode_data['koef']

        return set_m, 'Активный режим: {}'.format(set_m), options, drop_len_1, drop_len_2, drop_len_3, d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, koef#, curr_user#, pas

    
    elif ((button_id == 'set') or (button_id == 'koef') or (button_id == 'No clicks yet')) and (pas != conf['PASSWORD']):
        if set_m is not None:
            drop_len_1 = settings[set_m]['saw_1']['drop_len']
            drop_len_2 = settings[set_m]['saw_2']['drop_len']
            drop_len_3 = settings[set_m]['saw_3']['drop_len']
            d_min_1 = settings[set_m]['saw_1']['d_min']
            d_max_1 = settings[set_m]['saw_1']['d_max']
            d_min_2 = settings[set_m]['saw_2']['d_min']
            d_max_2 = settings[set_m]['saw_2']['d_max']
            d_min_3 = settings[set_m]['saw_3']['d_min']
            d_max_3 = settings[set_m]['saw_3']['d_max']

            new_current = settings.copy()
            new_current[set_m]['koef'] = koef # curr_mode_data['koef']

            print(new_current[set_m])
            with open(r"data/current_mode.json", "w", encoding='utf-8') as f:
                json.dump(new_current[set_m], f)
            print('------------')

        return set_m, 'Активный режим: {}'.format(set_m), options, drop_len_1, drop_len_2, drop_len_3, d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, koef#, curr_user#, pas

    elif button_id == 'koef':
        with open(r"data/current_mode.json", "r", encoding='utf-8') as f:
            current = json.load(f)

        current['koef'] = koef

        print('Текущий коэффициент: ', current['koef'])

        with open(r"data/current_mode.json", "w", encoding='utf-8') as f:
            json.dump(current, f)

        return set_m, 'Активный режим: {}'.format(set_m), options, drop_len_1, drop_len_2, drop_len_3, d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, koef#, curr_user#, pas

    elif button_id == 'save_mode':
        if new_name != '' and new_name.replace(' ', '') != '' and not(new_name in options):
            options.append(new_name)
            
            new_mode = mode_template.copy()
            #new_mode = settings[value].copy()
            print(new_mode)
            new_mode['name'] = new_name            
            new_mode['saw_1']['drop_len'] = drop_len_1
            new_mode['saw_2']['drop_len'] = drop_len_2
            new_mode['saw_3']['drop_len'] = drop_len_3
            new_mode['saw_1']['d_min'] = d_min_1
            new_mode['saw_1']['d_max'] = d_max_1
            new_mode['saw_2']['d_min'] = d_min_2
            new_mode['saw_2']['d_max'] = d_max_2
            new_mode['saw_3']['d_min'] = d_min_3
            new_mode['saw_3']['d_max'] = d_max_3

            print('Новый режим: ', new_mode)

            settings[new_name] = new_mode

            options = []
            for key in settings:
                options.append(key)
            print(options)

            with open(r"data/settings.json", "w", encoding='utf-8') as f:
                json.dump(settings, f)

            new_current = settings.copy()
            new_current[new_name]['koef'] = koef
            with open(r"data/current_mode.json", "w", encoding='utf-8') as f:
                json.dump(new_current[new_name], f)

            return new_name, 'Активный режим: {}'.format(new_name), options, drop_len_1, drop_len_2, drop_len_3, d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, koef#, curr_user#, ''

        elif (new_name in options) and not(new_name in ['Режим 1', 'Режим 2', 'Режим 3']):
            settings[new_name]['saw_1']['drop_len'] = drop_len_1
            settings[new_name]['saw_2']['drop_len'] = drop_len_2
            settings[new_name]['saw_3']['drop_len'] = drop_len_3
            settings[new_name]['saw_1']['d_min'] = d_min_1
            settings[new_name]['saw_1']['d_max'] = d_max_1
            settings[new_name]['saw_2']['d_min'] = d_min_2
            settings[new_name]['saw_2']['d_max'] = d_max_2
            settings[new_name]['saw_3']['d_min'] = d_min_3
            settings[new_name]['saw_3']['d_max'] = d_max_3
            print('Изменённый режим: ', settings[new_name])
            print(options)

            with open(r"data/settings.json", "w", encoding='utf-8') as f:
                json.dump(settings, f)

            new_current = settings.copy()
            new_current[new_name]['koef'] = koef

            with open(r"data/current_mode.json", "w", encoding='utf-8') as f:
                json.dump(new_current[new_name], f)

            return new_name, 'Активный режим: {}'.format(new_name), options, drop_len_1, drop_len_2, drop_len_3, d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, koef#, curr_user#, '' 
        
    #'''
    elif button_id == 'del_provider':

        if len(options) > 1 and not(value in ['Режим 1', 'Режим 2', 'Режим 3']):
            options.remove(value)
            settings.pop(value)

            options = []
            for key in settings:
                options.append(key)

            with open(r"data/settings.json", "w", encoding='utf-8') as f:
                json.dump(settings, f)

            new_current = settings.copy()
            new_current[options[0]]['koef'] = koef
            with open(r"data/current_mode.json", "w", encoding='utf-8') as f:
                json.dump(new_current[options[0]], f)

            return options[0], 'Активный режим: {}'.format(options[0]), options, drop_len_1, drop_len_2, drop_len_3, d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, koef#, curr_user#, ''
        else:
            return options[0], 'Активный режим: {}'.format(options[0]), options, drop_len_1, drop_len_2, drop_len_3, d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, koef#, curr_user#, pas
    #'''
    else:
        return set_m, 'Активный режим: {}'.format(set_m), options, drop_len_1, drop_len_2, drop_len_3, d_min_1, d_max_1, d_min_2, d_max_2, d_min_3, d_max_3, koef#, curr_user#, pas

#'''

'''
@app.callback(Output('curr_mode_data', 'data'),
              Input('set', 'value'),
              State('curr_mode_data', 'data'))
 
def change_mode(mode, curr_mode):
    if mode is not None:
        #print(mode)
        store_dict['name'] = mode
        return store_dict
    else:
        store_dict['name'] = curr_mode
        return store_dict
#'''


@app.callback(Output('download_report', 'data'), 
              #Output('info_void', 'data'),
              Input('report_provider', 'submit_n_clicks'),
              #Input('get_report', 'n_clicks'),
              State('time1h', 'value'),
              State('time1m', 'value'),
              State('time2h', 'value'),
              State('time2m', 'value'),
              State('date_pick_range', 'start_date'),
              State('date_pick_range', 'end_date'),
              prevent_initial_call=True)
 
def make_report(n_click, h1, m1, h2, m2, start, end):

    save = True
    report_name = None

    if n_click != None:
        thin_border = Border(
                                left=Side(border_style=BORDER_THIN, color='00000000'),
                                right=Side(border_style=BORDER_THIN, color='00000000'),
                                top=Side(border_style=BORDER_THIN, color='00000000'),
                                bottom=Side(border_style=BORDER_THIN, color='00000000')
                            )

        print(start, end)

        if start is not None:
            #start_date = datetime.fromisoformat(start)
            #start_date_str = start_date.strftime('%d %m %Y').replace(' ', '.')
            start_date = str(start)
            start_date_str = start_date.replace('-', '.')

        if end is not None:
            #end_date = datetime.fromisoformat(end)
            #end_date_str = end_date.strftime('%d %m %Y').replace(' ', '.')
            end_date = str(end)
            end_date_str = end_date.replace('-', '.')


        if (h1 is not None) and (m1 is not None):
            if int(h1) // 10 == 0:
                h1 = '0{}'.format(h1)
            if int(m1) // 10 == 0:
                m1 = '0{}'.format(m1)
            start_time_str = '{}:{}:00'.format(h1, m1)
        if (h2 is not None) and (m2 is not None):
            if int(h2) // 10 == 0:
                h2 = '0{}'.format(h2)
            if int(m2) // 10 == 0:
                m2 = '0{}'.format(m2)
            end_time_str = '{}:{}:00'.format(h2, m2)

        start_sec = time.mktime(time.strptime('{} {}'.format(start_time_str, start_date_str), '%H:%M:%S %Y.%m.%d'))
        end_sec = time.mktime(time.strptime('{} {}'.format(end_time_str, end_date_str), '%H:%M:%S %Y.%m.%d'))
        
        d, t, saw, L, L_uch, diam, mode, auto, plc_saw = mongo_report(db, THEME, -1, start_sec, end_sec, rev=True) # <---------------

        st_date_st = time.strftime("%d.%m.%Y", time.localtime(start_sec))
        end_date_st = time.strftime("%d.%m.%Y", time.localtime(end_sec))

        start_text = '{} {}'.format(st_date_st,
                                    start_time_str)
        end_text = '{} {}'.format(end_date_st, 
                                  end_time_str)

        report_name = "Раскряжевка отчёт {} - {}".format(start_text.replace(':','-'), end_text.replace(':','-'))

        print(report_name)

        #'''
        if save:
            try:
                wb_template = openpyxl.load_workbook(filename = 'data/report_template.xlsx')
                sheet_template = wb_template['Отчёт']
                val = sheet_template['A8'].value

                sheet_template['B2'] = '{} {}'.format(start_time_str,
                                                      st_date_st)
                sheet_template['B3'] = '{} {}'.format(end_time_str,
                                                      end_date_st)

                counter = 0
                arr_v = []
                arr_vuch = []
                q_saw1, v_saw1 = [], [] # <---------------------------
                q_saw2, v_saw2 = [], []
                q_saw3, v_saw3 = [], []
                q_auto, q_manual = 0, 0

                if len(d) != 0:
                    for i in range(len(d)):
                        if auto[i]:
                            q_auto += 1
                        else:
                            q_manual += 1

                        sheet_template['M{}'.format(i + 7)] = auto[i]   # <---------------------------
                        sheet_template['M{}'.format(i + 7)].border = thin_border


                        sheet_template['L{}'.format(i + 7)] = mode[i]
                        sheet_template['L{}'.format(i + 7)].border = thin_border

                        di = diam[i] / 1000
                        v = ((di / 2)**2) * pi * (L[i] / 1000)

                        if not (v is None):
                            arr_v.append(v)
                        
                        sheet_template['K{}'.format(i + 7)] = v
                        sheet_template['K{}'.format(i + 7)].border = thin_border

                        di_uch = int(diam[i] / 10) / 100
                        v_uch = ((di_uch / 2)**2) * pi * (L_uch[i] / 1000)
                        
                        if not (v_uch is None):
                            arr_vuch.append(v_uch)
                        
                        sheet_template['J{}'.format(i + 7)] = v_uch
                        sheet_template['J{}'.format(i + 7)].border = thin_border

                        sheet_template['I{}'.format(i + 7)] = L[i] / 1000
                        sheet_template['I{}'.format(i + 7)].border = thin_border

                        sheet_template['H{}'.format(i + 7)] = L_uch[i] / 1000
                        sheet_template['H{}'.format(i + 7)].border = thin_border

                        sheet_template['G{}'.format(i + 7)] = diam[i]
                        sheet_template['G{}'.format(i + 7)].border = thin_border

                        sheet_template['F{}'.format(i + 7)] = di_uch * 100
                        sheet_template['F{}'.format(i + 7)].border = thin_border

                        sheet_template['E{}'.format(i + 7)] = plc_saw[i]  # <---------------------------
                        sheet_template['E{}'.format(i + 7)].border = thin_border

                        sheet_template['D{}'.format(i + 7)] = saw[i]
                        sheet_template['D{}'.format(i + 7)].border = thin_border

                        sheet_template['C{}'.format(i + 7)] = '{}'.format(t[i])
                        sheet_template['C{}'.format(i + 7)].border = thin_border

                        sheet_template['B{}'.format(i + 7)] = '{}'.format(d[i])
                        sheet_template['B{}'.format(i + 7)].border = thin_border

                        counter += 1
                        sheet_template['A{}'.format(i + 7)] = i + 1
                        sheet_template['A{}'.format(i + 7)].border = thin_border
                else:
                    print(len(d))

                sheet_template['B{}'.format(counter + 8)] = 'Итого'
                #sheet_template['B{}'.format(counter + 8)].border = thin_border
                sheet_template['B{}'.format(counter + 9)] = 'Количество'
                #sheet_template['B{}'.format(counter + 9)].border = thin_border
                sheet_template['C{}'.format(counter + 9)] = len(arr_v)
                #sheet_template['C{}'.format(counter + 9)].border = thin_border
                sheet_template['B{}'.format(counter + 10)] = 'Vучет, м3'
                #sheet_template['B{}'.format(counter + 10)].border = thin_border
                sheet_template['C{}'.format(counter + 10)] = sum(arr_vuch)
                #sheet_template['C{}'.format(counter + 10)].border = thin_border
                sheet_template['B{}'.format(counter + 11)] = 'Vфакт, м3'
                #sheet_template['B{}'.format(counter + 11)].border = thin_border
                sheet_template['C{}'.format(counter + 11)] = sum(arr_v)
                #sheet_template['C{}'.format(counter + 11)].border = thin_border

                sheet_template['B{}'.format(counter + 12)] = 'Режим "Авто"'
                #sheet_template['B{}'.format(counter + 11)].border = thin_border
                sheet_template['C{}'.format(counter + 12)] = '{}%'.format(100 * q_auto/(q_auto + q_manual))
                #sheet_template['C{}'.format(counter + 11)].border = thin_border

                wb_template.save('data/reports/{}.xlsx'.format(report_name))            
            #'''    
            except:
                print('Нет данных за указанный период')
                wb = openpyxl.Workbook()
                sheet_template['B2'] = start_text
                sheet_template['B3'] = end_text
                sheet_template['A7'] = 'Нет данных за указанный период'
                wb.save('data/reports/{}.xlsx'.format(report_name))
            #'''
    
    if report_name is None:
        return None
    else:
        return dcc.send_file('./data/reports/{}.xlsx'.format(report_name))


@app.callback(Output('info_void', 'data'),
              Input('clear_report_folder', 'n_clicks'),
              Input('reboot', 'n_clicks'),
              prevent_initial_call=True)
 
def clear_report_fold_and_reboot(n_click, r_click):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if (button_id == 'clear_report_folder'):
        path = './data/reports'
        for f in os.listdir(path):
            os.remove('{}/{}'.format(path, f))
            #print(f)
        return None
    elif (button_id == 'reboot'):
        os.system('python reboot.py')
        return None
    else:
        return None


# Окно настроек, авторизация с помощью пароля
@app.callback(Output('drop_len_1', 'disabled'),
              Output('drop_len_2', 'disabled'),
              Output('drop_len_3', 'disabled'),
              Output('d_min_1', 'disabled'),
              Output('d_max_1', 'disabled'),
              Output('d_min_2', 'disabled'),
              Output('d_max_2', 'disabled'),
              Output('d_min_3', 'disabled'),
              Output('d_max_3', 'disabled'),
              Output('mode_name', 'disabled'),
              Output('save_mode', 'disabled'),
              Output('delete_mode', 'disabled'),
              Output('koef', 'disabled'),
              Output('set', 'disabled'),
              Output('password', 'disabled'),
              #Output('curr_user', 'data'),

              Input('mode_interval', 'n_intervals'),
              Input('password', 'value'),
              State('curr_user', 'data'))

def get_password(int, password, curr_user):
    
    ip_address = request.remote_addr
    with open(r"data/current_user.json", "r", encoding='utf-8') as f:
        user = json.load(f)

    if user['user'] == '':
        if password == conf['PASSWORD']:
            user['user'] = str(ip_address)
            with open(r"data/current_user.json", "w", encoding='utf-8') as f:
                json.dump(user, f)
            return False, False, False, False, False, False, False, False, False, False, False, False, False, False, False
        else:
            with open(r"data/current_user.json", "w", encoding='utf-8') as f:
                json.dump(user, f)
            return True, True, True, True, True, True, True, True, True, True, True, True, True, False, False

    else:
        if (password == conf['PASSWORD']) and (ip_address == user['user']):
            with open(r"data/current_user.json", "w", encoding='utf-8') as f:
                json.dump(user, f)
            return False, False, False, False, False, False, False, False, False, False, False, False, False, False, False
        elif (password != conf['PASSWORD']) and (ip_address == user['user']):
            user['user'] = ''
            with open(r"data/current_user.json", "w", encoding='utf-8') as f:
                json.dump(user, f)
            return True, True, True, True, True, True, True, True, True, True, True, True, True, False, False
        else:
            with open(r"data/current_user.json", "w", encoding='utf-8') as f:
                json.dump(user, f)
            return True, True, True, True, True, True, True, True, True, True, True, True, True, True, True


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)

