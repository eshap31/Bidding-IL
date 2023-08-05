import os


class protocol:
    LENGTH_FIELD_SIZE = 13

    @staticmethod
    def create_msg(data):
        """
        Create a valid protocol message, with length field
        """
        length = str(len(str(data)))
        zfill_length = length.zfill(protocol.LENGTH_FIELD_SIZE)
        message = zfill_length + str(data)
        return message.encode()

    @staticmethod
    def get_msg(my_client):
        """
        Extract message from protocol, without the length field
        If length field does not include a number, returns False, "Error"
        """
        len_word = my_client.recv(protocol.LENGTH_FIELD_SIZE).decode()
        if len_word.isnumeric():
            message = my_client.recv(int(len_word)).decode()
            if message == 'EXIT':
                return False, 'Error'
            else:
                return True, message
        else:
            return False, "Error"

    @staticmethod
    def get_ending(data):
        """ func gets data, and returns the ending """
        return data[-1]

    @staticmethod
    def get_image_data(client_socket):
        image_size = client_socket.recv(protocol.LENGTH_FIELD_SIZE).decode()
        print(f'size: {image_size}')
        if image_size.isnumeric():
            # Receive the image size
            image_size = int(image_size)
            # Receive the image data
            image_data = client_socket.recv(image_size)
            print(type(image_data))
            if isinstance(image_data, bytes):
                return True, image_data
            else:
                return False, 'Error'
        else:
            return False, "Error"

    @staticmethod
    def create_image_data(data, len):
        print(len)
        zfill_length = len.zfill(protocol.LENGTH_FIELD_SIZE)
        message = zfill_length.encode() + data
        return message
