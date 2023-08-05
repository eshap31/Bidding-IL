# Bidding-IL. A Bidding Platform GUI Project

This project is a simple bidding platform GUI application built using Python's Tkinter library for the graphical user interface, along with sockets and the select module for handling network communication.

## Features

- User-friendly GUI interface to facilitate bidding on items.
- Real-time updates on bidding activity through socket communication.
- Allows multiple users to participate and bid simultaneously.

## Requirements

To run this project, you need the following:

- Python 3.x installed on your system.
- Tkinter library (usually comes pre-installed with Python).
- Internet connection for real-time bidding updates.

## How to Run

1. Download the project files, and insert the bg.png file in a new folder called images.
2. Open a terminal or command prompt and navigate to the project directory.
3. Run the `server.py` script to start the bidding server:

   python server.py

4. Next, run the `client.py` script to launch the GUI application:

   python client.py

5. The GUI window will open, and you can start bidding on the items displayed.

## How it Works

1. The server script (`server.py`) initializes the bidding platform and waits for incoming client connections.

2. The client script (`client.py`) establishes a connection with the server and opens the GUI window.

3. The GUI displays the items available for bidding, along with their current highest bid and the name of the highest bidder.

4. When a user places a bid through the GUI, the client sends the bid information to the server via sockets.

5. The server receives the bid, checks if it's higher than the current highest bid, and updates the item's bid information accordingly.

6. The server then broadcasts the updated bid details to all connected clients, allowing them to see the real-time bidding activity.

7. The GUI updates with the latest bid information received from the server, ensuring all clients have a synchronized view of the bidding process.

## Contributions

This project was developed by Eitam Shapsa. Feel free to contribute by submitting bug reports, feature requests, or pull requests on [GitHub]([https://github.com/yourusername/bidding-platform-gui](https://github.com/eshap31/Bidding-IL)).

## License

This project is licensed under the [Creative Commons Zero v1.0 Universal License](LICENSE). You are free to modify and distribute the code as per the terms of the license.

## Contact

If you have any questions or suggestions related to the project, you can reach out to me at [eitam.shapsa@gmail.com](mailto:your.email@example.com). I'd be happy to hear from you!

Happy Bidding!
