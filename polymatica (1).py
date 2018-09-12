# coding=utf-8
import pandas as pd


class Polymatica:
    # Конструктор,сюда мы передаём четыре параметра : Логин\Пароль\Метод начала сессии\Урл
    def __init__(self, login, password, start, url):
        self.login = login
        self.password = password
        self.start = start
        self.url = url

        authorization = '{"state":0,"session":"","queries":[{"uuid":"00000000-00000000-00000000-00000000","command":{"plm_type_code":205,"state":2,"login":"%s","passwd":"%s","locale":1}}]}' % (self.login, self.password)
        authorization_response = self.start.post(self.url, data=authorization).json()

        self.session_number = authorization_response['queries'][0]['command']['session_id'] # Номер сессии
        self.uuid_number = authorization_response['queries'][0]['command']['manager_uuid'] # Уникальный номер

        self.retcode = 0

        # Условие проверки правильности выполнения запроса
        if self.session_number and self.uuid_number is not None:
            print("Cессия : %s и Уид : %s" % (self.session_number, self.uuid_number))
        else:
            self.retcode = -1

    # открытие куба
    def get_cube_1(self, cube_name_1):
        # Получаем номер слоя
        get_layer = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":210,"state":21}}]}' % (self.session_number, self.uuid_number)
        get_layer_response = self.start.post(self.url, data=get_layer).json()

        #print(get_layer_response)

        self.layer_id = get_layer_response['queries'][0]['command']['layers'][0]['uuid'] # Номер слоя

        self.retcode = 0

        if self.layer_id is None:
            self.retcode = -2
            exit()

        #print("Слой : %s" % (self.layer_id))

        # Получаем все доступные имена кубов и их uuid
        list_cubes = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":208,"state":1}}]}' % (self.session_number, self.uuid_number)
        list_cubes_response = self.start.post(self.url, data=list_cubes).json()

        #print(list_cubes_response)

        self.cube_uuid_1 = list_cubes_response['queries'][0]['command']['cubes'] # Содержит все имена кубов и их номера

        # Все уникальные номера кубов
        all_cubes_uuid = []
        for x in self.cube_uuid_1:
            all_cubes_uuid.append(x['uuid'])

        # Все имена кубов
        all_names_cubes = []
        for x in self.cube_uuid_1:
            all_names_cubes.append(x['name'])

        all_names_and_uuids = (all_cubes_uuid, all_names_cubes) # Здесь лежат уникальные номера кубов и их имена в двух списках

        index_cubes = all_names_and_uuids[1].index(cube_name_1)# Сюда падает название куба из poly_start (cube_name)

        self.id_cube_1 = all_names_and_uuids[0][index_cubes] # Возвращаем по индеку уникальный номер куба


        if self.cube_uuid_1 is None:
            self.retcode = -3
            exit()

        #print("ID куба для открытия : %s " % (self.id_cube_1))

        # Открываем куб (из poly_start) и забираем модуль куба
        open_cube = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":208,"state":16,"cube_id":"%s","layer_id":"%s","module_id":"00000000-00000000-00000000-00000000"}}]}' % (self.session_number, self.uuid_number, self.id_cube_1, self.layer_id)
        open_cube_response = self.start.post(self.url, data=open_cube).json()

        #print(open_cube_response)

        self.module_cube_1 = open_cube_response['queries'][0]['command']['module_desc']['uuid'] # Содержит модуль открытого куба

        if self.module_cube_1 is None:
            self.retcode = -4
            return None

        #print( "Модуль открытого куба : %s" % (self.module_cube_1))
        return self.cube_uuid_1


    # Метод получения названий размерностей открытого куба
    def get_the_dimensions_and_facts_1(self, dimensions_1, facts_1):

        dimensions_names = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":502,"state":1}}]}' % (self.session_number, self.module_cube_1)
        dimensions_names_response = self.start.post(self.url, data=dimensions_names).json()

        self.dimensions_1 = dimensions_names_response['queries'][0]['command']['dimensions'] # Содержит названия и id размерностей

        # Все имена размерностей открытого куба
        all_names_dimensions = []
        for x in self.dimensions_1:
            all_names_dimensions.append(x['name'])

        # Все id размерностей открытого куба
        all_id_dimensions = []
        for x in self.dimensions_1:
            all_id_dimensions.append(x['id'])

        all_names_and_id_dimensions = (all_id_dimensions, all_names_dimensions) # Здесь лежат id размерностей и их имена в двух списках
        #print('Размерности', all_names_and_id_dimensions)

        self.retcode = 0

        facts_names = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":503,"state":1}}]}' % (self.session_number, self.module_cube_1)
        facts_names_response = self.start.post(self.url, data=facts_names).json()

        self.facts_1 = facts_names_response['queries'][0]['command']['facts'] # Cодержит названия фактов и их id

        # Имена фактов открытого куба
        all_facts_names = []
        for x in self.facts_1:
            all_facts_names.append(x['name'])

        # id фактов открытого куба
        all_facts_id = []
        for x in self.facts_1:
            all_facts_id.append(x['id'])

        all_facts_names_and_id = (all_facts_id, all_facts_names) # Здесь лежат id фактов и их имена в двух списках
        #print('Факты', all_facts_names_and_id)

        # Выделение фактов
        for x in facts_1:
            res = set(facts_1) ^ set(all_facts_names)
            for x in res:
                i = all_facts_names_and_id[1].index(x)
                self.id_fact_1 = all_facts_names_and_id[0][i]
                pick_facts = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":503,"state":13,"fact":"%s","is_seleceted":true}}]}' % (self.session_number, self.module_cube_1, self.id_fact_1)
                pick_facts_response = self.start.post(self.url, data=pick_facts).json()
                #print('Выделен Факт', x)

        # Удаление фактов открытого куба
        delete_facts_open_cube = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":503,"state":19}}]}' % (self.session_number, self.module_cube_1)
        delete_facts_open_cube_response = self.start.post(self.url, data=delete_facts_open_cube).json()


        # Метод перемещения размерностей открытого куба (left)
        for x in dimensions_1:
            i = all_names_and_id_dimensions[1].index(x)
            self.id_dimension_left_1 = all_names_and_id_dimensions[0][i]
            self.level_left_1 = dimensions_1.index(x)
            dimensions_move_left = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":502,"state":3,"position":%s,"id":"%s","level":%s}}]}' % (self.session_number, self.module_cube_1, 1, self.id_dimension_left_1, self.level_left_1)
            dimensions_move_left_response = self.start.post(self.url, data=dimensions_move_left).json()


        # Развернуть размерности (left)
        for x in dimensions_1:
            i = all_names_and_id_dimensions[1].index(x)
            self.lvl_left_1 = dimensions_1.index(x) - 1
            expand_dimensions_left = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":506,"state":13,"position":%s,"level":%s}}]}' % (self.session_number, self.module_cube_1, 1, self.lvl_left_1)
            expand_dimensions_left_response = self.start.post(self.url, data=expand_dimensions_left).json()

        # Убираем всего
        close_total = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":506,"state":21}}]}' % (self.session_number, self.module_cube_1)
        close_total_response = self.start.post(self.url, data=close_total).json()

        # Получаем данные рабочей области
        workplace_data = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":506,"state":1,"from_row":0,"from_col":0,"num_row":10000,"num_col":10000}}]}' % (self.session_number, self.module_cube_1)
        workplace_data_response = self.start.post(self.url, data=workplace_data).json()

        self.top_1 = workplace_data_response['queries'][0]['command']['top'] # Массив данных, формирующих область заголовков для столбцов с данными
        self.left_1 = workplace_data_response['queries'][0]['command']['left'] # Формирование левой части заголовков строк, начиная с первой строки с данными
        self.data_1 = workplace_data_response['queries'][0]['command']['data'] # Массив данных со значениями

        del self.data_1[-1] # Удаление последнего элемента в массиве данных со значениями (Удаление значения 'Всего')
        del self.left_1[-1] # Удаление последнего элемента в массиве с размерностями ('Всего')

        for line in self.left_1:
            if self.left_1.index(line) == 0:
                for i in range(0, len(line)):
                    line[i] = line[i]['value']
            else:
                for i in range(0, len(line)):
                    if 'value' in line[i]:
                        line[i] = line[i]['value']
                    else:
                        line[i] = self.left_1[self.left_1.index(line) - 1][i]

        table = pd.DataFrame(self.left_1, columns=dimensions_1).assign(**pd.DataFrame(self.data_1, columns=facts_1))


        #pivot_df = pd.pivot_table(table, index=dimensions_1[1], columns=dimensions_1[0], values=['Loss qty'])

        # Закрываем рабочий модуль
        close_module = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":207,"state":10,"module_id":"%s"}}]}' % (self.session_number, self.uuid_number, self.module_cube_1)
        close_module_response = self.start.post(self.url, data=close_module).json()

        #print(pivot_df)
        #print(table)
        #print(self.data_1)
        #print(self.left_1)
        return table

        # открытие куба
    def get_cube_2(self, cube_name_2):
        # Получаем все доступные имена кубов и их uuid
        list_cubes = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":208,"state":1}}]}' % (self.session_number, self.uuid_number)
        list_cubes_response = self.start.post(self.url, data=list_cubes).json()

        #print(list_cubes_response)

        self.cube_uuid_2 = list_cubes_response['queries'][0]['command']['cubes']  # Содержит все имена кубов и их номера

        # Все уникальные номера кубов
        all_cubes_uuid = []
        for x in self.cube_uuid_2:
            all_cubes_uuid.append(x['uuid'])

        # Все имена кубов
        all_names_cubes = []
        for x in self.cube_uuid_2:
            all_names_cubes.append(x['name'])

        all_names_and_uuids = (
            all_cubes_uuid, all_names_cubes)  # Здесь лежат уникальные номера кубов и их имена в двух списках

        index_cubes = all_names_and_uuids[1].index(cube_name_2)  # Сюда падает название куба из poly_start (cube_name)

        self.id_cube_2 = all_names_and_uuids[0][index_cubes]  # Возвращаем по индеку уникальный номер куба

        if self.cube_uuid_2 is None:
            self.retcode = -3
            exit()

        #print("ID куба для открытия : %s " % (self.id_cube_2))

        # Открываем куб (из poly_start) и забираем модуль куба
        open_cube = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":208,"state":16,"cube_id":"%s","layer_id":"%s","module_id":"00000000-00000000-00000000-00000000"}}]}' % (self.session_number, self.uuid_number, self.id_cube_2, self.layer_id)
        open_cube_response = self.start.post(self.url, data=open_cube).json()

        #print(open_cube_response)

        self.module_cube_2 = open_cube_response['queries'][0]['command']['module_desc']['uuid']  # Содержит модуль открытого куба

        if self.module_cube_2 is None:
            self.retcode = -4
            return None

        #print("Модуль открытого куба : %s" % (self.module_cube_2))
        return self.cube_uuid_2

        # Метод получения названий размерностей открытого куба
    def get_the_dimensions_and_facts_2(self, dimensions_2, facts_2):

        dimensions_names = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":502,"state":1}}]}' % (self.session_number, self.module_cube_2)
        dimensions_names_response = self.start.post(self.url, data=dimensions_names).json()

        self.dimensions_2 = dimensions_names_response['queries'][0]['command']['dimensions']  # Содержит названия и id размерностей

        # Все имена размерностей открытого куба
        all_names_dimensions = []
        for x in self.dimensions_2:
            all_names_dimensions.append(x['name'])

        # Все id размерностей открытого куба
        all_id_dimensions = []
        for x in self.dimensions_2:
            all_id_dimensions.append(x['id'])

        all_names_and_id_dimensions = (all_id_dimensions, all_names_dimensions)  # Здесь лежат id размерностей и их имена в двух списках
        #print('Размерности', all_names_and_id_dimensions)

        self.retcode = 0

        facts_names = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":503,"state":1}}]}' % (self.session_number, self.module_cube_2)
        facts_names_response = self.start.post(self.url, data=facts_names).json()

        self.facts_2 = facts_names_response['queries'][0]['command']['facts']  # Cодержит названия фактов и их id

        # Имена фактов открытого куба
        all_facts_names = []
        for x in self.facts_2:
            all_facts_names.append(x['name'])

        # id фактов открытого куба
        all_facts_id = []
        for x in self.facts_2:
            all_facts_id.append(x['id'])

        all_facts_names_and_id = (all_facts_id, all_facts_names)  # Здесь лежат id фактов и их имена в двух списках
        #print('Факты', all_facts_names_and_id)

        # Выделение фактов
        for x in facts_2:
            res = set(facts_2) ^ set(all_facts_names)
            for x in res:
                i = all_facts_names_and_id[1].index(x)
                self.id_fact_2 = all_facts_names_and_id[0][i]
                pick_facts = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":503,"state":13,"fact":"%s","is_seleceted":true}}]}' % (self.session_number, self.module_cube_2, self.id_fact_2)
                pick_facts_response = self.start.post(self.url, data=pick_facts).json()
                #print('Выделен Факт', x)

        # Удаление фактов открытого куба
        delete_facts_open_cube = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":503,"state":19}}]}' % (self.session_number, self.module_cube_2)
        delete_facts_open_cube_response = self.start.post(self.url, data=delete_facts_open_cube).json()

        # Метод перемещения размерностей открытого куба (left)
        for x in dimensions_2:
            i = all_names_and_id_dimensions[1].index(x)
            self.id_dimension_left_2 = all_names_and_id_dimensions[0][i]
            self.level_left_2 = dimensions_2.index(x)
            dimensions_move_left = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":502,"state":3,"position":%s,"id":"%s","level":%s}}]}' % (self.session_number, self.module_cube_2, 1, self.id_dimension_left_2, self.level_left_2)
            dimensions_move_left_response = self.start.post(self.url, data=dimensions_move_left).json()

        # Развернуть размерности (left)
        for x in dimensions_2:
            i = all_names_and_id_dimensions[1].index(x)
            self.lvl_left_2 = dimensions_2.index(x) - 1
            expand_dimensions_left = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":506,"state":13,"position":%s,"level":%s}}]}' % (self.session_number, self.module_cube_2, 1, self.lvl_left_2)
            expand_dimensions_left_response = self.start.post(self.url, data=expand_dimensions_left).json()

        # Убираем всего
        close_total = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":506,"state":21}}]}' % (self.session_number, self.module_cube_2)
        close_total_response = self.start.post(self.url, data=close_total).json()

        # Получаем данные рабочей области
        workplace_data = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":506,"state":1,"from_row":0,"from_col":0,"num_row":10000,"num_col":10000}}]}' % (self.session_number, self.module_cube_2)
        workplace_data_response = self.start.post(self.url, data=workplace_data).json()

        self.top_2 = workplace_data_response['queries'][0]['command']['top']  # Массив данных, формирующих область заголовков для столбцов с данными
        self.left_2 = workplace_data_response['queries'][0]['command']['left']  # Формирование левой части заголовков строк, начиная с первой строки с данными
        self.data_2 = workplace_data_response['queries'][0]['command']['data']  # Массив данных со значениями

        del self.data_2[-1]  # Удаление последнего элемента в массиве данных со значениями (Удаление значения 'Всего')
        del self.left_2[-1]  # Удаление последнего элемента в массиве с размерностями ('Всего')

        for line in self.left_2:
            if self.left_2.index(line) == 0:
                for i in range(0, len(line)):
                    line[i] = line[i]['value']
            else:
                for i in range(0, len(line)):
                    if 'value' in line[i]:
                        line[i] = line[i]['value']
                    else:
                        line[i] = self.left_2[self.left_2.index(line) - 1][i]

        table = pd.DataFrame(self.left_2, columns=dimensions_2).assign(**pd.DataFrame(self.data_2, columns=facts_2))

        #pivot_df = pd.pivot_table(table, index=dimensions_2[1], columns=dimensions_2[0], values=['Closing Stock(Proj.)', 'Total Shortfall', 'UFO'])

        # Закрываем рабочий модуль
        close_module = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":207,"state":10,"module_id":"%s"}}]}' % (self.session_number, self.uuid_number, self.module_cube_2)
        close_module_response = self.start.post(self.url, data=close_module).json()

        #print(pivot_df)
        #print(table)
        #print(self.data_2)
        #print(self.left_2)
        return table

        # открытие куба
    def get_cube_3(self, cube_name_3):
        # Получаем все доступные имена кубов и их uuid
        list_cubes = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":208,"state":1}}]}' % (self.session_number, self.uuid_number)
        list_cubes_response = self.start.post(self.url, data=list_cubes).json()

        #print(list_cubes_response)

        self.cube_uuid_3 = list_cubes_response['queries'][0]['command']['cubes']  # Содержит все имена кубов и их номера

        # Все уникальные номера кубов
        all_cubes_uuid = []
        for x in self.cube_uuid_3:
            all_cubes_uuid.append(x['uuid'])

        # Все имена кубов
        all_names_cubes = []
        for x in self.cube_uuid_3:
            all_names_cubes.append(x['name'])

        all_names_and_uuids = (all_cubes_uuid, all_names_cubes)  # Здесь лежат уникальные номера кубов и их имена в двух списках

        index_cubes = all_names_and_uuids[1].index(cube_name_3)  # Сюда падает название куба из poly_start (cube_name)

        self.id_cube_3 = all_names_and_uuids[0][index_cubes]  # Возвращаем по индеку уникальный номер куба

        if self.cube_uuid_3 is None:
            self.retcode = -3
            exit()

        #print("ID куба для открытия : %s " % (self.id_cube_3))

        # Открываем куб (из poly_start) и забираем модуль куба
        open_cube = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":208,"state":16,"cube_id":"%s","layer_id":"%s","module_id":"00000000-00000000-00000000-00000000"}}]}' % (self.session_number, self.uuid_number, self.id_cube_3, self.layer_id)
        open_cube_response = self.start.post(self.url, data=open_cube).json()

        #print(open_cube_response)

        self.module_cube_3 = open_cube_response['queries'][0]['command']['module_desc']['uuid']  # Содержит модуль открытого куба

        if self.module_cube_3 is None:
            self.retcode = -4
            return None

        #print("Модуль открытого куба : %s" % (self.module_cube_3))
        return self.cube_uuid_3

        # Метод получения названий размерностей открытого куба
    def get_the_dimensions_and_facts_3(self, dimensions_3, facts_3):

        dimensions_names = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":502,"state":1}}]}' % (self.session_number, self.module_cube_3)
        dimensions_names_response = self.start.post(self.url, data=dimensions_names).json()

        self.dimensions_3 = dimensions_names_response['queries'][0]['command']['dimensions']  # Содержит названия и id размерностей

        # Все имена размерностей открытого куба
        all_names_dimensions = []
        for x in self.dimensions_3:
            all_names_dimensions.append(x['name'])

        # Все id размерностей открытого куба
        all_id_dimensions = []
        for x in self.dimensions_3:
            all_id_dimensions.append(x['id'])

        all_names_and_id_dimensions = (all_id_dimensions, all_names_dimensions)  # Здесь лежат id размерностей и их имена в двух списках
        #print('Размерности', all_names_and_id_dimensions)

        self.retcode = 0

        facts_names = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":503,"state":1}}]}' % (self.session_number, self.module_cube_3)
        facts_names_response = self.start.post(self.url, data=facts_names).json()

        self.facts_3 = facts_names_response['queries'][0]['command']['facts']  # Cодержит названия фактов и их id

        # Имена фактов открытого куба
        all_facts_names = []
        for x in self.facts_3:
            all_facts_names.append(x['name'])

        # id фактов открытого куба
        all_facts_id = []
        for x in self.facts_3:
            all_facts_id.append(x['id'])

        all_facts_names_and_id = (all_facts_id, all_facts_names)  # Здесь лежат id фактов и их имена в двух списках
        #print('Факты', all_facts_names_and_id)

        # Выделение фактов
        for x in facts_3:
            res = set(facts_3) ^ set(all_facts_names)
            for x in res:
                i = all_facts_names_and_id[1].index(x)
                self.id_fact_3 = all_facts_names_and_id[0][i]
                pick_facts = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":503,"state":13,"fact":"%s","is_seleceted":true}}]}' % (self.session_number, self.module_cube_3, self.id_fact_3)
                pick_facts_response = self.start.post(self.url, data=pick_facts).json()
                #print('Выделен Факт', x)

        # Удаление фактов открытого куба
        delete_facts_open_cube = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":503,"state":19}}]}' % (self.session_number, self.module_cube_3)
        delete_facts_open_cube_response = self.start.post(self.url, data=delete_facts_open_cube).json()

        # Метод перемещения размерностей открытого куба (left)
        for x in dimensions_3:
            i = all_names_and_id_dimensions[1].index(x)
            self.id_dimension_left_3 = all_names_and_id_dimensions[0][i]
            self.level_left_3 = dimensions_3.index(x)
            dimensions_move_left = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":502,"state":3,"position":%s,"id":"%s","level":%s}}]}' % (self.session_number, self.module_cube_3, 1, self.id_dimension_left_3, self.level_left_3)
            dimensions_move_left_response = self.start.post(self.url, data=dimensions_move_left).json()

        # Развернуть размерности (left)
        for x in dimensions_3:
            i = all_names_and_id_dimensions[1].index(x)
            self.lvl_left_3 = dimensions_3.index(x) - 1
            expand_dimensions_left = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":506,"state":13,"position":%s,"level":%s}}]}' % (self.session_number, self.module_cube_3, 1, self.lvl_left_3)
            expand_dimensions_left_response = self.start.post(self.url, data=expand_dimensions_left).json()

        # Убираем всего
        close_total = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":506,"state":21}}]}' % (self.session_number, self.module_cube_3)
        close_total_response = self.start.post(self.url, data=close_total).json()

        # Получаем данные рабочей области
        workplace_data = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":506,"state":1,"from_row":0,"from_col":0,"num_row":10000,"num_col":10000}}]}' % (self.session_number, self.module_cube_3)
        workplace_data_response = self.start.post(self.url, data=workplace_data).json()

        self.top_3 = workplace_data_response['queries'][0]['command']['top']  # Массив данных, формирующих область заголовков для столбцов с данными
        self.left_3 = workplace_data_response['queries'][0]['command']['left']  # Формирование левой части заголовков строк, начиная с первой строки с данными
        self.data_3 = workplace_data_response['queries'][0]['command']['data']  # Массив данных со значениями

        del self.data_3[-1]  # Удаление последнего элемента в массиве данных со значениями (Удаление значения 'Всего')
        del self.left_3[-1]  # Удаление последнего элемента в массиве с размерностями ('Всего')

        for line in self.left_3:
            if self.left_3.index(line) == 0:
                for i in range(0, len(line)):
                    line[i] = line[i]['value']
            else:
                for i in range(0, len(line)):
                    if 'value' in line[i]:
                        line[i] = line[i]['value']
                    else:
                        line[i] = self.left_3[self.left_3.index(line) - 1][i]

        table = pd.DataFrame(self.left_3, columns=dimensions_3).assign(**pd.DataFrame(self.data_3, columns=facts_3))

        # pivot_df = pd.pivot_table(table, index=dimensions_2[1], columns=dimensions_2[0], values=['Closing Stock(Proj.)', 'Total Shortfall', 'UFO'])

        # Закрываем рабочий модуль
        close_module = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":207,"state":10,"module_id":"%s"}}]}' % (self.session_number, self.uuid_number, self.module_cube_3)
        close_module_response = self.start.post(self.url, data=close_module).json()

        end_session = '{"state":0,"session":"%s","queries":[{"uuid":"%s","command":{"plm_type_code":206,"state":10}}]}' % (self.session_number, self.uuid_number)
        end_session_response = self.start.post(self.url, data=end_session).json()

        #print(pivot_df)
        #print(table)
        #print(self.data_3)
        #print(self.left_3)
        return table






















        












































