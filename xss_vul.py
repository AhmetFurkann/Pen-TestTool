
import LogEditor
import datetime
import getpass
import time

from selenium.common.exceptions import NoAlertPresentException
from login_utilty import input_check
from selenium import webdriver


class XssVulCheck:

    def __init__(self):
        self.browser = webdriver.Chrome()
        self.__Log = LogEditor.LogFile()


    def login_check_via_sel(self, host):
        # options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        # browser = webdriver.Chrome()
        # browser = webdriver.Chrome(options=options)
        process_name = "XSS Zaafiyeti Giriş Sayfası Kontrolü"
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        started_time = datetime.datetime.now().strftime("%H:%M:%S")
        # TODO: The three information should be in LogEditor file
        self.browser.get(host)

        username_element_check = False
        password_element_check = False
        submit_element = False

        forms = self.browser.find_elements_by_tag_name("form")
        for form in forms:
            elements = form.find_elements_by_tag_name("input")
            for element in elements:
                if element.get_attribute("type") == "text":
                    username_element_check = True
                elif element.get_attribute("type") == "password":
                    password_element_check = True
                elif element.get_attribute("type") == "submit":
                    submit_element = True

        if username_element_check and password_element_check and submit_element:
            process_statu = "Başarılı"
            detail = "{} web sayfası bir giriş sayfası olarak belirlenmiştir.".format(host)
            finish_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.__Log.insert_to_log(process_name, process_statu,date,started_time,finish_time, detail)
            return True
        else:
            process_statu = "Başarısız"
            detail = "{} web sayfası üzerinde bir giriş sayfası bulunamamıştır.".format(host)
            finish_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.__Log.insert_to_log(process_name, process_statu, date, started_time, finish_time, detail)
            return False


    def login_into_site(self, host):
        # TODO: Only check for one form of the page
        #   It should check if the page has more than one login form
        process_name = "XSS Zaafiyeti Giriş Sayfasına Giriş Denemesi"
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        started_time = datetime.datetime.now().strftime("%H:%M:%S")
        username_input, password_input, submit_element, form= self.load_login_elements(host)
        if username_input and password_input and submit_element is not None:
            login_form_attribute = form.get_attribute("action")
            while True:
                # TODO: should be checked for other form attribute
                #   because it can be changed from site to site
                #   like 'id' and for other attributes
                username = input("Lütfen kullanıcı adını giriniz: ")
                password = getpass.getpass(prompt="Lütfen şifreyi giriniz: ")
                username_input.send_keys(username)
                password_input.send_keys(password)
                submit_element.click()
                forms = self.browser.find_elements_by_tag_name("form")
                if not self.compare_forms(login_form_attribute, "action", forms):
                    print("Başarılı ile giriş yaptınız.")
                    process_statu = "Başarılı"
                    detail = "{} web sayfasına giriş işlemi gerçekleştirilmiştir..".format(host)
                    finish_time = datetime.datetime.now().strftime("%H:%M:%S")
                    self.__Log.insert_to_log(process_name, process_statu, date, started_time, finish_time, detail)
                    return True
                else:
                    print("Kuallınıcı adı veyahut şifreniz yanlış lütfen tekrar giriniz.")
                    process_statu = "Başarılı"
                    detail = "{} web sayfasına giriş işlemi gerçekleştirilmiştir..".format(host)
                    finish_time = datetime.datetime.now().strftime("%H:%M:%S")
                    self.__Log.insert_to_log(process_name, process_statu, date, started_time, finish_time, detail)
                    username_input, password_input, submit_element, form = self.load_login_elements(host)

    def xss_vul_check(self, host):

        self.browser.get(host)
        text_element = list()
        alert_informations = []
        with open("xss_vectors.txt", "r") as xss_vectors:
            for vector in xss_vectors:
                vector = vector.replace("\n", "")
                print(vector)
                text_element = self.load_all_text_element(host)
                alert_control = False
                while True:
                    if len(text_element) == 0:
                        break
                    else:
                        element = text_element[len(text_element)-1]
                        try_element = self.browser.find_element_by_xpath("//input[@type='{0}']".format(element))
                        print(try_element.get_attribute("type"))
                        try_element.send_keys(vector)
                        try_element.submit()
                        try:
                            alert = self.browser.switch_to.alert
                            print(alert.text)
                            alert.accept()
                        except NoAlertPresentException as error:
                            print("Alert oluşmadı")
                            alert_control = True
                        if not alert_control:
                            alert_informations.append(["XSS Vulnerable Site : {}".format(host), "Alert Keyword: {}".format(vector)])
                        text_element.pop()
                        print("Length of all text element liste : ", len(text_element))
        return alert_informations

    def load_all_text_element(self, host):

        all_text_element = list()
        self.browser.get(host)
        all_input_element = self.browser.find_elements_by_tag_name("input")
        for element in all_input_element:
            if element.get_attribute("type") == "text" or element.get_attribute("type") == "password":
                all_text_element.append(element.get_attribute("type"))
        return all_text_element

    def compare_forms(self, object, attribute, form_list):

        for form in form_list:
            if form.get_attribute(attribute) == object:
                print("Hala aynı sitedesiniz!")
                return True

    def load_login_elements(self, host):

        self.browser.get(host)
        username_input = None
        password_input = None
        submit_element = None
        forms = self.browser.find_elements_by_tag_name("form")
        for form in forms:
            print("INFO (Forum Type)", form.get_attribute("action"))
            elements = form.find_elements_by_tag_name("input")
            for element in elements:
                if element.get_attribute("type") == "text":
                    username_input = element
                elif element.get_attribute("type") == "password":
                    password_input = element
                elif element.get_attribute("type") == "submit":
                    submit_element = element
        # TODO: Element should be checked before they've returned
        return username_input, password_input, submit_element, form

    def start_xss(self, host):
        answer = None
        xss_vul_page = list()
        xss_vul_login = list()
        login_page_statu = self.login_check_via_sel(host)
        if login_page_statu:
            print("{0} web sayfası bir giriş sayfasıdır!\n"
                  "Bu sayfa üzerinde XSS zaafiiyeti denemesi yapılsın mı ?"
                  "".format(host))
            print("CEVAP (E/H): ", end="")
            answer = input_check("e", "h")
        else:
            print("{0} web sayfasına XSS zafiyeti başlatılıyor!".format(host))
            print("3")
            time.sleep(1)
            print("2")
            time.sleep(1)
            print("1")
            xss_vul_page = self.xss_vul_check(host)

        process_name = "XSS Zaafiyeti Taraması"
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        started_time = datetime.datetime.now().strftime("%H:%M:%S")

        if answer:
            xss_vul_login = self.xss_vul_check(host)
            login_control = self.login_into_site(host)
            xss_vul_page = self.xss_vul_check(host)

        elif not answer:
            login_control = self.login_into_site(host)
            xss_vul_page = self.xss_vul_check(host)

        detail = "{} web sayfasına XSS taraması gerçekleştirilmiştir.\n".format(host)
        process_statu = "Başarılı"

        if len(xss_vul_page) != 0 and len(xss_vul_login) != 0:
            xss_vul_page = xss_vul_page + xss_vul_login
            for vulnerable_page in xss_vul_login:
                detail = detail + vulnerable_page[0] + vulnerable_page[1]
            finish_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.__Log.insert_to_log(process_name, process_statu, date, started_time, finish_time, detail)

        elif len(xss_vul_page) != 0:
            print(xss_vul_page)
            for vulnerable_page in xss_vul_page:
                detail = detail + vulnerable_page[0] + " " + vulnerable_page[1]
            finish_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.__Log.insert_to_log(process_name, process_statu, date, started_time, finish_time, detail)

        elif len(xss_vul_login) != 0:
            print(xss_vul_login)
            for vulnerable_page in xss_vul_login:
                detail = detail + vulnerable_page[0] + vulnerable_page[1]
            finish_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.__Log.insert_to_log(process_name, process_statu, date, started_time, finish_time, detail)

        else:
            process_statu = "Başarısız."
            message = "XSS Zaafiyeti Bulunmamıştır.\n"
            detail = detail + message
            finish_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.__Log.insert_to_log(process_name, process_statu, date, started_time, finish_time, detail)
            print(message)
