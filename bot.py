from collections import UserDict
from datetime import datetime, timedelta
import pickle

# Базовий клас для всіх полів, що зберігають значення
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для зберігання імені, наслідується від Field
class Name(Field):
    def __init__(self, value):
        self.value = value

# Клас для зберігання телефонного номера, наслідується від Field
class Phone(Field):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        # Перевірка, чи є значення телефонним номером з 10 цифр
        if self.value.isdigit() and len(self.value) == 10:
            return self.value

class Birthday(Field):
    def __init__(self, value):
        self.value = datetime.strptime(value, "%d.%m.%Y")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

# Клас для зберігання запису, що містить ім'я та список телефонів
class Record:
    def __init__(self, name):
        self.name = Name(name)  # Ім'я запису
        self.phones = []  # Список телефонів
        self.birthday = None

    # Додає телефон до запису
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    # Видаляє телефон з запису
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    # Знаходить телефон у записі
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    # Редагує існуючий телефон у записі
    def edit_phone(self, phone, new_phone):
        for p in self.phones:
            if p.value == phone:
                p.value = new_phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    # Повертає рядкове представлення запису
    def __str__(self):
        phones_str = ', '.join(str(phone) for phone in self.phones)
        return f"Name: {self.name} Phones: {phones_str} Birthday: {self.birthday}"
# Клас для зберігання адресної книги, наслідується від UserDict
class AddressBook(UserDict):
    # Додає запис до адресної книги
    def add_record(self, record):
        self.data[record.name.value] = record
    
    # Знаходить запис за ім'ям
    def find(self, name):
        return self.data.get(name, None)
    
    # Видаляє запис за ім'ям
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    # Метод, який повертає список користувачів, яких потрібно привітати по днях на наступному тижні
    def get_upcoming_birthdays(self):
        today = datetime.today()
        upcoming_bds = []
        for record in self.data.values():
            if record.birthday:
                 # Замінюємо рік дня народження на поточний рік
                birthday = datetime.strptime(record.birthday, "%d.%m.%Y") 
                temp_date = birthday.replace(year=today.year)
                delta_days = (temp_date - today).days

                # Перевіряємо, чи день народження у наступні 7 днів
                if -1 <= delta_days <= 6:
                    congratulation_day = temp_date

                    #Перевіряємо вихідні
                    if congratulation_day.weekday() == 5:
                        congratulation_day += timedelta(days=2)
                    elif congratulation_day.weekday() == 6:
                        congratulation_day += timedelta(days=1)
                    
                    # Форматуємо дату привітання у формат DD-MM-YYYY
                    congratulation_day_str = congratulation_day.strftime('%d-%m-%Y')
                    # Додаємо ім'я користувача та дату привітання до списку
                    upcoming_bds.append((str(record.name), congratulation_day_str))
        return upcoming_bds


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return "Invalid value entered. Please check the input data."
        except KeyError as e:
            return "Record not found. Please check the input data."
        except TypeError as e:
            return "Invalid value entered. Please check the input data."
    return wrapper

@input_error
def parse_input(user_input):
    try:
        command, *args = user_input.split()  # Розділяє введення на команду та аргументи
        command = command.strip().lower()  # Очищує команду від пробілів та переводить у нижній регістр
        args = [arg.strip().upper() for arg in args]  # Очищує аргументи від пробілів та переводить у верхній регістр
        return command, *args  # Повертає команду та аргументи
    except ValueError:
        raise ValueError
    except TypeError:
        raise TypeError

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    if not phone.isdigit() or len(phone) != 10:
        raise ValueError
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(name, phone, new_phone, book: AddressBook):
    if not new_phone.isdigit() or len(new_phone) != 10:
        raise ValueError
    record = book.find(name)
    if record is None:
        return "Record not found."
    record.edit_phone(phone, new_phone)
    return "Phone number updated."

@input_error
def find_phone(name, book: AddressBook):
    record = book.find(name)
    if record is None:
        raise KeyError
    return [phone.value for phone in record.phones]

@input_error
def show_all(book: AddressBook):
    data = book.data
    if data is None:
        raise KeyError
    return [str(record) for record in data.values()]

@input_error
def add_birthday(name, birthday, book: AddressBook):
    try:
        # Перевірка формату дати
        datetime.strptime(birthday, "%d.%m.%Y")
    except ValueError:
        raise ValueError
    
    record = book.find(name)
    if record is None:
        raise KeyError
    
    record.birthday = birthday
    return "Birthday added."

@input_error
def show_birthday(name, book: AddressBook):
    record = book.find(name)
    if record is None:
        raise KeyError
    return record.birthday

@input_error
def birthdays(book: AddressBook):
    data = book.data
    if data is None:
        raise KeyError
    upcoming_bds = book.get_upcoming_birthdays()
    if upcoming_bds:
        return upcoming_bds
    return "No birthdays in the next 7 days."

def save_data(book: AddressBook, filename = "addressbook.pkl"):
    with open(filename, "wb") as file:
        print("Saving data to file ", filename)
        pickle.dump(book, file)

def load_data(filename = "addressbook.pkl"):
    try:
        with open(filename, "rb") as file:
            print("Loading data from file ", filename)
            return pickle.load(file)
    except FileNotFoundError:
        print("Creating a new address book.")
        return AddressBook()

def main():
    print("Welcome to the assistant bot!")
    book = load_data()
    while True:
        user_input = input("Enter a command => ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("Greetings! How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(*args, book))

        elif command == "phone":
            print(find_phone(*args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(*args, book))

        elif command == "show-birthday":
            print(show_birthday(*args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()  # Запуск головної функції програми