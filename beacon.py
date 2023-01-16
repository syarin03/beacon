import sys
import re
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QRegExpValidator
import pymysql

form_class = uic.loadUiType("main.ui")[0]

host_str = '10.10.21.116'
user_str = 'beacon_admin'
password_str = 'admin1234'

class User:
    def __init__(self, info):
        self.num = info[0]
        self.uid = info[1]
        self.upw = info[2]
        self.name = info[3]
        self.phone = info[4]
        self.type = info[5]


class WindowClass(QMainWindow, form_class):
    login_user = None
    isIDChecked = False
    isPWRuleChecked = False
    isPWSameChecked = False

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle('HRD-Net 짭')
        self.stackedWidget.setCurrentWidget(self.stack_title)

        engnum = QRegExp("[A-Za-z0-9]*")
        num = QRegExp("[0-9]{0,11}")
        self.edit_login_id.setValidator(QRegExpValidator(engnum, self))
        self.edit_login_pw.setValidator(QRegExpValidator(engnum, self))
        self.edit_regist_id.setValidator(QRegExpValidator(engnum, self))
        self.edit_regist_pw.setValidator(QRegExpValidator(engnum, self))
        self.edit_regist_pwck.setValidator(QRegExpValidator(engnum, self))
        self.edit_regist_phone.setValidator(QRegExpValidator(num, self))

        self.group_logout_name.setVisible(False)

        self.btn_main_to_schedule.mousePressEvent = self.go_schedule
        self.btn_main_to_message.mousePressEvent = self.go_message
        self.btn_main_to_beacon.mousePressEvent = self.go_beacon
        self.btn_main_to_login.mousePressEvent = self.go_login
        self.btn_main_to_regist.mousePressEvent = self.go_regist

        self.btn_title_to_main.mousePressEvent = self.go_main
        self.btn_message_to_main.mousePressEvent = self.go_main
        self.btn_schedule_to_main.mousePressEvent = self.go_main
        self.btn_beacon_to_main.mousePressEvent = self.go_main
        self.btn_login_to_main.mousePressEvent = self.go_main
        self.btn_regist_to_main.mousePressEvent = self.go_main

        self.btn_schedule_edit_to_schedule.mousePressEvent = self.go_schedule
        self.btn_schedule_add_to_schedule.mousePressEvent = self.go_schedule
        self.btn_schedule_add.mousePressEvent = self.go_schedule_add
        self.table_schedule.doubleClicked.connect(self.go_schedule_edit)
        self.btn_search_schedule.mousePressEvent = self.search_schedule
        self.btn_add_schedule.mousePressEvent = self.add_schedule

        self.btn_title_to_beacon.mousePressEvent = self.go_beacon

        self.btn_send.mousePressEvent = self.send_message

        self.btn_regist.mousePressEvent = self.registration
        self.btn_login.mousePressEvent = self.login
        self.btn_logout.mousePressEvent = self.logout

        self.btn_regist_idck.mousePressEvent = self.check_id
        self.stackedWidget.currentChanged.connect(self.stack_change)
        self.edit_regist_id.textChanged.connect(self.id_changed)
        self.edit_regist_pw.textChanged.connect(self.pw_changed)
        self.edit_regist_pwck.textChanged.connect(self.pw_changed)

    def stack_change(self):
        self.edit_login_id.clear()
        self.edit_login_pw.clear()
        self.edit_regist_id.clear()
        self.edit_regist_pw.clear()
        self.edit_regist_pwck.clear()
        self.edit_regist_name.clear()
        self.edit_regist_phone.clear()

        self.radio_regist_stu.setAutoExclusive(False)
        self.radio_regist_stu.setChecked(False)
        self.radio_regist_stu.setAutoExclusive(True)
        self.radio_regist_pro.setAutoExclusive(False)
        self.radio_regist_pro.setChecked(False)
        self.radio_regist_pro.setAutoExclusive(True)

    def login(self, event):
        sql = f"SELECT * FROM user WHERE uid = '{self.edit_login_id.text()}' and upw = '{self.edit_login_pw.text()}'"
        with self.conn_fetch() as cur:
            cur.execute(sql)
            result = cur.fetchall()
            if len(result) == 0:
                QMessageBox.warning(self, '경고', '아이디 또는 비밀번호가 일치하지 않습니다')
            else:
                self.login_user = User(result[0])
                QMessageBox.information(self, '알림', '로그인 되었습니다')
                self.group_login_regist.setVisible(False)
                self.group_logout_name.setVisible(True)
                self.label_login_user.setText(self.login_user.name + ' 님')
                self.stackedWidget.setCurrentWidget(self.stack_main)

    def logout(self, event):
        self.login_user = None
        QMessageBox.information(self, '알림', '로그아웃 되었습니다')
        self.group_login_regist.setVisible(True)
        self.group_logout_name.setVisible(False)
        self.label_login_user.clear()

    def registration(self, event):
        if len(self.edit_regist_id.text()) <= 0 or len(self.edit_regist_pw.text()) <= 0 or len(
                self.edit_regist_pwck.text()) <= 0 or len(self.edit_regist_name.text()) <= 0 or len(
            self.edit_regist_phone.text()) <= 0 or (
                not self.radio_regist_stu.isChecked() and not self.radio_regist_pro.isChecked()):
            QMessageBox.warning(self, '경고', '모든 입력칸을 확인해주세요')
        elif not self.isIDChecked:
            QMessageBox.warning(self, '경고', '아이디 중복 확인을 해주세요')
        elif not self.isPWRuleChecked or not self.isPWSameChecked:
            QMessageBox.warning(self, '경고', '비밀번호를 확인해주세요')
        else:
            regist_id = self.edit_regist_id.text()
            regist_pw = self.edit_regist_pw.text()
            regist_name = self.edit_regist_name.text()
            regist_phone = self.edit_regist_phone.text()
            if self.radio_regist_stu.isChecked():
                regist_type = 's'
            else:
                regist_type = 'p'
            sql = f"INSERT INTO user (uid, upw, uname, phone, type) VALUES ('{regist_id}', '{regist_pw}', '{regist_name}', '{regist_phone}', '{regist_type}')"
            print(sql)
            with self.conn_commit() as con:
                with con.cursor() as cur:
                    cur.execute(sql)
                    con.commit()
            QMessageBox.information(self, '알림', '회원가입에 성공하였습니다')
            self.stackedWidget.setCurrentWidget(self.stack_main)

    def id_changed(self):
        self.isIDChecked = False
        self.btn_regist_idck.setEnabled(True)

    def pw_changed(self):
        if self.edit_regist_pw.text().isdigit() or self.edit_regist_pw.text().isalpha() or len(
                self.edit_regist_pw.text()) < 8:
            self.label_pw_rule.setText('영문 숫자 혼용하여 8글자 이상이어야 합니다')
            self.isPWRuleChecked = False
        else:
            self.label_pw_rule.clear()
            self.isPWRuleChecked = True
        if self.edit_regist_pw.text() != self.edit_regist_pwck.text():
            self.label_pw_check.setText('비밀번호가 일치하지 않습니다')
            self.isPWSameChecked = False
        else:
            self.label_pw_check.clear()
            self.isPWSameChecked = True

    def check_id(self, event):
        sql = f"SELECT * FROM user WHERE uid = '{self.edit_regist_id.text()}'"

        with self.conn_fetch() as cur:
            cur.execute(sql)
            result = cur.fetchall()
            if len(result) == 0:
                self.isIDChecked = True
                QMessageBox.information(self, '알림', '사용 가능한 아이디입니다')
                self.btn_regist_idck.setEnabled(False)
            else:
                self.isIDChecked = False
                QMessageBox.warning(self, '경고', '이미 사용 중인 아이디입니다')
                self.btn_regist_idck.setEnabled(True)

    def go_login(self, event):
        self.stackedWidget.setCurrentWidget(self.stack_login)

    def go_regist(self, event):
        self.stackedWidget.setCurrentWidget(self.stack_regist)

    def go_message(self, event):
        if self.login_user is None:
            QMessageBox.warning(self, '경고', '로그인이 필요한 기능입니다')
            self.stackedWidget.setCurrentWidget(self.stack_login)
            return

        self.browser_message.clear()
        sql = f"SELECT a.sender_num, a.receiver_num, b.uname, a.sendtime, a.message " \
              f"FROM message a " \
              f"LEFT JOIN user b " \
              f"ON a.sender_num = b.num " \
              f"WHERE sender_num = {self.login_user.num} or receiver_num = {self.login_user.num} ORDER BY sendtime"
        with self.conn_fetch() as cur:
            cur.execute(sql)
            result = cur.fetchall()
            for i in result:
                if self.login_user.num == i[0]:
                    self.browser_message.append(
                        '<div style="text-align: right;">'
                        '<span style="font-size: 11px;color: gray;">' + str(i[3]) + '</span>'
                        '<span style="font-size: 16px;color: black;"> ' + i[4] + '</span>'
                        '</div>')
                else:
                    self.browser_message.append(
                        '<div style="text-align: left;">'
                        '<b style="font-size: 14px;">' + i[2] + '</b><br>'
                        '<span style="font-size: 16px;color: black;">' + i[4] + '</span>'
                        '<span style="font-size: 11px;color: gray;"> ' + str(i[3]) + '</span>'
                        '</div>')

        self.stackedWidget.setCurrentWidget(self.stack_message)

    def conn_fetch(self):
        con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='beacon', charset='utf8')
        cur = con.cursor()
        return cur

    def conn_commit(self):
        con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='beacon', charset='utf8')
        return con

    def go_schedule(self, event):
        if self.login_user is None:
            QMessageBox.warning(self, "경고", "로그인이 필요합니다")
            self.stackedWidget.setCurrentWidget(self.stack_login)
            return

        self.table_schedule.setRowCount(0)

        self.search_schedule(event)

        self.date_search_start.setDate(QDate.currentDate().addDays(-3))
        self.date_search_end.setDate(QDate.currentDate().addDays(3))

        self.table_schedule.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_schedule.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.stackedWidget.setCurrentWidget(self.stack_schedule_search)

    def search_schedule(self, event):
        self.table_schedule.setRowCount(0)
        start = self.date_search_start.date().toString('yyyy-MM-dd')
        end = self.date_search_end.date().toString('yyyy-MM-dd')
        sql = "select a.num, b.uname, a.start_date, a.end_date, a.content, a.ispublic_stu, a.ispublic_pro " \
              "from schedule a left join user b on a.member_num = b.num " \
              f"where (a.member_num = '{self.login_user.num}' and " \
              f"a.start_date between '{start}' and '{end}' and a.end_date between '{start}' and '{end}') "
        if self.login_user.type == 's':
            sql += f"or (a.ispublic_stu = '1' and a.start_date between '{start}' and '{end}' and a.end_date between '{start}' and '{end}')"
        else:
            sql += f"or (a.ispublic_pro = '1' and a.start_date between '{start}' and '{end}' and a.end_date between '{start}' and '{end}')"

        print(sql)

        with self.conn_fetch() as cur:
            cur.execute(sql)
            result = cur.fetchall()
            self.table_schedule.setRowCount(len(result))
            col = 0
            for i in result:
                if i[2] == i[3]:
                    self.table_schedule.setItem(col, 0, QTableWidgetItem(str(i[2])))
                else:
                    date_str = str(i[2]) + '\n~ ' + str(i[3])
                    self.table_schedule.setItem(col, 0, QTableWidgetItem(date_str))
                self.table_schedule.setItem(col, 1, QTableWidgetItem(str(i[4])))
                self.table_schedule.setItem(col, 2, QTableWidgetItem(str(i[1])))
                col += 1

    def add_schedule(self, event):
        if self.edit_add_schedule.text() == '':
            QMessageBox.warning(self, '경고', '일정 내용을 입력해주세요')
            return
        start_date = self.date_add_start.date().toString('yyyy-MM-dd')
        end_date = self.date_add_end.date().toString('yyyy-MM-dd')
        schedule_str = self.edit_add_schedule.text()
        ispublic_stu = 0
        ispublic_pro = 0
        if self.check_add_stu.isChecked():
            ispublic_stu = 1
        if self.check_add_pro.isChecked():
            ispublic_pro = 1
        sql = f"INSERT INTO schedule (member_num, start_date, end_date, content, ispublic_pro, ispublic_stu) " \
              f"VALUES ('{self.login_user.num}', '{start_date}', '{end_date}', '{schedule_str}', {ispublic_stu}, {ispublic_pro})"
        print(sql)
        with self.conn_commit() as con:
            with con.cursor() as cur:
                cur.execute(sql)
                con.commit()
        QMessageBox.information(self, '알림', '일정이 등록되었습니다')
        self.stackedWidget.setCurrentWidget(self.stack_schedule_search)

    def go_schedule_edit(self):
        row = self.table_schedule.currentIndex().row()
        col = self.table_schedule.currentIndex().column()
        print(row, col)
        data = self.table_schedule.item(row, col)
        print(data.text())
        self.stackedWidget.setCurrentWidget(self.stack_schedule_edit)

    def go_schedule_add(self, event):
        self.date_add_start.setDate(QDate.currentDate())
        self.date_add_end.setDate(QDate.currentDate())
        self.edit_add_schedule.clear()
        self.check_add_stu.setCheckState(Qt.Unchecked)
        self.check_add_pro.setCheckState(Qt.Unchecked)
        self.stackedWidget.setCurrentWidget(self.stack_schedule_add)

    def go_main(self, event):
        self.stackedWidget.setCurrentWidget(self.stack_main)

    def go_beacon(self, event):
        self.stackedWidget.setCurrentWidget(self.stack_beacon)

    def go_title(self, event):
        self.stackedWidget.setCurrentWidget(self.stack_title)

    def send_message(self, event):
        date_str = QDateTime.currentDateTime().toString('MM-dd hh:mm')
        print(date_str)
        self.browser_message.append(
            '<div style="text-align: right;">'
            '<span style="font-size: 10px;color: gray;">' + date_str + '</span>'
                                                                       '<span style="font-size: 14px;color: black;"> '
            + self.edit_message.toPlainText() +
            '</span></div>')
        print("append")
        self.edit_message.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
