import os
import select
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
from protocol import protocol
import socket


class Home_Screen:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.home = Tk()  # create a window
        self.home.title('Bidding-IL')  # set the title
        self.home.geometry('400x400')  # set the size
        # Create a Canvas widget
        self.canvas = Canvas(self.home, width=400, height=400)
        self.canvas.pack()
        # Load the background image
        self.bg = PhotoImage(file="images/bg.png")
        # Create the background image on the canvas
        self.bg_canvas = self.canvas.create_image(0, 0, anchor=NW, image=self.bg)

        # Add text to the background
        self.home_screen_text = self.canvas.create_text(208, 60, text="Welcome to Bidding-IL", font=("David", 28),
                                                        fill="Black", anchor=CENTER)
        # add logout button
        self.logout_button = Button(self.canvas, text="Logout", command=self.logout)
        # self.logout_button.place(relx=1, x=-10, y=10, anchor="ne")

        # sign up and login buttons
        self.login_button = Button(self.canvas, text='Login Here', command=self.login_window, padx=10, pady=5,
                                   # define login button
                                   bg="lightgray", highlightbackground="lightgray", highlightcolor="lightgray",
                                   borderwidth=8)
        self.signup_button = Button(self.canvas, text='Sign Up Here', command=self.signup_window, padx=10, pady=5,
                                    # define signup button
                                    bg="lightgray", highlightbackground="lightgray", highlightcolor="lightgray",
                                    borderwidth=8)
        self.login_button.place(relx=0.7, rely=0.4, anchor=CENTER)  # put login button on screen
        self.signup_button.place(relx=0.3, rely=0.4, anchor=CENTER)  # put signup button on screen

        self.username_entry = None
        self.password_entry = None

        self.used_username = None

        self.login = None  # create login window, give a starting value of None
        self.signup = None  # create signup window, give a starting value of None

        self.add_item_button = None
        self.buy_item_button = None
        self.image_label = None
        self.prev_button = None
        self.next_button = None
        self.current_image_index = None
        self.sell_button = None
        self.image = None

        # buyer
        self.bid_entry = None
        self.place_bid_button = None
        self.highest_bid_label = Label()
        self.enter_bid_label = None
        self.not_sold = True
        self.highest_bid = None
        self.check = True

        self.no_items_forsale_label = None

        self.back_button = Button(self.canvas, text='back', command=self.bidding_screen_func)
        # self.back_button.place(relx=0.1, rely=0.1, anchor=CENTER)

        self.f_types = (
            ("Image Files", ("*.png", "*.jpg", "*.jpeg", "*.webp")),
            ("All Files", "*.*")
        )
        self.item_list = []

    def send_bid(self, bid):
        print('send bid here')
        data = protocol.create_msg(bid)
        self.client.send(data)  # send the server the updated bid
        print(f'sent bid of {bid} dollars')

    def item_chosen(self, event):  # client chose an item
        """
        1. change window
        2. send the server what item buyer chose
        3. add bid_entry to the screen for buyer to input bid
        4. add place_bid_button then when clicked will send the server the bid amount
        5. add highest_bid_label to show buyer the highest current bid on the item
        6. get item status from server, to know when item has been sold, or if bid is valid
        7. loop until bid is over
        """
        print(f'chosen image address: {self.item_list[self.current_image_index]}')
        self.canvas.delete(self.home_screen_text)
        self.prev_button.destroy()
        self.next_button.destroy()
        # change item size
        self.image.thumbnail((150, 150))
        image_tk = ImageTk.PhotoImage(self.image)
        self.image_label.configure(image=image_tk)
        self.image_label.image = image_tk  # Keep a reference to the image
        self.image_label.unbind("<Button-1>")
        # send message to server that you joined the bid
        data = protocol.create_msg(self.current_image_index)
        self.client.send(data)  # send the server the image index
        # get highest bid
        data = protocol.get_msg(self.client)
        print(f'highest bid is {data[1]}')
        # create bid entry, label, and button, and highest bid label
        self.bid_entry = Entry(self.canvas)
        self.bid_entry.insert(0, '0')
        self.highest_bid_label = Label(self.canvas, text=f'highest bid: {data[1]}')
        self.highest_bid_label.place(relx=0.4, rely=0.7)
        self.enter_bid_label = Label(self.canvas, text='enter bid:')
        self.place_bid_button = Button(self.canvas, text='Place Bid!',
                                       command=lambda: self.send_bid(self.bid_entry.get()))
        self.enter_bid_label.place(relx=0.3, rely=0.2)
        self.bid_entry.place(relx=0.5, rely=0.2)
        self.place_bid_button.place(relx=0.4, rely=0.3)
        print('before buyer_donet')
        self.logout_button.configure(command=self.real_logout)
        self.logout_button.place(relx=0.9, rely=0.1)
        self.buyer_donet()

    def buyer_logout(self):
        # send server logout msg
        print('buyer logout')
        data = protocol.create_msg('logout')
        self.client.send(data)
        self.client.close()
        self.canvas.delete()
        self.home.destroy()
        main()

    def buyer_donet(self):  # get bids from server
        res = self.client_iter()
        if res is not None:
            if res[0]:  # check status
                checker = res[1].split(',')
                if checker[0] == 'over':
                    print('bidding is over')
                    self.bid_entry.destroy()
                    self.enter_bid_label.destroy()
                    self.place_bid_button.destroy()
                    self.highest_bid_label.destroy()
                    self.image_label.destroy()
                    self.canvas.delete(self.bg_canvas)
                    self.logout_button.configure(command=self.buyer_logout)
                    self.logout_button.place(relx=0.9, rely=0.1, anchor="ne")
                    self.home_screen_text = self.canvas.create_text(198, 75, text='Auction is over.\r\nplease log out.',
                                                                    font=('David', 15), fill='Red', anchor=CENTER)
                    return
                elif checker[0] == 'won':
                    print('bidding is over, you won!')
                    self.bid_entry.destroy()
                    self.enter_bid_label.destroy()
                    self.place_bid_button.destroy()
                    self.highest_bid_label.destroy()
                    self.image_label.destroy()
                    self.canvas.delete(self.bg_canvas)
                    self.logout_button.configure(command=self.buyer_logout)
                    self.logout_button.place(relx=0.9, rely=0.1, anchor="ne")
                    self.home_screen_text = self.canvas.create_text(198, 75,
                                                                    text='Auction is over, you won.\r\nplease log out.'
                                                                    , font=('David', 15), fill='Blue', anchor=CENTER)
                    return
                elif checker[0] == 'lost':
                    print('lost auction')
                    self.bid_entry.destroy()
                    self.enter_bid_label.destroy()
                    self.place_bid_button.destroy()
                    self.highest_bid_label.destroy()
                    self.image_label.destroy()
                    self.canvas.delete(self.bg_canvas)
                    self.logout_button.configure(command=self.buyer_logout)
                    self.logout_button.place(relx=0.9, rely=0.1, anchor="ne")
                    self.home_screen_text = self.canvas.create_text(208, 75,
                                                                    text=f'Auction is over, you lost.\r\nwinning bid was '
                                                                         f'{checker[1]} dollars.\r\nplease log out.'
                                                                    , font=('David', 15), fill='Red', anchor=CENTER)
                    return
                else:
                    print(f'highest bid is {res[1]}')
                    self.highest_bid_label.configure(text=f'highest bid is {res[1]}')
        self.canvas.after(20, self.buyer_donet)

    def buyer_func(self, username):
        print('buyer')
        buyer_msg = protocol.create_msg('buyer')  # let server know that client wants to buy
        self.client.send(buyer_msg)
        self.canvas.delete(self.home_screen_text)
        # clear screen
        self.add_item_button.destroy()
        self.buy_item_button.destroy()
        # get amount of images
        count = protocol.get_msg(self.client)
        if count[0]:
            if count[1] == 'no items for sale':
                """ give user the option to go back """
                print('no items for sale')
                # put no items for sale label on screen
                self.no_items_forsale_label = Label(self.canvas,
                                                    text='no items for sale\r\nplease log out\r\nor go back.', fg='red',
                                                    font=('david', 15))
                self.no_items_forsale_label.place(relx=0.3, rely=0.3)
                self.back_button.configure(command=lambda: self.buyer_to_server(username))
                self.back_button.place(relx=0.1, rely=0.1, anchor=CENTER)
                # tell user to click on logout
            else:
                self.home_screen_text = self.canvas.create_text(208, 60, text="Choose an item", font=("David", 20),
                                                                fill="Black", anchor=CENTER)
                i = 1
                print(f'there are {count[1]} items to choose from')
                while i <= int(count[1]):  # add all images to list
                    image_data = protocol.get_image_data(self.client)
                    if image_data[0]:
                        image_data = image_data[1]
                        # Save the received image
                        image_address = f'received_image_{i}.png'
                        with open(image_address, "wb") as file:
                            file.write(image_data)  # save image localy
                        self.item_list.append(image_address)  # add image address to items list
                        print("Image received and saved.")
                        print(f'item addresses: {image_address}')
                        i += 1
                    else:
                        print('invalid')
                        continue
                # add to image viewer
                # Create a label to display the images
                self.image_label = Label(self.canvas)
                self.image_label.place(x=0, y=0, relwidth=1, relheight=1)  # Place the label to fill the window

                self.current_image_index = 0

                # Load and display the first image in the list
                self.image = Image.open(self.item_list[self.current_image_index])
                self.image.thumbnail((250, 250))  # Resize the image if needed
                image_tk = ImageTk.PhotoImage(self.image)
                self.image_label.configure(image=image_tk)
                self.image_label.image = image_tk  # Keep a reference to the image

                # Bind the click event to the image label
                self.image_label.bind("<Button-1>", self.item_chosen)

                # Create buttons to navigate through the images
                self.prev_button = Button(self.canvas, text="Previous", command=self.show_previous_image)
                self.prev_button.place(x=10, rely=.98, anchor=SW)

                self.next_button = Button(self.canvas, text="Next", command=self.show_next_image)
                self.next_button.place(x=360, rely=.98, anchor=SE)

                self.logout_button.place(relx=0.9, rely=0.1, anchor=NE)

                if len(self.item_list) == 1:
                    self.next_button.configure(state=DISABLED)
                    self.prev_button.configure(state=DISABLED)

    def buyer_to_server(self, username):
        self.no_items_forsale_label.place_forget()
        self.back_button.place_forget()
        data = protocol.create_msg('back')
        self.client.send(data)
        self.bidding_screen_func(username)

    def show_previous_image(self):  # buyer function
        self.current_image_index = (self.current_image_index - 1) % len(self.item_list)
        self.image = Image.open(self.item_list[self.current_image_index])
        self.image.thumbnail((250, 250))
        image_tk = ImageTk.PhotoImage(self.image)
        self.image_label.configure(image=image_tk)
        self.image_label.image = image_tk  # Keep a reference to the image

    def show_next_image(self):  # buyer function
        self.current_image_index = (self.current_image_index + 1) % len(self.item_list)
        self.image = Image.open(self.item_list[self.current_image_index])
        self.image.thumbnail((250, 250))
        image_tk = ImageTk.PhotoImage(self.image)
        self.image_label.configure(image=image_tk)
        self.image_label.image = image_tk  # Keep a reference to the image

    def seller_func(self, username):
        print(f'seller')
        seller_msg = protocol.create_msg('seller')  # let server know that client wants to sell
        self.client.send(seller_msg)
        # Open file explorer
        filename = filedialog.askopenfilename(initialdir="c:/users/eitam/downloads", title="Select an Image",
                                              filetypes=self.f_types)
        # Check if a file was selected
        if filename:
            # Print the address of the selected image
            print("Selected image:", filename)
            self.add_item_button.destroy()
            self.buy_item_button.destroy()
            self.canvas.delete(self.home_screen_text)
            # send image data to server
            with open(filename, "rb") as file:  # read data
                image_data = file.read()
            image_type = os.path.splitext(filename)[1][1:]
            image_type = protocol.create_msg(image_type)
            self.client.send(image_type)  # send the server the image type

            # Send the image data to the server
            image_size = len(image_data)
            image_data = protocol.create_image_data(image_data, str(image_size))  # create image packet
            self.client.send(image_data)
            print(f'sent {filename}')

            # loop until false - client gets offers, and chooses when to end bidding
            self.logout_button.configure(command=self.real_logout)
            self.sell_button = Button(self.canvas, text='sell item',
                                      command=self.sell_func)  # add command that goes to end function
            self.sell_button.place(relx=0.7, rely=0.4, anchor=CENTER)
            self.highest_bid_label = Label(self.canvas, text=f'highest bid is {0}')
            self.highest_bid_label.place(relx=0.3, rely=0.4, anchor=CENTER)
            self.seller_donet()

    def seller_donet(self):
        res = self.client_iter()
        if not self.not_sold:  # if item is sold
            return
        if res is not None:
            if res[0]:
                print(f'highest bid: {res[1]}')
                self.highest_bid = res[1]
                self.highest_bid_label.configure(text=f'highest bid is: {res[1]}')
                print('updated highest bid')
        self.canvas.after(20, self.seller_donet)

    def client_iter(self):
        rlist, _, _ = select.select([self.client], [], [], .02)
        if self.client in rlist:
            print('inside, reading from server...')
            res = protocol.get_msg(self.client)
            return res
        return None

    def sell_func(self):  # when the seller clicks on the "sell" button
        self.not_sold = False
        if self.highest_bid is None:
            print('no offer, ending auction...')
            self.highest_bid_label.destroy()
            self.sell_button.destroy()
            self.canvas.delete(self.bg_canvas)
            self.canvas.delete(self.home_screen_text)
            self.home_screen_text = self.canvas.create_text(208, 60, text='No bids, please log out.',
                                                            font=('David', 15), fill='Red', anchor=CENTER)
            data = protocol.create_msg('Over, no bids')
            self.client.send(data)  # send status to the server
            self.logout_button.configure(command=self.seller_logout)
            self.logout_button.place(relx=0.9, rely=0.1, anchor="ne")
        else:
            print(f'highest bid is {self.highest_bid}')
            """
            1. send server the highest bid
            2. display to screen: user bought the item for bid amount 
            3. tell seller to logout
            """
            # tell server that the bid is over
            data = protocol.create_msg('Over, there is a winner')
            self.client.send(data)  # send to server
            # remove widgets from screen
            self.highest_bid_label.destroy()
            self.sell_button.destroy()
            self.canvas.delete(self.bg_canvas)
            self.canvas.delete(self.home_screen_text)
            # add message to the screen
            self.home_screen_text = self.canvas.create_text(208, 60,
                                                            text=f'winning bid: {self.highest_bid}\r\nplease log out.',
                                                            font=('David', 15), fill='Red', anchor=CENTER)
            # add logout button to the screen
            self.logout_button.configure(command=self.seller_logout)
            self.logout_button.place(relx=0.9, rely=0.1, anchor="ne")

    def seller_logout(self):
        self.canvas.delete()
        self.home.destroy()
        self.client.close()
        main()

    def real_logout(self):
        """ if clicked logout during bidding_screen_function, send server the logout message """
        self.not_sold = False
        data = protocol.create_msg('logout')
        self.client.send(data)
        self.logout()

    def bidding_screen_func(self, username):
        """ open bidding screen window as home screen """
        print('bidding screen func')
        self.logout_button.place(relx=0.9, rely=0.1, anchor=CENTER)
        self.logout_button.configure(command=self.real_logout)
        self.home.title(username)
        self.canvas.delete(self.home_screen_text)
        self.home_screen_text = self.canvas.create_text(208, 60, text="Choose an option", font=('David', 28),
                                                        fill='Black',
                                                        anchor=CENTER)  # change text
        # add dropwdown menu, and add an option to upload an item
        self.add_item_button = Button(self.canvas, text='Put item up for auction', padx=10, pady=5, bg="lightgray",
                                      highlightbackground="lightgray", highlightcolor="lightgray", borderwidth=6,
                                      command=lambda: self.seller_func(username))

        self.buy_item_button = Button(self.canvas, text='Buy an item', padx=10, pady=5, bg='lightgray',
                                      highlightbackground='lightgray', highlightcolor='lightgray', borderwidth=6,
                                      command=lambda: self.buyer_func(username))

        self.buy_item_button.place(relx=.3, rely=.4, anchor=CENTER)
        self.add_item_button.place(relx=0.7, rely=0.4, anchor=CENTER)
        """ 
        1. get list of images from the server as bytes
            - decode them and save them as images in the images folder - in order to add to image viewer
        2. create an image viewer with a button for the client to choose a product
        4. when client clicks on image, the screen of the auction will pop up
        """

    def login_func(self, username, password):
        """ send username and password to server using protocol """
        login_data = protocol.create_msg('l')  # notifies the server that user wants to log in
        self.client.connect(('127.0.0.1', 59000))  # connect to server ip
        print('connected: status = login')
        self.client.send(login_data)
        print('sent login data')
        login_status = protocol.get_msg(self.client)
        if login_status[0]:
            if login_status[1] == 'username?':  # make a loop of the following until the user input is valid
                username_data = protocol.create_msg(username)
                self.client.send(username_data)
                login_status = protocol.get_msg(self.client)
                if login_status[0]:
                    if login_status[1] == 'password?':
                        print('password?')
                        password_data = protocol.create_msg(password)
                        self.client.send(password_data)
                        user_input_status = protocol.get_msg(self.client)
                        if user_input_status[1] == 'True':
                            self.login.destroy()
                            self.login_button.destroy()
                            self.signup_button.destroy()
                            self.bidding_screen_func(username)
                        elif user_input_status[1] == 'False':
                            login_error = Label(self.login, text='Invalid username or password, try again', fg='red')
                            login_error.grid(row=4, columnspan=30)  # Adjust the row and column values
                            self.client.close()
                            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def signup_func(self, username, password):
        """ send username and password to server using protocol """
        signup_data = protocol.create_msg('s')  # notifies server that user wants to sign in
        self.client.connect(('127.0.0.1', 59000))  # connect to server ip
        print('connected: satus = signup')
        self.client.send(signup_data)
        print('sent signup data')
        signup_status = protocol.get_msg(self.client)
        if signup_status[0]:
            if signup_status[1] == 'username?':  # make a loop of the following until the user input is valid
                username_data = protocol.create_msg(username)
                self.client.send(username_data)
                login_status = protocol.get_msg(self.client)
                if login_status[0]:
                    if login_status[1] == 'password?':
                        print('password?')
                        password_data = protocol.create_msg(password)
                        self.client.send(password_data)
                        user_input_status = protocol.get_msg(self.client)  # if everything works it will be true
                        if user_input_status[1] == 'True':
                            self.signup.destroy()
                            self.login_button.destroy()
                            self.signup_button.destroy()
                            self.bidding_screen_func(username)
                        elif user_input_status[1] == 'taken':
                            print('username already taken!')
                            signup_error = Label(self.signup, text='Username already taken!', fg='red')
                            signup_error.grid(row=4, columnspan=30)  # Set column span to 2
                            self.client.close()
                            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        else:
                            print('username or password is too long')
                            length_error = Label(self.signup, text='username or password is too long', fg='red')
                            length_error.grid(row=4, columnspan=30)  # Set column span to 2
                            self.client.close()
                            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def login_window(self):
        self.login = Toplevel()
        self.login.title('Login')
        self.login.geometry('230x200')
        """ username and password entries """
        self.username_entry = Entry(self.login, width=25)
        self.username_entry.insert(0, 'username')
        self.password_entry = Entry(self.login, width=25)
        self.password_entry.insert(0, 'password')
        self.username_entry.grid(row=0, column=0, padx=10, pady=10)
        self.password_entry.grid(row=1, column=0, padx=10, pady=10)
        """ login button """
        button_1 = Button(self.login, text='Login', command=lambda: self.login_func(self.username_entry.get(),
                                                                                    self.password_entry.get()))  # command
        # will be to send to server
        button_1.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def signup_window(self):
        self.signup = Toplevel()
        self.signup.title('Sign Up')
        self.signup.geometry('230x200')
        """ username and password entries """
        username_entry = Entry(self.signup, width=25)
        username_entry.insert(0, 'username (max 12 chars)')
        password_entry = Entry(self.signup, width=25)
        password_entry.insert(0, 'password (max 12 chars)')
        username_entry.grid(row=0, column=0, padx=10, pady=10)
        password_entry.grid(row=1, column=0, padx=10, pady=10)
        """ login button """
        button_1 = Button(self.signup, text='Sign Up', command=lambda: self.signup_func(username_entry.get(),
                                                                                        password_entry.get()))  #
        # command will be to send to server
        button_1.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def logout(self):
        """
        1. send logout message to server
        2. loop back to the home screen, to allow user to log back in
        """
        print('logging out...')
        data = protocol.create_msg('EXIT')
        self.client.send(data)
        self.home.destroy()
        self.client.close()
        main()

    def main_func(self):
        self.home.mainloop()


def main():
    print('main')
    my_client = Home_Screen()
    my_client.main_func()


if __name__ == '__main__':
    main()
