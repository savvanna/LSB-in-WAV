import wave
import os
import struct
import math

cover_path = "cover_audio.wav"
stego_path = "stego_audio_LSB.wav"
msg_path = "data.txt"
output_path = "output.txt"
continuous_duration = 0.2

def convertMsgToBin(m):
    res = ''
    for i in m:
        x = str(format(ord(i), 'b'))
        x = ('0' * (8 - len(x))) + x
        res += x
    return res

def decimalToBinary(n):
    return bin(n).replace("0b", "")

def frames_continuous(time):
    global rate
    return int(rate * time)

def pre(cover):
    global para, channels, sample_width, frames, samples, fmt, mask, minByte, rate
    para = cover.getparams()
    channels = cover.getnchannels()
    sample_width = cover.getsampwidth()
    frames = cover.getnframes()
    rate = cover.getframerate()

    if channels == 1:
        fmt = str(frames) + "B"
        minByte = -(1 << 7)
    elif channels == 2:
        fmt = str(frames) + "h"
        minByte = -(1 << 15)
    else:
        raise ValueError("Number of channels is too large")

def count_available_slots(rawdata):
    global minByte
    cnt = 0
    for i in range(len(rawdata)):
        if rawdata[i] != minByte:
            cnt += 1
    return cnt

def stego(cover, msg, nlsb):
    pre(cover)
    rawdata = list(struct.unpack(fmt, cover.readframes(frames)))

    available = count_available_slots(rawdata)
    slot_len = frames_continuous(continuous_duration)
    nslots = math.ceil(len(msg) / (slot_len * nlsb))
    skip = (available - (nslots * slot_len)) // (nslots - 1)

    cover_ind, msg_ind, res, slot_ind = 0, 0, [], 0

    while msg_ind < len(msg) and cover_ind < len(rawdata):
        if rawdata[cover_ind] == minByte:
            res.append(struct.pack(fmt[-1], rawdata[cover_ind]))
            cover_ind += 1
            continue

        curr = ""
        while len(curr) < nlsb:
            if msg_ind < len(msg):
                curr += msg[msg_ind]
            else:
                curr += "0"
            msg_ind += 1
        curr = int(curr)

        sign = 1
        if rawdata[cover_ind] < 0:
            rawdata[cover_ind] *= -1
            sign = -1
        
        to_append = ((rawdata[cover_ind] & mask) | curr) * sign
        res.append(struct.pack(fmt[-1], to_append))
        cover_ind += 1
        slot_ind += 1

        if slot_ind < slot_len:
            continue

        i = 0
        while i < skip and cover_ind < len(rawdata):
            if rawdata[cover_ind] != minByte:
                i += 1
            res.append(struct.pack(fmt[-1], rawdata[cover_ind]))
            cover_ind += 1
        slot_ind = 0

    while cover_ind < len(rawdata):
        res.append(struct.pack(fmt[-1], rawdata[cover_ind]))
        cover_ind += 1
    
    stego_file = wave.open(stego_path, "w")
    stego_file.setparams(para)
    stego_file.writeframes(b"".join(res))
    stego_file.close()

    print("Steganography complete. Data hidden in file", stego_path)

def extract(stego, nlsb, size_in_bytes):
    pre(stego)

    msg = ""
    stego_index = 0
    rawdata = list(struct.unpack(fmt, stego.readframes(frames)))

    size = size_in_bytes * 8
    msg_index = 0

    available = count_available_slots(rawdata)
    slot_len = frames_continuous(continuous_duration)
    nslots = math.ceil(size / (slot_len * nlsb))
    skip = (available - (nslots * slot_len)) // (nslots - 1)

    mask = (1 << nlsb) - 1

    slot_ind = 0
    while msg_index < size:
        if rawdata[stego_index] != minByte:
            curr = decimalToBinary(abs(rawdata[stego_index]) & mask)
            msg += ('0' * (nlsb - len(curr))) + curr
            msg_index += nlsb
        stego_index += 1
        slot_ind += 1
        if slot_ind < slot_len:
            continue
        i = 0
        while i < skip:
            if rawdata[stego_index] != minByte:
                i += 1
            stego_index += 1
        slot_ind = 0

    msg = msg[:size]
    
    val = len(msg) // 8
    chunks, chunk_size = len(msg), len(msg) // val
    new_string = [msg[i:i + chunk_size] for i in range(0, chunks, chunk_size)]
    dec_msg = ''.join(chr(int(i, 2)) for i in new_string)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(dec_msg)
    print("The extracted message is written in", output_path)

if __name__ == "__main__":
    print("Select operation:")
    print("1. Encode message into audio")
    print("2. Decode message from audio")
    
    choice = input("Enter choice (1 or 2): ")

    if choice == '1':
        cover = wave.open(cover_path, "r")
        with open(msg_path, 'r', encoding='utf-8') as file:
            msg = file.read()
        msg = convertMsgToBin(msg)
        nlsb = int(input("Enter number of LSBs to be used: "))
        stego(cover, msg, nlsb)
        cover.close()
    elif choice == '2':
        stego = wave.open(stego_path, "r")
        nlsb = int(input("Enter number of LSBs used: "))
        size = int(input("Enter size of data in bytes: "))
        extract(stego, nlsb, size)
        stego.close()
    else:
        print("Invalid choice.")