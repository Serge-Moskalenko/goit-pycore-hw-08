from collections import UserDict
from datetime import datetime, timedelta
import pickle
import json


# def load_data(filename="addressbook.pkl"):
#     try:
#         with open(filename, "rb") as f:
#             return pickle.load(f)
#     except FileNotFoundError:
#         return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

# def save_data(book, filename="addressbook.pkl"):
#     with open(filename, "wb") as f:
#         pickle.dump(book, f)

def save_data(book, filename="addressbook.json"):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump({"contacts":book.to_dict()}, file, ensure_ascii=False, indent=4)

def load_data(filename="addressbook.json"):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return AddressBook.from_dict(data['contacts'])
    except FileNotFoundError:
        return AddressBook()

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value: str):         
        if value.isdigit() and len(value) == 10:
            super().__init__(value)
        else:
            raise ValueError(f"Phone is too short: {value}. Please put in 10 digits")

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name, phones=None, birthday=None):
        self.name = Name(name)
        self.phones = phones if phones else []
        self.birthday = birthday

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones}{birthday}"
    
    def add_phone(self, phone):
        try:
            self.phones.append(Phone(phone))
        except ValueError as e:
            print(e)

    def add_birthday(self, date):
        try:
            self.birthday = Birthday(date)
        except ValueError as e:
            print(e)

    def edit_phone(self, old_phone, new_phone):
        try:
            for phone in self.phones:
                if phone.value == old_phone:
                    phone.value = Phone(new_phone).value
                    break
            else:
                raise ValueError('Phone not found')
        except ValueError as e:
            print(e)

    def delete_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def to_dict(self):
        return {
            "name": self.name.value,
            "phones": [p.value for p in self.phones],
            "birthday": self.birthday.value.strftime("%d.%m.%Y") if self.birthday else None
        }

    @classmethod
    def from_dict(cls, data):
        name = data['name']
        phones = [Phone(phone) for phone in data['phones']]
        birthday = Birthday(data['birthday']) if data['birthday'] else None
        return cls(name, phones, birthday)

class AddressBook(UserDict):
    def __str__(self):
        return '\n'.join(str(contact) for contact in self.data.values())
    
    def add_record(self, contact):
        self.data[contact.name.value] = contact

    def find(self, name):
        return self.data.get(name, None)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        
        for item in self.data.values():
            if item.birthday:
                birthday_this_year = item.birthday.value.replace(year=today.year)
                days_until_birthday = (birthday_this_year - today).days
                
                if 0 <= days_until_birthday <= 7:
                    if birthday_this_year.weekday() == 5:  
                        birthday_this_year += timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:
                        birthday_this_year += timedelta(days=1)

                    upcoming_birthdays.append({
                        "name": item.name.value,
                        "birthday": birthday_this_year
                    })

        return upcoming_birthdays

    def to_dict(self):
        return {name: record.to_dict() for name, record in self.data.items()}

    @classmethod
    def from_dict(cls, data):
        ab = cls()
        for name, record_data in data.items():
            ab.add_record(Record.from_dict(record_data))
        return ab

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, ValueError) as e:
            return str(e)
    return wrapper

@input_error
def add_contact(args, contacts):
    name, phone, *_ = args

    if name in contacts:
        user = input("Do you want to overwrite the contact? (yes/no): ").strip().lower()

        if user == "yes":
            contacts.add_record(Record(name))
            contacts[name].add_phone(phone)
            return "Contact updated"
        elif user == "no":
            return "Contact not added"
        else:
            return "Invalid command."
    else: 
        contact = Record(name)
        contact.add_phone(phone)
        contacts.add_record(contact)
        return "Contact added."

@input_error   
def change_number(args, contacts):
    name, old_phone, new_phone = args
    record = contacts.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone number changed"
    else:
        return f"{name} not found"

@input_error
def print_phone(args, contacts):
    name, *ar = args
    record = contacts.find(name)
    if record:
        return '; '.join(phone.value for phone in record.phones)
    else:
        return f"{name} not found"

@input_error
def add_birthday(args, contacts):
    name, date = args
    record = contacts.find(name)
    if record:
        record.add_birthday(date)
        return f"Birthday added for {name}."
    else:
        return f"{name} not found."

@input_error
def show_birthday(args, contacts):
    name, *ar = args
    record = contacts.find(name)
    if record:
        return str(record.birthday.value) if record.birthday else "Birthday not set."
    else:
        return f"{name} not found."

@input_error
def birthdays(args, contacts):
    upcoming_birthdays = contacts.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next week."
    return "\n".join(f"{contact['name']}: {contact['birthday']}" for contact in upcoming_birthdays)

def main():
    contacts = load_data()
    print("Welcome to the assistant bot!")
    print("Available commands:\nhello\nadd\nall\nchange\nphone\nclose or exit")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(contacts)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "all":
            print(contacts)
        elif command == "change":
            print(change_number(args, contacts))
        elif command == "phone":
            print(print_phone(args, contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        elif command == "birthdays":
            print(birthdays(args, contacts))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"Error: {error}")
