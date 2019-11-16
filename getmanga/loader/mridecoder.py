    
def mri_decoder(data):
    n = len(data) + 7
    header = [82, 73, 70, 70, 255 & n, n >> 8 & 255, n >> 16 & 255, n >> 24 & 255, 87, 69, 66, 80, 86, 80, 56]
    data = list(map(lambda x: x ^ 101, data))
    return bytes(header + data)