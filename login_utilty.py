

def input_check(yes_indicator, no_indicator):
    while True:
        control_input = input()
        if control_input.lower() == yes_indicator:
            return True

        elif control_input.lower() == no_indicator:
            return False
        else:
            print("Lütfen 'e' veya 'h' kullanarak cevap veriniz!")