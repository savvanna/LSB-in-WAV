import wave
import struct
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Steganography")
        self.root.geometry("400x650")
        self.root.configure(bg="#ADD8E6")

        self.current_frame = None
        self.create_encode_frame()

        # Настройка стилей для кнопок с закругленными углами
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
        self.button_browse = ttk.Button(self.current_frame, text="Обзор", style="Rounded.TButton", command=self.browse_file)
        self.button_browse.pack(pady=5)

        tk.Label(self.current_frame, text="Введите сообщение:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.entry_msg = tk.Entry(self.current_frame, width=50, font=('Arial', 12))
        self.entry_msg.pack(pady=5)

        self.button_load_file = ttk.Button(self.current_frame, text="Загрузить из файла", style="Rounded.TButton", command=self.load_message_from_file)
        self.button_load_file.pack(pady=5)

        self.label_file_size = tk.Label(self.current_frame, text="Размер файла: 0 байт", font=('Arial', 12), bg="#ADD8E6", fg="black")
        self.label_file_size.pack(pady=5)

        tk.Label(self.current_frame, text="Введите количество LSB:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.entry_lsb = tk.Entry(self.current_frame, font=('Arial', 12))
        self.entry_lsb.pack(pady=5)

        self.button_encode = ttk.Button(self.current_frame, text="Зашифровать", style="Rounded.TButton", command=self.encode_message)
        self.button_encode.pack(pady=10)

        self.switch_button = ttk.Button(self.current_frame, text="Перейти к расшифровке", style="Rounded.TButton", command=self.create_decode_frame)
        self.switch_button.pack(pady=5)

        self.cover_path = ""

    def create_decode_frame(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#ADD8E6")
        self.current_frame.pack(padx=10, pady=(20, 10))  # Отступ сверху

        tk.Label(self.current_frame, text="Выберите аудиофайл:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.button_browse = ttk.Button(self.current_frame, text="Обзор", command=self.browse_file)
        self.button_browse.pack(pady=5)

        tk.Label(self.current_frame, text="Введите размер данных в байтах для расшифровки:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.entry_size = tk.Entry(self.current_frame, font=('Arial', 12))
        self.entry_size.pack(pady=5)

        tk.Label(self.current_frame, text="Введите количество LSB:", font=('Arial', 12), bg="#ADD8E6").pack(pady=5)
        self.entry_lsb = tk.Entry(self.current_frame, font=('Arial', 12))
        self.entry_lsb.pack(pady=5)

        self.button_decode = ttk.Button(self.current_frame, text="Расшифровать", command=self.decode_message)
        self.button_decode.pack(pady=10)

        self.switch_button = ttk.Button(self.current_frame, text="Перейти к шифрованию", command=self.create_encode_frame)
        self.switch_button.pack(pady=5)

        self.cover_path = ""

    def clear_frame(self):
        if self.current_frame is not None:
            self.current_frame.pack_forget()

    def browse_file(self):
        self.cover_path = filedialog.askopenfilename(
            title="Выберите аудиофайл",
            filetypes=(("WAV files", "*.wav"), ("All files", "*.*"))
        )

    def load_message_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите текстовый файл",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                message = file.read()
                self.entry_msg.delete(0, tk.END)  # Очищаем текущее сообщение
                self.entry_msg.insert(0, message)  # Вставляем новое сообщение

                # Вычисляем размер сообщения в байтах
                file_size_bytes = len(message.encode('utf-8'))
                self.label_file_size.config(text=f"Размер файла: {file_size_bytes} байт")

    def encode_message(self):
        if not self.cover_path:
            messagebox.showerror("Ошибка", "Сначала выберите аудиофайл!")
            return
        msg = self.entry_msg.get()
        if not msg:
            messagebox.showerror("Ошибка", "Введите сообщение для шифрования!")
            return
        try:
            nlsb = int(self.entry_lsb.get())
            self.stego(self.cover_path, msg, nlsb)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное значение для LSB!")

    def decode_message(self):
        if not self.cover_path:
            messagebox.showerror("Ошибка", "Сначала выберите аудиофайл!")
            return
        try:
            nlsb = int(self.entry_lsb.get())
            size = int(self.entry_size.get())
            self.extract(self.cover_path, nlsb, size)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные значения!")

    def convertMsgToBin(self, m):
        res = ''
        for i in m:
            x = str(format(ord(i), 'b'))
            x = ('0' * (8 - len(x))) + x
            res += x
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

        samples = frames * channels

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
        return sum(1 for i in rawdata if i != minByte)

    def stego(self, cover_path, msg, nlsb):
        with wave.open(cover_path, "r") as cover:
            self.pre(cover, nlsb)
            rawdata = list(struct.unpack(fmt, cover.readframes(frames)))

            msg_bin = self.convertMsgToBin(msg)
            available = self.count_available_slots(rawdata)
            slot_len = self.frames_continuous(0.2)
            nslots = math.ceil(len(msg_bin) / (slot_len * nlsb))

            skip = (available - (nslots * slot_len)) // (nslots - 1) if nslots > 1 else 0

            cover_ind = 0
            msg_ind = 0
            res = []

            while msg_ind < len(msg_bin) and cover_ind < len(rawdata):
                if rawdata[cover_ind] == minByte:
                    res.append(struct.pack(fmt[-1], rawdata[cover_ind]))
                    cover_ind += 1
                    continue

                curr = ""
                while len(curr) < nlsb:
                    if msg_ind < len(msg_bin):
                        curr += msg_bin[msg_ind]
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

                if (msg_ind // nlsb) % slot_len == 0:
                    for _ in range(skip):
                        while cover_ind < len(rawdata) and rawdata[cover_ind] != minByte:
                            cover_ind += 1

            while cover_ind < len(rawdata):
                res.append(struct.pack(fmt[-1], rawdata[cover_ind]))
                cover_ind += 1

            stego_path = "stego_audio_LSB.wav"
            with wave.open(stego_path, "w") as steg:
                steg.setparams(para)
                steg.writeframes(b"".join(res))

            messagebox.showinfo("Успех", f"Данные успешно зашифрованы в файл {stego_path}")

    def extract(self, stego_path, nlsb, size_in_bytes):
        global frames, samples, fmt, minByte

        with wave.open(stego_path, "r") as stego:
            self.pre(stego, nlsb)

            msg = ""
            stego_index = 0
            rawdata = list(struct.unpack(fmt, stego.readframes(frames)))

            size = size_in_bytes * 8
            msg_index = 0

            available = self.count_available_slots(rawdata)
            slot_len = self.frames_continuous(0.2)
            nslots = math.ceil(size / (slot_len * nlsb))
            skip = (available - (nslots * slot_len)) // (nslots - 1) if nslots > 1 else 0

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

            with open("output.txt", 'w', encoding='utf-8') as file:
                file.write(dec_msg)

            messagebox.showinfo("Успех", "Сообщение успешно расшифровано и записано в output.txt")

    def decimalToBinary(self, n):
        return bin(n).replace("0b", "")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()