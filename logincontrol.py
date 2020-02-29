import mechanize
import time


class LogInCheck:

    def __init__(self):
        self.__browser = mechanize.Browser()
        self.__host = None

    def login_check(self, host):
        self.__host = host
        self.__browser.open(host)
        control = False
        forms = self.__browser.forms()
        for form_num, form in enumerate(forms):
            for control in form.controls:
                if str(control.type) == "text" or str(control.type) == "password":
                    control = True
        if control:
            return True, self.__browser
        else:
            return False

    def login_into_site(self):

        while True:
            username = input("Kullanıcı Adı: ")
            password = input("Parola: ")
            self.__browser.select_form(nr=0)
            self.__browser.form['username'] = username
            self.__browser.form['password'] = password
            response = self.__browser.submit()
            # Eğer aktif olan urlde değişiklik varsa yani bir yönlendirme işlemi
            # gerçekleştirilmiş ise bu durumda başarılı bir şekilde belirtilen siteye girilmiştir.
            if response.geturl() != self.__host:
                self.__host = response.geturl()
                print("Başarılı bir şekilde giriş yaptınız.")
                time.sleep(1)
                print("---- Aktif URL {0} olarak değiştirildi! ----".format(self.__host))
                time.sleep(1)
                return self.__host, self.__browser
            else:
                print("Kullanıcı adı veya parolanız yanlış! Tekrar Deneyiniz...")


if __name__ == "__main__":
    log_in_control = LogInCheck()
    try:
        if log_in_control.login_check("http://192.101.101.101.101.101.101.101/")[0]:
            print("Giriş sayfasıdır!")
    except mechanize.HTTPError:
        print("Girmiş olduğunuz site bulunamadı...")
        # log_in_control.login_into_site()
