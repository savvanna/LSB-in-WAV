import wave
import struct
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

cover_path = "cover_audio.wav"
stego_path = "stego_audio_LSB.wav"
msg_path = "data.txt"
output_path = "output.txt"
continuous_duration = 0.2

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Steganography")
        self.root.geometry("400x650")
        self.root.configure(bg="#ADD8E6")

        self.current_frame = None
        self.create_encode_frame()

        style = ttk.Style()
        style.configure("Rounded.TButton",
                        padding=10,
                        relief="flat",
                        background="#2196F3",
                        foreground="black",
                        font=('Arial', 12),
                        borderwidth=5)
        style.map("Rounded.TButton",
                  background=[("active", "#1976D2")],
                  foreground=[("active", "black")])

    def create_encode_frame(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#ADD8E6")
        self.current_frame.pack(padx=10, pady=(20, 10))

        tk.Label(self.current_frame, text="Выберите аудиофайл:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.button_browse_cover = ttk.Button(self.current_frame, text="Обзор", command=self.browse_cover_file)
        self.button_browse_cover.pack(pady=5)

        tk.Label(self.current_frame, text="Выберите файл с сообщением:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.button_browse_msg = ttk.Button(self.current_frame, text="Обзор", command=self.browse_msg_file)
        self.button_browse_msg.pack(pady=5)

        tk.Label(self.current_frame, text="Размер сообщения (в байтах):", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.label_file_size = tk.Label(self.current_frame, text="", font=('Arial', 12), bg="#ADD8E6")
        self.label_file_size.pack(pady=5)

        tk.Label(self.current_frame, text="Введите количество LSB:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.entry_lsb = tk.Entry(self.current_frame, font=('Arial', 12))
        self.entry_lsb.pack(pady=5)

        self.button_encode = ttk.Button(self.current_frame, text="Зашифровать", style="Rounded.TButton", command=self.encode_message)
        self.button_encode.pack(pady=10)

        self.switch_button = ttk.Button(self.current_frame, text="Перейти к расшифровке", style="Rounded.TButton", command=self.create_decode_frame)
        self.switch_button.pack(pady=5)

    def create_decode_frame(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#ADD8E6")
        self.current_frame.pack(padx=10, pady=(20, 10))

        tk.Label(self.current_frame, text="Выберите аудиофайл:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.button_browse_stego = ttk.Button(self.current_frame, text="Обзор", command=self.browse_stego_file)
        self.button_browse_stego.pack(pady=5)

        tk.Label(self.current_frame, text="Введите количество LSB:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.entry_lsb = tk.Entry(self.current_frame, font=('Arial', 12))
        self.entry_lsb.pack(pady=5)

        tk.Label(self.current_frame, text="Введите размер данных в байтах:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.entry_size = tk.Entry(self.current_frame, font=('Arial', 12))
        self.entry_size.pack(pady=5)

        self.button_decode = ttk.Button(self.current_frame, text="Расшифровать", style="Rounded.TButton", command=self.decode_message)
        self.button_decode.pack(pady=10)

        self.switch_button = ttk.Button(self.current_frame, text="Перейти к шифрованию", style="Rounded.TButton", command=self.create_encode_frame)
        self.switch_button.pack(pady=5)

    def browse_cover_file(self):
        global cover_path
        cover_path = filedialog.askopenfilename(
            title="Выберите аудиофайл",
            filetypes=(("WAV files", "*.wav"), ("All files", "*.*"))
        )

    def browse_msg_file(self):
        global msg_path
        msg_path = filedialog.askopenfilename(
            title="Выберите текстовый файл",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if msg_path:
            with open(msg_path, 'r', encoding='utf-8') as file:
                message = file.read()
                file_size_bytes = len(message.encode('utf-8'))
                self.label_file_size.config(text=f"{file_size_bytes} байт")

    def browse_stego_file(self):
        global stego_path
        stego_path = filedialog.askopenfilename(
            title="Выберите аудиофайл",
            filetypes=(("WAV files", "*.wav"), ("All files", "*.*"))
        )

    def clear_frame(self):
        if self.current_frame is not None:
            self.current_frame.pack_forget()

    def encode_message(self):
        if not cover_path:
            messagebox.showerror("Ошибка", "Сначала выберите аудиофайл!")
            return
        if not msg_path:
            messagebox.showerror("Ошибка", "Сначала выберите файл с сообщением!")
            return
        try:
            nlsb = int(self.entry_lsb.get())
            with wave.open(cover_path, "r") as cover:
                with open(msg_path, 'r', encoding='utf-8') as file:
                    msg = file.read()
                print("Size of message in bytes: ", len(msg))
                msg = self.convertMsgToBin(msg)
                print("Length of message in bits: ", len(msg))
                self.stego(cover, msg, nlsb)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное значение для LSB!")

    def decode_message(self):
        if not stego_path:
            messagebox.showerror("Ошибка", "Сначала выберите аудиофайл!")
            return
        try:
            nlsb = int(self.entry_lsb.get())
            size = int(self.entry_size.get())
            with wave.open(stego_path, "r") as stego:
                self.extract(stego, nlsb, size)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные значения!")

    def convertMsgToBin(self, m):
        res = ''
        for i in m:
            x = str(format(ord(i), 'b'))
            x = ('0' * (8 - len(x))) + x
            res = res + x
        return res

    def frames_continuous(self, time):
        global rate
        return int(rate * time)

    def pre(self, cover, nlsb):
        global para, channels, sample_width, frames, samples, fmt, mask, minByte, rate

        para = cover.getparams()
        channels = cover.getnchannels()
        sample_width = cover.getsampwidth()
        frames = cover.getnframes()
        rate = cover.getframerate()

        print("\nrate", rate)
        duration = frames / rate
        samples = frames * channels
        print("parameters", para)
        print("Total rawdata size expected:", frames * channels * sample_width)
        print("channels", channels)
        print("sample_width", sample_width)
        print("frames", frames)
        print("samples", samples)

        if channels == 1:
            fmt = str(samples) + "B"
            mask = (1 << 8) - (1 << nlsb)
            minByte = -(1 << 8)
        elif channels == 2:
            fmt = str(samples) + "h"
            mask = (1 << 15) - (1 << nlsb)
            minByte = -(1 << 15)
        else:
            raise ValueError("Number of channels is too large")

    def count_available_slots(self, rawdata):
        global minByte
        cnt = 0
        for i in range(len(rawdata)):
            if rawdata[i] != minByte:
                cnt += 1
        return cnt

    def stego(self, cover, msg, nlsb):
        self.pre(cover, nlsb)
        rawdata = list(struct.unpack(fmt, cover.readframes(frames)))
        print(f"Read {len(rawdata)} bytes from the audio file")

        available = self.count_available_slots(rawdata)
        slot_len = self.frames_continuous(continuous_duration)
        nslots = math.ceil(len(msg) / (slot_len * nlsb))
        print("\nnslots", nslots, "\nslot_len", slot_len, "\navailable", available)
        skip = (available - (nslots * slot_len)) // (nslots - 1)

        print("skip", skip)

        cover_ind = 0
        msg_ind = 0
        res = []

        slot_ind = 0

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
            curr = int(curr, 2)

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

        if msg_ind < len(msg):
            print("\n\nMessage length too long. Terminating process")
            messagebox.showerror("Ошибка", "Сообщение слишком длинное для выбранного аудиофайла!")
            return 0
        while cover_ind < len(rawdata):
            res.append(struct.pack(fmt[-1], rawdata[cover_ind]))
            cover_ind += 1

        with wave.open(stego_path, "w") as steg:
            steg.setparams(para)
            steg.writeframes(b"".join(res))

        print("\n\nSteganography complete. Data hidden in file", stego_path)
        messagebox.showinfo("Успех", f"Данные успешно зашифрованы в файл {stego_path}")
        return 1

    def decimalToBinary(self, n):
        return bin(n).replace("0b", "")

    def extract(self, stego, nlsb, size_in_bytes):
        global frames, samples, fmt, minByte

        self.pre(stego, nlsb)

        msg = ""
        stego_index = 0
        rawdata = list(struct.unpack(fmt, stego.readframes(frames)))

        size = size_in_bytes * 8
        msg_index = 0

        available = self.count_available_slots(rawdata)
        slot_len = self.frames_continuous(continuous_duration)
        nslots = math.ceil(size / (slot_len * nlsb))
        print("\nnslots", nslots, "\nslot_len", slot_len, "\navailable frames", available)
        skip = (available - (nslots * slot_len)) // (nslots - 1)
        print("skip", skip)

        mask = (1 << nlsb) - 1

        slot_ind = 0
        while msg_index < size:
            if rawdata[stego_index] != minByte:
                curr = self.decimalToBinary(abs(rawdata[stego_index]) & mask)
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
        chunks = [msg[i:i + 8] for i in range(0, len(msg), 8)]
        dec_msg = ''.join(chr(int(i, 2)) for i in chunks)

        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(dec_msg)
        print("\nThe extracted message is written in", output_path)
        messagebox.showinfo("Успех", "Сообщение успешно расшифровано и записано в output.txt")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
