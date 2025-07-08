def encodeInp(message):
    keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    output = ''
    i = 0
    while True:
        char1 = ord(message[i])
        i += 1
        if i < len(message):
            char2 = ord(message[i])
        else:
            char2 = 'nan'

        i += 1
        if i < len(message):
            char3 = ord(message[i])
        else:
            char3 = 'nan'
        i += 1
        enc1 = char1 >> 2
        if char2 != 'nan':
            enc2 = ((char1 & 3) << 4) | (char2 >> 4)
        else:
            enc2 = (char1 & 3) << 4
        if char2 != 'nan' and char3 != 'nan':
            enc3 = ((char2 & 15) << 2) | (char3 >> 6)
        elif char2 != 'nan' and char3 == 'nan':
            enc3 = (char2 & 15) << 2
        else:
            enc3 = 0
        if char3 != 'nan':
            enc4 = char3 & 63
        else:
            enc4 = 0
        if char2 == 'nan':
            enc3 = 64
            enc4 = 64
        elif char3 == 'nan':
            enc4 = 64
        output = output + keyStr[enc1] + keyStr[enc2] + keyStr[enc3] + keyStr[enc4]
        if i >= len(message):
            break
    return output