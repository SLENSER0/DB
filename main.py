import datetime as dt
import psycopg2
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QTabWidget, QWidget, QVBoxLayout, QMainWindow, QHBoxLayout, QTableView, \
    QPushButton
import traceback


class MainWindow(QApplication):
    def __init__(self):
        super().__init__([])
        self.main_window = QWidget()
        self.main_window.setWindowTitle("Расписание")
        self.schedule_tables = []

        self.tabs = QTabWidget()
        self.weekdays = QTabWidget()
        self.week = QTabWidget()

        self.tabs.addTab(QWidget(), "Предметы")
        self.tabs.addTab(QWidget(), "Преподаватели")
        self.tabs.addTab(QWidget(), "Расписание")

        self.weekdays.addTab(QWidget(), 'Понедельник')
        self.weekdays.addTab(QWidget(), 'Вторник')
        self.weekdays.addTab(QWidget(), 'Среда')
        self.weekdays.addTab(QWidget(), 'Четверг')
        self.weekdays.addTab(QWidget(), 'Пятница')
        self.weekdays.addTab(QWidget(), 'Суббота')
        self.weekdays.addTab(QWidget(), 'Воскресенье')

        self.main_layout = QVBoxLayout()
        self.tab1_layout = QVBoxLayout()
        self.tab2_layout = QVBoxLayout()
        self.tab3_layout = QVBoxLayout()
        self.tab4_layout = QVBoxLayout()
        self.tab5_layout = QVBoxLayout()
        self.tab6_layout = QVBoxLayout()
        self.tab7_layout = QVBoxLayout()
        self.tab8_layout = QVBoxLayout()
        self.tab9_layout = QVBoxLayout()
        self.tab10_layout = QVBoxLayout()

        self.main_window.setLayout(self.main_layout)
        self.tabs.widget(0).setLayout(self.tab1_layout)
        self.tabs.widget(1).setLayout(self.tab2_layout)
        self.tabs.widget(2).setLayout(self.tab3_layout)

        self.weekdays.widget(0).setLayout(self.tab4_layout)
        self.weekdays.widget(1).setLayout(self.tab5_layout)
        self.weekdays.widget(2).setLayout(self.tab6_layout)
        self.weekdays.widget(3).setLayout(self.tab7_layout)
        self.weekdays.widget(4).setLayout(self.tab8_layout)
        self.weekdays.widget(5).setLayout(self.tab9_layout)
        self.weekdays.widget(6).setLayout(self.tab10_layout)

        self.main_layout.addWidget(self.tabs)
        self.tab3_layout.addWidget(self.weekdays)
        self.main_window.show()

        self.update_button = QPushButton("Update")
        self.tab3_layout.addWidget(self.update_button)
        self.update_button.clicked.connect(self.update_schedule)

        self.add_table_to_tab(self.tab1_layout, "subject")
        self.add_table_to_tab(self.tab2_layout, "teacher")

        self.db_params = {
            "host": "localhost",
            "port": "5432",
            "database": "Schedule",
            "user": "dummy",
            "password": "123456"
        }

        self.init_schedule()

    def get_days_from_weekay(self, day):
        weekdays = {
            'Понедельник': [1, 8],
            'Вторник': [2, 9],
            'Среда': [3, 10],
            'Четверг': [4, 11],
            'Пятница': [5, 12],
            'Суббота': [6, 13],
            'Воскресенье': [7, 14]
        }
        return weekdays[day]

    def get_weekday(self, number):
        weekdays = {
            1: 'Понедельник',
            2: 'Вторник',
            3: 'Среда',
            4: 'Четверг',
            5: 'Пятница',
            6: 'Суббота',
            7: 'Воскресенье'
        }
        return weekdays[number - 7 * (number > 7)]

    def query(self, query):
        conn = psycopg2.connect(**self.db_params)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def init_schedule(self):
        t1 = [self.tab4_layout, self.tab5_layout, self.tab6_layout, self.tab7_layout, self.tab8_layout,
              self.tab9_layout, self.tab10_layout]
        t2 = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

        for i, days in enumerate(t2):
            self.init_day_in_schedule(t1[i], self.get_days_from_weekay(days))

    def init_day_in_schedule(self, tab_layout, days):
        for i in range(2):
            query_str = f"SELECT * FROM {'timetable'} WHERE DAY = '{days[i]}'"
            rows = self.query(query_str)

            if len(rows) != 0:
                table_model = QStandardItemModel(len(rows), len(rows[0]))
                for i, row in enumerate(rows):
                    for j, value in enumerate(row):
                        item = QStandardItem(str(value))
                        table_model.setItem(i, j, item)
                table_view = QTableView()
                table_model.setHorizontalHeaderLabels(
                    ['id', 'day', 'subject_id', 'room_numb', 'start_time', 'teacher_id'])
                table_view.setModel(table_model)
                tab_layout.addWidget(table_view)

                table_model.itemChanged.connect(lambda item: self.handle_item_changed(item, 'timetable', table_view))

                join_button = QPushButton("Join")
                join_button.clicked.connect(
                    lambda _, table_view=table_view: self.add_row_to_table(table_view, 'timetable'))
                tab_layout.addWidget(join_button)

                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(
                    lambda _, table_view=table_view: self.delete_selected_row(table_view, 'timetable'))
                tab_layout.addWidget(delete_button)

                self.schedule_tables.append(table_view)

            else:
                empty_table_view = QTableView()
                empty_table_model = QStandardItemModel()
                empty_table_model.setHorizontalHeaderLabels(
                    ['id', 'day', 'subject_id', 'room_numb', 'start_time', 'teacher_id'])
                empty_table_view.setModel(empty_table_model)
                tab_layout.addWidget(empty_table_view)

                join_button = QPushButton("Join")
                join_button.clicked.connect(
                    lambda _, table_view=empty_table_view: self.add_row_to_table(empty_table_view, 'timetable'))
                tab_layout.addWidget(join_button)

                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(
                    lambda _, table_view=empty_table_view: self.delete_selected_row(empty_table_view, 'timetable'))
                tab_layout.addWidget(delete_button)

                self.schedule_tables.append(empty_table_view)

    def update_schedule(self):
        for tab_layout in [self.tab4_layout, self.tab5_layout, self.tab6_layout, self.tab7_layout,
                           self.tab8_layout, self.tab9_layout, self.tab10_layout]:
            while tab_layout.count():
                item = tab_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        self.schedule_tables = []
        self.init_schedule()

    def add_row_to_table(self, table_view, table_name):
        try:
            table_model = table_view.model()
            column_count = table_model.columnCount()

            row_count = table_model.rowCount()

            table_model.insertRow(row_count)

            k = self.query(f'SELECT id FROM {table_name} ORDER BY id DESC LIMIT 1')[0][0]
            index = table_model.index(k, 0)
            table_model.setData(index, k + 1)

            val = ('1,' * (column_count - 1))[:-1]
            if len(val) > 5:
                val = f"1, 1, 1, '{dt.time(0, 0)}', 1"

            conn = psycopg2.connect(**self.db_params)
            cur = conn.cursor()
            cur.execute(f'INSERT INTO {table_name} VALUES ({k + 1},{val})')
            conn.commit()
            conn.close()

            if table_name != 'timetable':
                self.update_table()
            else:
                self.update_schedule()
        except Exception as e:
            print(e)

    def delete_selected_row(self, table_view, table_name):
        try:
            table_model = table_view.model()
            selected_indexes = table_view.selectedIndexes()

            headers = self.extract(self.query(
                f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ORDINAL_POSITION;"))

            conn = psycopg2.connect(**self.db_params)
            cur = conn.cursor()
            cur.execute(f'DELETE FROM {table_name} WHERE {headers[0]} = {table_model.data(selected_indexes[0])}')
            conn.commit()
            conn.close()

            if selected_indexes:
                unique_rows = set()
                for index in selected_indexes:
                    unique_rows.add(index.row())

                for row in sorted(unique_rows, reverse=True):
                    table_model.removeRow(row)
            if table_name != 'timetable':
                self.update_table()
            else:
                self.update_schedule()
        except Exception as e:
            print(e)

    def extract(self, lst):
        return [item[0] for item in lst]

    def add_table_to_tab(self, tab_layout, table_name):
        query_str = f"SELECT * FROM {table_name}"
        rows = self.query(query_str)
        headers = self.extract(self.query(
            f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ORDINAL_POSITION;"))
        table_model = QStandardItemModel(len(rows), len(rows[0]))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QStandardItem(str(value))
                table_model.setItem(i, j, item)
        table_view = QTableView()
        table_model.setHorizontalHeaderLabels(headers)
        table_view.setModel(table_model)
        tab_layout.addWidget(table_view)

        table_model.itemChanged.connect(lambda item: self.handle_item_changed(item, table_name, table_view))

        update_button = QPushButton("Update")
        update_button.clicked.connect(lambda: self.update_table())
        tab_layout.addWidget(update_button)

        join_button = QPushButton("Join")
        join_button.clicked.connect(lambda _, table_view=table_view: self.add_row_to_table(table_view, table_name))
        tab_layout.addWidget(join_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda _, table_view=table_view: self.delete_selected_row(table_view, table_name))
        tab_layout.addWidget(delete_button)

    def update_table(self):
        try:
            for tab_layout in [self.tab1_layout, self.tab2_layout]:
                while tab_layout.count():
                    item = tab_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()

            self.add_table_to_tab(self.tab1_layout, "subject")
            self.add_table_to_tab(self.tab2_layout, "teacher")
        except Exception as e:
            print(f"Ошибка при обновлении таблицы: {e}")
            traceback.print_exc()

    def handle_item_changed(self, item, table_name, table_view):
        try:
            headers = self.extract(self.query(
                f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ORDINAL_POSITION;"))
            column = item.column()
            new_value = item.text()
            conn = psycopg2.connect(**self.db_params)
            cur = conn.cursor()
            cur.execute(
                f"UPDATE {table_name} SET \"{headers[column]}\"='{new_value}' WHERE id = {self.get_row_values(table_view)[0]}")
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Ошибка при изменении таблицы: {e}")
            traceback.print_exc()

    def get_row_values(self, table_view):
        table_model = table_view.model()
        selection_model = table_view.selectionModel()

        selected_indexes = selection_model.selectedIndexes()
        if len(selected_indexes) > 0:
            row = selected_indexes[0].row()
            row_values = []
            for column in range(table_model.columnCount()):
                index = table_model.index(row, column)
                value = table_model.data(index)
                row_values.append(value)
            return row_values
        else:
            return None


app = MainWindow()
app.exec()
