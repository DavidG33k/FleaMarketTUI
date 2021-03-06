import re
from typing import Callable, Any

import PySimpleGUI as sg
import requests
from valid8 import ValidationError, validate

from flea_market_tui.domain import Username, Password, Email, FleaMarket, Name, Description, Condition, Brand, Price, \
    Category, Item

api_address = 'http://localhost:8000/api/v1/'

class Gui:

    sg.theme('DarkRed')

    __key = None
    __fleamarket = FleaMarket()
    __id_dictionary = []
    __users_list = []

    def progress_bar(self) -> None:
        layout = [[sg.Text('Creating your account...')],
                [sg.ProgressBar(1000, orientation='h', size=(20, 20), key='progbar')],
                [sg.Cancel()]]

        window = sg.Window('Working...', layout)
        for i in range(1000):
            event, values = window.read(timeout=1)
            if event == 'Cancel' or event == sg.WIN_CLOSED:
                break
            window['progbar'].update_bar(i + 1)
        window.close()

    def first_menu(self) -> None:
        layout = [[sg.Image(filename='../resources/logo.png')],
                  [sg.Button('Login as user', size=67)],
                  [sg.Button('Login as admin', size=67)],
                  [sg.Button('Registration', size=67)],
                  [sg.Button('Exit', size=67)]]

        window = sg.Window("FleaMarket", layout)

        while True:
            event, values = window.read()

            if event == 'Login as user':
                window.close()
                self.user_login()
                break
            if event == 'Login as admin':
                window.close()
                self.admin_login()
                break
            if event == 'Registration':
                window.close()
                self.registration()
                break
            if event == 'Exit' or event == sg.WIN_CLOSED:
                break

        window.close()

    def registration(self) -> None:
        global username, password

        layout = [[sg.Text("Sign Up", size =(15, 1), font=40, justification='c')],
                 [sg.Text("Username")],
                 [sg.InputText(key='-username-')],
                 [sg.Text("E-mail")],
                 [sg.InputText(key='-email-')],
                 [sg.Text("Password")],
                 [sg.InputText(key='-password-', password_char='*')],
                 [sg.Button("Submit"), sg.Button("Cancel")]]

        window = sg.Window("FleaMarket", layout)

        while True:
            event,values = window.read()
            if event == 'Cancel' or event == sg.WIN_CLOSED:
                window.close()
                self.first_menu()
                break
            else:
                if event == "Submit":
                    username = self.__build_input(values['-username-'], Username)
                    email = self.__build_input(values['-email-'], Email)
                    password = self.__build_input(values['-password-'], Password)

                    if (type(username) is str or type(password) is str or type(email) is str):
                        err = ''

                        if (type(username) is str):
                            err += 'Username not valid:\n' + username + '\n\n'
                        if (type(password) is str):
                            err += 'Password not valid:\n' + password + '\n\n'
                        if (type(email) is str):
                            err += 'Email not valid:\n' + email

                        sg.Popup(err)
                    else:
                        res = requests.post(url=f'{api_address}auth/registration',
                                            data={'username': username, 'email': email,
                                                  'password1': password, 'password2': password})
                        self.progress_bar()
                        if res.status_code == 400:
                            err = ''
                            if res.json().get('username') is not None:
                                err += 'Username not valid: ' + str(res.json().get('username')) + '\n\n'
                            if res.json().get('email') is not None:
                                err += 'Email not valid: ' + str(res.json().get('email')) + '\n\n'
                            if res.json().get('password1') is not None:
                                err += 'Password not valid: ' + str(res.json().get('password1')) + '\n\n'
                            if res.json().get('non_field_errors') is not None:
                                err += 'Fields not valid: ' + str(res.json().get('non_field_errors'))

                            sg.Popup(err)
                        else:
                            sg.Popup('Registration completed!')
                            window.close()
                            self.user_login()
                            break

        window.close()

    def user_login(self) -> None:
        layout = [[sg.Text("User Sign in", size =(15, 1), font=40, justification='r')],
                [sg.Text("Username")],
                [sg.InputText(key='-username-')],
                [sg.Text("Password")],
                [sg.InputText(key='-password-', password_char='*')],
                [sg.Button('Ok'), sg.Button('Cancel')]]

        window = sg.Window("FleaMarket", layout)

        while True:
            event,values = window.read()
            if event == "Cancel" or event == sg.WIN_CLOSED:
                window.close()
                self.first_menu()
                break
            else:
                if event == "Ok":
                    username = self.__build_input(values['-username-'], Username)
                    password = self.__build_input(values['-password-'], Password)

                    if(type(username) is str or type(password) is str):
                        err=''

                        if(type(username) is str):
                            err += 'Username not valid:\n' + username + '\n\n'
                        if (type(password) is str):
                            err += 'Password not valid:\n' + password

                        sg.Popup(err)
                    else:
                        res = requests.post(url=f'{api_address}auth/login/', data={'username': username, 'password': password})

                        if res.status_code != 200:
                            sg.Popup('User does not exist :( Please retry!')
                            window.close()
                            self.user_login()
                        elif res.status_code == 200:
                            self.__key = res.json()['key']
                            window.close()
                            self.user_home_menu()

    def admin_login(self) -> None:
        layout = [[sg.Text("Admin Sign In", size =(15, 1), font=40, justification='r')],
                [sg.Text("Username")],
                [sg.InputText(key='-username-')],
                [sg.Text("Password")],
                [sg.InputText(key='-password-', password_char='*')],
                [sg.Button('Ok'), sg.Button('Cancel')]]

        window = sg.Window("FleaMarket", layout)

        while True:
            event,values = window.read()
            if event == "Cancel" or event == sg.WIN_CLOSED:
                window.close()
                self.first_menu()
                break
            else:
                if event == "Ok":
                    username = self.__build_input(values['-username-'], Username)
                    password = self.__build_input(values['-password-'], Password)

                    if(type(username) is str or type(password) is str):
                        err=''

                        if(type(username) is str):
                            err += 'Username not valid:\n' + username + '\n\n'
                        if (type(password) is str):
                            err += 'Password not valid:\n' + password

                        sg.Popup(err)
                    else:
                        res = requests.post(url=f'{api_address}auth/login/', data={'username': username, 'password': password})

                        if res.status_code != 200:
                            sg.Popup('User does not exist :( Please retry!')
                            window.close()
                            self.admin_login()

                        self.__key = res.json()['key']
                        window.close()
                        self.admin_home_menu()

    def user_home_menu(self) -> None:

        try:
            self.__fetch()
        except ValueError as e:
            sg.Popup('Error to retrive items!')
        except RuntimeError:
            sg.Popup('Connection failed!')

        data = self.make_table()

        headings = ['   NAME    ', '    DESCRIPTION     ', '    CONDITION   ', '   BRAND  ', '    PRICE   ', '    CATEGORY    ']

        layout = [[sg.Table(values=data[1:][:], headings=headings,
                            alternating_row_color='PaleVioletRed4',
                            max_col_width=100,
                            auto_size_columns=True,
                            display_row_numbers=True,
                            justification='center',
                            num_rows=10,
                            key='-TABLE-',
                            enable_events=True,
                            row_height=45)],
                  [sg.Button('Add', button_color='green4'), sg.Button('Edit', button_color='blue4', key='-edit-', disabled=True), sg.Button('Remove', button_color='red3', key='-remove-', disabled=True), sg.Button('Logout'), sg.Text('Sort by:'), sg.Combo(['price', 'condition', 'brand'], enable_events=True, key='-sortby-')]]

        window = sg.Window("FleaMarket", layout)

        while True:
            event, values = window.read()

            ############################ LOGOUT BUTTON ############################
            if event == sg.WIN_CLOSED or event == 'Logout':
                break

            ############################ ADD BUTTON ############################
            if event == 'Add':
                window['-edit-'].Update(disabled=True)
                window['-remove-'].Update(disabled=True)
                new_item = self.item_form()
                if new_item is not None:
                    self.__fleamarket.add_item(new_item)
                    self.__store(new_item)
                    data = self.make_table()
                    window['-TABLE-'].Update(values=data[1:][:])
                    sg.Popup('Item added successfully!')

            ############################ TABLE EVENT ############################
            if event == '-TABLE-':
                window['-remove-'].Update(disabled=False)
                window['-edit-'].Update(disabled=False)

            ############################ EDIT BUTTON ############################
            if event == '-edit-':
                selected_row = re.sub(r'^\[', '', str(values['-TABLE-']))
                selected_row = re.sub(r'\]$', '', selected_row)
                if (selected_row != ''):
                    self.__edit_item(int(selected_row))
                    data = self.make_table()
                    window['-TABLE-'].Update(values=data[1:][:])

            ############################ REMOVE BUTTON ############################
            if event == '-remove-':
                selected_row = re.sub(r'^\[', '', str(values['-TABLE-']))
                selected_row = re.sub(r'\]$', '', selected_row)
                if(selected_row != ''):
                    if(sg.popup_yes_no('Are you sure to delete the element in row ' + selected_row + ' ?') == 'Yes'):
                        self.__delete(self.__fleamarket.item(int(selected_row)))
                        self.__fleamarket.remove_item(int(selected_row))
                        data = self.make_table()
                        window['-TABLE-'].Update(values=data[1:][:])
                        sg.Popup('Item removed!')

            ############################ SORTBY EVENT ############################
            if event == '-sortby-':
                if values['-sortby-'] == 'price':
                    self.__sort_by_price()
                elif values['-sortby-'] == 'condition':
                    self.__sort_by_condition()
                elif values['-sortby-'] == 'brand':
                    self.__sort_by_brand()
                data = self.make_table()
                window['-TABLE-'].Update(values=data[1:][:])

        window.close()

    def admin_home_menu(self) -> None:

        try:
            self.__fetch_admin()
        except ValueError as e:
            sg.Popup('Error to retrive items!')
        except RuntimeError:
            sg.Popup('Connection failed!')

        data = self.make_table()
        headings = ['   NAME    ', '    DESCRIPTION     ', '    CONDITION   ', '   BRAND  ', '    PRICE   ', '    CATEGORY    ']

        layout = [[sg.Table(values=data[1:][:], headings=headings,
                            alternating_row_color='PaleVioletRed4',
                            max_col_width=100,
                            auto_size_columns=True,
                            display_row_numbers=True,
                            justification='center',
                            num_rows=10,
                            key='-TABLE-',
                            enable_events=True,
                            row_height=45)],
                  [sg.Button('Remove', button_color='red3', key='-remove-', disabled=True), sg.Button('Users list', button_color='blue4'), sg.Button('Logout'), sg.Text('Sort by:'), sg.Combo(['price', 'condition', 'brand'], enable_events=True, key='-sortby-')]]

        window = sg.Window("FleaMarket", layout)

        while True:
            event, values = window.read()

            ############################ LOGOUT BUTTON ############################
            if event == sg.WIN_CLOSED or event == 'Logout':
                break

            ############################ TABLE EVENT ############################
            if event == '-TABLE-':
                window['-remove-'].Update(disabled=False)

            ############################ REMOVE BUTTON ############################
            if event == '-remove-':
                selected_row = re.sub(r'^\[', '', str(values['-TABLE-']))
                selected_row = re.sub(r'\]$', '', selected_row)
                if(selected_row != ''):
                    if(sg.popup_yes_no('Are you sure to delete the element in row ' + selected_row + ' ?') == 'Yes'):
                        self.__superdelete(self.__fleamarket.item(int(selected_row)))
                        self.__fleamarket.remove_item(int(selected_row))
                        data = self.make_table()
                        window['-TABLE-'].Update(values=data[1:][:])
                        sg.Popup('Item removed!')

            ############################ USER LIST BUTTON ############################
            if event == 'Users list':
                self.__show_user_list()

            ############################ SORTBY EVENT ############################
            if event == '-sortby-':
                if values['-sortby-'] == 'price':
                    self.__sort_by_price()
                elif values['-sortby-'] == 'condition':
                    self.__sort_by_condition()
                elif values['-sortby-'] == 'brand':
                    self.__sort_by_brand()
                data = self.make_table()
                window['-TABLE-'].Update(values=data[1:][:])

        window.close()

    def __show_user_list(self) -> None:

        try:
            self.__fetch_users_list()
        except ValueError as e:
            sg.Popup('Error to retrive users!')
        except RuntimeError:
            sg.Popup('Connection failed!')

        data = self.make_users_table()
        headings = ['   ID    ', '    USERNAME     ']

        layout = [[sg.Table(values=data[1:][:], headings=headings,
                            alternating_row_color='PaleVioletRed4',
                            max_col_width=100,
                            auto_size_columns=True,
                            display_row_numbers=True,
                            justification='center',
                            num_rows=10,
                            key='-TABLE-',
                            enable_events=True,
                            row_height=45)],
                  [sg.Button('Close')]]

        window = sg.Window("FleaMarket", layout)

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Close':
                break

        window.close()

    def __edit_item(self, index: int) -> None:
        id_to_edit = self.__find_id(self.__fleamarket.item(index))
        item = self.item_form()
        if item is not None:
            self.__fleamarket.update_item(index, item)
            self.__update(self.__fleamarket.item(index), id_to_edit)
            sg.Popup('Updated successfully!')

    def __update(self, item: Any, id: int) -> None:
            requests.patch(url=f'{api_address}item/edit/' + str(id)+ '/',
                           headers={'Authorization': f'Token {self.__key}'},
                           data={'name': item.name.value, 'description': item.description.value,
                              'condition': item.condition.value, 'brand': item.brand.value,
                              'price': item.price.value_in_cents, 'category': item.category})

    def __find_id(self, item: Item) -> int:
        for i in range(len(self.__id_dictionary)):
            if (item.name.value, item.brand.value) == (self.__id_dictionary[i][1], self.__id_dictionary[i][2]):
                return int(self.__id_dictionary[i][0])

    def make_table(self) -> None:
        data = [[j for j in range(6)] for i in range(self.__fleamarket.items()+1)]

        for i in range(self.__fleamarket.items()):
            item = self.__fleamarket.item(i)
            if(item.condition.value == '0'):
                data[i+1] = [item.name, item.description, 'As new', item.brand, item.price, item.category.value]
            elif (item.condition.value == '1'):
                data[i+1] = [item.name, item.description, 'Good condition', item.brand, item.price, item.category.value]
            elif (item.condition.value == '2'):
                data[i+1] = [item.name, item.description, 'Acceptable condition', item.brand, item.price, item.category.value]

        return data

    def make_users_table(self) -> None:
        data = [[j for j in range(6)] for i in range(len(self.__users_list)+1)]

        for i in range(len(self.__users_list)):
            data[i+1] = [self.__users_list[i][0], self.__users_list[i][1]]

        return data

    def item_form(self) -> Item:
        layout = [[sg.Text("Add new item", size=(15, 1), font=40, justification='r')],
                  [sg.Text("Name")],
                  [sg.InputText(key='-name-')],
                  [sg.Text("Description")],
                  [sg.InputText(key='-description-')],
                  [sg.Text("Condition")],
                  [sg.Combo(['As new', 'Good condition', 'Acceptable condition'], key='-condition-')],
                  [sg.Text("Brand")],
                  [sg.InputText(key='-brand-')],
                  [sg.Text("Price")],
                  [sg.InputText(key='-price-')],
                  [sg.Text("Category")],
                  [sg.InputText(key='-category-')],
                  [sg.Button('Confirm', button_color='green4'), sg.Button('Cancel', button_color='red3')]]

        window = sg.Window('FleaMarket', layout)

        while True:
            event, values = window.read()

            if event == 'Cancel' or event == sg.WIN_CLOSED:
                break
            else:
                if event == "Confirm":
                    name = self.__build_input(values['-name-'], Name)
                    description = self.__build_input(values['-description-'], Description)
                    brand = self.__build_input(values['-brand-'], Brand)
                    price = self.__build_input(values['-price-'], Price.parse)
                    category = self.__build_input(values['-category-'], Category)

                    if values['-condition-'] == 'As new':
                        condition = self.__build_input('0', Condition)
                    elif values['-condition-'] == 'Good condition':
                        condition = self.__build_input('1', Condition)
                    elif values['-condition-'] == 'Acceptable condition':
                        condition = self.__build_input('2', Condition)
                    else:
                        condition = self.__build_input(values['-condition-'], Condition)

                    if (type(name) is str or type(description) is str or type(condition) is str or type(brand) is str or type(price) is str or type(category) is str):
                        err = ''

                        if (type(name) is str):
                            err += 'Username not valid:\n' + name + '\n\n'
                        if (type(description) is str):
                            err += 'Description not valid:\n' + description + '\n\n'
                        if (type(condition) is str):
                            err += 'Condition not valid:\n' + condition + '\n\n'
                        if (type(brand) is str):
                            err += 'Brand not valid:\n' + brand + '\n\n'
                        if (type(price) is str):
                            err += 'Price not valid:\n' + price + '\n\n'
                        if (type(category) is str):
                            err += 'Category not valid:\n' + category

                        sg.Popup(err)
                    else:
                        window.close()
                        return Item(name, description, condition, brand, price, category)

        window.close()

    def __sort_by_price(self) -> None:
        self.__fleamarket.sort_by_price()

    def __sort_by_condition(self) -> None:
        self.__fleamarket.sort_by_condition()

    def __sort_by_brand(self) -> None:
        self.__fleamarket.sort_by_brand()

    def __store(self, new_item: Any) -> None:
        req = requests.post(url=f'{api_address}item/add/',
                            headers={'Authorization': f'Token {self.__key}'},
                            data={'name': new_item.name.value, 'description': new_item.description.value,
                                  'condition': new_item.condition.value, 'brand': new_item.brand.value,
                                  'price': new_item.price.value_in_cents, 'category': new_item.category})

        self.__id_dictionary.append([req.json()['id'], new_item.name.value, new_item.brand.value])

    def __delete(self, item: Any) -> None:
        index = None
        for i in range(len(self.__id_dictionary)):
            if (item.name.value, item.brand.value) == (self.__id_dictionary[i][1], self.__id_dictionary[i][2]):
                requests.delete(url=f'{api_address}item/edit/{self.__id_dictionary[i][0]}',
                                headers={'Authorization': f'Token {self.__key}'})
                index = i
                break

        self.__id_dictionary.pop(index)

    def __superdelete(self, item: Any) -> None:
        index = None
        for i in range(len(self.__id_dictionary)):
            if (item.name.value, item.brand.value) == (self.__id_dictionary[i][1], self.__id_dictionary[i][2]):
                requests.delete(url=f'{api_address}item-moderator/edit/{self.__id_dictionary[i][0]}',
                                headers={'Authorization': f'Token {self.__key}'})
                index = i
                break

        self.__id_dictionary.pop(index)

    def __fetch(self) -> None:
        self.__fleamarket.clear()
        self.__id_dictionary.clear()
        res = requests.get(url=f'{api_address}item/', headers={'Authorization': f'Token {self.__key}'})

        if res.status_code != 200:
            raise RuntimeError()

        items = res.json()

        for item in items:
            validate('row length', item, length=7)

            item_id = int(item['id'])
            name = Name(str(item['name']))
            description = Description(str(item['description']))
            condition = Condition(str(item['condition']))
            brand = Brand(str(item['brand']))
            price = Price.create(int(int(item['price']) / 100), int(item['price']) % 100)
            category = Category(str(item['category']))

            self.__id_dictionary.append([item_id, name.value, brand.value])

            self.__fleamarket.add_item(Item(name, description, condition, brand, price, category))

    def __fetch_admin(self) -> None:
        self.__fleamarket.clear()
        self.__id_dictionary.clear()
        res = requests.get(url=f'{api_address}item-moderator/', headers={'Authorization': f'Token {self.__key}'})

        if res.status_code != 200:
            raise RuntimeError()

        items = res.json()

        for item in items:
            validate('row length', item, length=7)

            item_id = int(item['id'])
            name = Name(str(item['name']))
            description = Description(str(item['description']))
            condition = Condition(str(item['condition']))
            brand = Brand(str(item['brand']))
            price = Price.create(int(int(item['price']) / 100), int(item['price']) % 100)
            category = Category(str(item['category']))

            self.__id_dictionary.append([item_id, name.value, brand.value])

            self.__fleamarket.add_item(Item(name, description, condition, brand, price, category))

    def __fetch_users_list(self) -> None:
        self.__users_list.clear()
        res = requests.get(url=f'{api_address}users/', headers={'Authorization': f'Token {self.__key}'})

        if res.status_code != 200:
            raise RuntimeError()

        items = res.json()

        for item in items:
            validate('row length', item, length=2)

            self.__users_list.append([item['id'], item['username']])

    @staticmethod
    def __build_input(input_string, builder: Callable) -> Any:  # Implemented to erase exceptions in real time.
        try:
            res = builder(input_string.strip())
            return res
        except (TypeError, ValueError, ValidationError) as e:
            return str(e)


#  _____________MAIN_____________
def main(name: str):
    if name == '__main__':
        Gui().first_menu()


main(__name__)