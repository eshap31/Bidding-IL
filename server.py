import socket
import threading
from protocol import protocol


class bidding_server:
    def __init__(self):
        self.command_list = ['o', 'b', 'p', 'u', 's', 'l']
        self.host = '127.0.0.1'
        self.port = 59000
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create server object
        self.server.bind((self.host, self.port))
        self.server.listen()  # activate listen
        self.clients = []  # list of clients
        self.usernames = []  # list of usernames
        self.sellers = []
        self.sellers_dict = {}
        self.items = []
        self.bids = []  # list that holds tuples, of buyers and their highest bid
        self.highest_bid = 0

    @staticmethod
    def read_file():
        """ reads from file
                    adds each username and password to users dictionary
                    returns the dictionary
                """
        users = {}
        with open("username_password.txt", "r") as file:
            for line in file:
                line = line.strip()
                if line != "":
                    username, password = line.split(",")
                    users[username] = password
        return users

    @staticmethod
    def write_file(username, password):
        with open("username_password.txt", "a") as file:
            file.write(f"{username},{password}\n")

    def buyer(self, username, client):
        """
        1. send the buyer the images (products that are being sold), if there are no images, send error message to the
           client
        """
        if len(self.sellers_dict) == 0:  # if there are no items for sale
            """ wait for response from client, either logout or go back """
            msg = protocol.create_msg('no items for sale')
            client.send(msg)
            client_status = protocol.get_msg(client)
            if client_status[0]:  # if client wants to logout
                if client_status[1] == 'logout':
                    self.logout(client)
                else:  # if client wants to go back
                    self.determine_user(username, client)
        else:
            # send the buyer how many items are up for sale
            count = len(self.items)
            print(f'amount of items: {count}')
            count = protocol.create_msg(count)
            client.send(count)
            index = 0
            while index < len(self.items):
                image_data = protocol.create_image_data(self.items[index], str(len(self.items[index])))
                # send to client
                client.send(image_data)
                index += 1
            chosen_item = protocol.get_msg(client)  # get chosen item index from buyer
            if chosen_item[0]:
                # get index of client in self.sellers list
                chosen_item = int(chosen_item[1])
                print(f'chosen item number: {chosen_item}')
                # add the buyer to the list of buyers for sellers item
                my_seller = self.sellers[chosen_item]
                print(f'my seller: {my_seller}')
                print(f'sellers_dict: {self.sellers_dict}')
                list_1 = self.sellers_dict[self.sellers[chosen_item]]
                print(f'item seller list: {list_1}')
                self.sellers_dict[self.sellers[chosen_item]].append(client)  # add buyer to list
                print(f'updated item list: {self.sellers_dict[self.sellers[chosen_item]]}')
                highest_bid = list_1[0]
                print(f'highest bid is {highest_bid}')
                highest_bid = protocol.create_msg(highest_bid)
                client.send(highest_bid)  # send the new buyer the current highest bid
                print(f'sent: {highest_bid}')
                while self.sellers_dict[self.sellers[chosen_item]][2]:
                    current_bid = protocol.get_msg(client)  # wait to receive a bid from the buyer
                    print('received bid')
                    if current_bid[1].isnumeric():
                        current_bid = current_bid[1]
                        if self.sellers_dict[self.sellers[chosen_item]][0] is None or int(current_bid) > \
                                self.sellers_dict[self.sellers[chosen_item]][
                                    0]:  # if the current bid is greater than the highest bid
                            self.sellers_dict[self.sellers[chosen_item]][0] = int(current_bid)  # update the highest bid
                            self.sellers_dict[self.sellers[chosen_item]][1] = client  # update the highest bidder
                            print(f'updated list: {self.sellers_dict[self.sellers[chosen_item]]}')
                            data = protocol.create_msg(current_bid)  # send to seller, and buyers
                            self.sellers[chosen_item].send(data)  # send to seller
                            i = 3
                            while i < len(self.sellers_dict[self.sellers[chosen_item]]):
                                self.sellers_dict[self.sellers[chosen_item]][i].send(data)  # send to all buyers
                                i += 1
                    elif current_bid[1] == 'logout':
                        break
                    if not self.sellers_dict[self.sellers[chosen_item]][2]:
                        break

                print('out of buyer loop')
                # log user out
                print(f'logging {username} out')
                self.usernames.remove(username)  # remove username from list
                print(f'updated client list: {self.usernames}')
                self.clients.remove(client)
                client.close()

    def seller(self, username, client):
        """
        1. add client to seller_socket list
        2. add username to seller_user list
        3. get the image that the client is selling
        4. add to sale list (will turn into image viewer on the clients side)
        """
        self.sellers.append(client)

        image_type = protocol.get_msg(client)
        image_type = image_type[1]
        print(f'type: {image_type}')

        # receive the image data using the get_image_data function
        image_data = protocol.get_image_data(client)
        image_data = image_data[1]

        # add to dictionary
        self.sellers_dict[client] = []
        self.sellers_dict[client].append(None)  # the first place in the list will be the highest bid
        self.sellers_dict[client].append(None)  # holds the highest bidder
        self.sellers_dict[client].append(True)
        print(f'list: {self.sellers_dict[client]}')
        self.items.append(image_data)  # add image_data to items list
        status = protocol.get_msg(client)  # wait for seller to decide to sell
        if status[0]:
            if status[1] == 'Over, no bids':
                self.sellers_dict[client][2] = False
                # del self.sellers_dict[client]  # delete bid from dictionary
                print('false')
                print(f'ending auction, no bids')
                data = protocol.create_msg('over')
                i = 3
                print(f'there are {len(self.sellers_dict[client]) - 2} buyers')
                while i < len(self.sellers_dict[client]):
                    self.sellers_dict[client][i].send(data)  # tell buyers that the bid is over
                    i += 1
                self.items.remove(image_data)  # remove item from items list
                self.sellers.remove(client)  # remove seller from seller's list
                self.usernames.remove(username)
                self.clients.remove(client)
                client.close()
                print(f'updated client list: {self.usernames}')
            elif status[1] == 'logout':
                # send buyers that the bid is over - seller left
                self.sellers_dict[client][2] = False
                print('false')
                print(f'ending auction, seller left')
                data = protocol.create_msg('over')
                i = 3
                print(f'there are {len(self.sellers_dict[client]) - 2} buyers')
                while i < len(self.sellers_dict[client]):
                    self.sellers_dict[client][i].send(data)  # tell buyers that the bid is over
                    i += 1
                self.items.remove(image_data)  # remove item from items list
                self.sellers.remove(client)  # remove seller from seller's list
                self.usernames.remove(username)
                self.clients.remove(client)
                client.close()
                print(f'updated client list: {self.usernames}')
            else:
                self.sellers_dict[client][2] = False
                winning_bid = self.sellers_dict[client][0]  # save winning bid
                print(f'winning bid: {winning_bid}')
                winning_bidder = self.sellers_dict[client][1]  # save winning bidder
                # send then winning bidder the fact that he won
                data = protocol.create_msg('won')
                self.sellers_dict[client][1].send(data)
                # send the other bidders the fact that they lost, and who they lost to
                i = 3
                data = protocol.create_msg(f'lost,{winning_bid}')
                while i < len(self.sellers_dict[client]):
                    if self.sellers_dict[client][i] != self.sellers_dict[client][1]:
                        self.sellers_dict[client][i].send(data)
                    i += 1
                self.items.remove(image_data)  # remove item from items list
                self.sellers.remove(client)  # remove seller from seller's list
                self.usernames.remove(username)
                self.clients.remove(client)
                client.close()

    def login_func(self, client, username, password):
        """ - check if the username and password exists
            - if all checks out, send True message to client, add client socket and username to list
        """
        users = self.read_file()
        if username in users and users[username] == password and username not in self.usernames:
            print("Login Successful!")
            # send the client a yes message and add to lists
            self.usernames.append(username)
            self.clients.append(client)
            print(f'username: {username} password: {password}')
            print(f'username list: {self.usernames}')
            data = protocol.create_msg('True')
            client.send(data)
            # wait for the user to make the decision - either to join a bid, or to sell an item
            choice = protocol.get_msg(client)
            if choice[0]:  # all checks out
                if choice[1] == 'seller':
                    print(f'{username} is a seller')
                    self.seller(username, client)
                elif choice[1] == 'buyer':
                    print(f'{username} is a buyer')
                    self.buyer(username, client)
                else:
                    self.logout(client)
            else:
                self.logout(client)
        else:
            # send the client an error message
            data = protocol.create_msg('False')
            client.send(data)
            client.close()
            print(f'closing connection')

    def signup_func(self, client, username, password):
        """ - check if the username isn't already taken
            - if all checks out, send True message to client, add client socket and username to list
        """
        users = self.read_file()

        if username in users:
            # send error message
            print('username already taken!')
            data = protocol.create_msg('taken')
            client.send(data)
        elif len(password) > 12 or len(username) > 12:
            print('username or password is too long')
            data = protocol.create_msg('length')
            client.send(data)
        else:
            print('signup successful')
            # send the client a yes message and add to lists
            bidding_server.write_file(username, password)  # add username and password to file
            self.usernames.append(username)
            self.clients.append(client)
            print(f'username: {username} password: {password}')
            print(f'username list: {self.usernames}')
            data = protocol.create_msg('True')
            client.send(data)
            self.determine_user(username, client)

    def determine_user(self, username, client):
        """ check if user wants to be a seller or a user """
        choice = protocol.get_msg(client)
        if choice[0]:  # all checks out
            if choice[1] == 'seller':
                print(f'{username} is a seller')
                self.seller(username, client)
            elif choice[1] == 'buyer':
                print(f'{username} is a buyer')
                self.buyer(username, client)
            else:
                self.logout(client)
        else:
            self.logout(client)

    def handle_client_start(self, client, l_s_status):
        """
        1. differentiate between sign up and login requests
        2. receive username and passwords from client
        3. send parameters to login_func and signup_func according to user needs
        """
        if l_s_status == 's':
            print('in ls status s')
            data = protocol.create_msg('username?')
            client.send(data)
            username = protocol.get_msg(client)
            if username[0]:
                print(f'username: {username[0]}')
                data = protocol.create_msg('password?')
                client.send(data)
                password = protocol.get_msg(client)
                if password[0]:
                    print(f'password: {password}')
                    self.signup_func(client, username[1], password[1])
        elif l_s_status == 'l':
            print('in ls status l')
            data = protocol.create_msg('username?')
            client.send(data)
            username = protocol.get_msg(client)
            if username[0]:
                print(f'username: {username[1]}')
                data = protocol.create_msg('password?')
                client.send(data)
                password = protocol.get_msg(client)
                if password[0]:
                    print(f'password: {password[1]}')
                    self.login_func(client, username[1], password[1])
        else:  # close the client connection
            client.close()

    def logout(self, client):
        """ take client out of client list, take username out of list, and close connection """
        index = self.clients.index(client)
        self.clients.remove(client)
        client.close()
        username = self.usernames[index]
        print(f'removing {username}')
        self.usernames.remove(username)
        print(f'updated user list {self.usernames}')

    def start_loop(self):
        while True:
            print('server is running and listening...')
            client, address = self.server.accept()
            print(f'connection is established with {str(address)}')
            # handle the login/signup
            l_s_status = protocol.get_msg(client)  # gets an s for signup, l for login
            if l_s_status[0]:
                print(f'login sign up status is {l_s_status}')
                thread = threading.Thread(target=self.handle_client_start, args=(client, l_s_status[1],))
                thread.start()
            else:
                client.close()


def main():
    my_server = bidding_server()
    my_server.start_loop()


if __name__ == '__main__':
    main()
