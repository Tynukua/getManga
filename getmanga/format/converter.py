class Converter:
    def __init__(self, path_list):
        self.path_list = path_list

    def mri_decoder(self, data):
        n = len(data) + 7
        header = [82, 73, 70, 70, 255 & n, 
            n >> 8 & 255, n >> 16 & 255, 
            n >> 24 & 255, 87, 69, 66, 80, 
            86, 80, 56]
        data = list(map(lambda x: x ^ 101, data))
        return bytes(header + data)