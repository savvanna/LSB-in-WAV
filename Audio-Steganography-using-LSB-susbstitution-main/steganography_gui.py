import wave
import struct
import math
import tkinter as tk
from tkinter import filedialog, messagebox

class SteganographyApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Audio Steganography")

        # Элементы интерфейса
        self.label_cover = tk.Label(root, text="Выберите аудиофайл:")
        self.label_cover.pack()

        self.button_browse = tk.Button(root, text="Обзор", command=self.browse_file)
        self.button_browse.pack()

        self.label_msg = tk.Label(root, text="Введите сообщение для шифрования:")
        self.label_msg.pack()

        self.entry_msg = tk.Entry(root, width=50)
        self.entry_msg.pack()

        self.label_lsb = tk.Label(root, text="Введите количество LSB:")
        self.label_lsb.pack()

        self.entry_lsb = tk.Entry(root)
        self.entry_lsb.pack()

        self.button_encode = tk.Button(root, text="Зашифровать", command=self.encode_message)
        self.button_encode.pack()

        self.cover_path = ""

    def browse_file(self):
        self.cover_path = filedialog.askopenfilename(
            title="Выберите аудиофайл",
            filetypes=(("WAV files", "*.wav"), ("All files", "*.*"))
        )

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

        # Получение метаданных
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
            self.pre(cover, nlsb)  # Передаем nlsb в функцию pre
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

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()