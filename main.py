from pygame import *   
import sounddevice as sd
import scipy.io.wavfile as wav
from scipy.io.wavfile import write
import numpy as np
from time import sleep

# === Налаштування ===
fs = 44100     # Частота дискретизації (кількість вимірів за секунду)
chunk = 1024   # Кількість семплів (відліків) за один кадр
width, height = 800, 400  

init()
screen = display.set_mode((width, height))
display.set_caption("Live Audio (Mic)")
clock = time.Clock()

start_rect=Rect(295,80,150,80)
show_rect=Rect(150,50,325,250)
start_record_but=transform.scale(image.load('but1.png'),(200,100))
start_record_but1=transform.scale(image.load('but2.png'),(200,100))
show_record=transform.scale(image.load('bbbb.png'),(150,50))
blited=start_record_but
mixer.music.load('rock-music-feel-2-175866.wav')
mixer.music.set_volume(0.5)
if 'karaoke1.wav':
    sound=mixer.Sound('karaoke1.wav')
    sound.set_volume(10)
    length=sound.get_length()

# Початкові дані — масив нулів (ще немає звуку)
data = [0.0] * chunk
record_buffer=[]
a=1

# === Функція, яку викликає sounddevice, коли приходить нова порція звуку ===
def audio_callback(indata, frames, time_info, status):
    global data
    if status:
        print(status)  # Якщо є помилки або попередження, виводимо їх
    # Перетворюємо отриманий звук у список і масштабуємо під висоту екрану
    data = [sample * (height // 2) for sample in indata[:, 0].tolist()]
    if start:
        record_buffer.extend((indata[:, 0] * 32767).astype('int16').tolist())

# === Запуск потоку з мікрофона ===
stream = sd.InputStream(
    callback=audio_callback,  # Функція для отримання аудіо
    channels=1,               # Один канал (моно)
    samplerate=fs,             # Частота дискретизації
    blocksize=chunk,           # Розмір буфера (chunk)
    dtype='float32'            # Тип даних (числа з плаваючою комою)
)
stream.start()

running = True
start=False
show=False
while running:
    for e in event.get():
        x, y = mouse.get_pos()
        if e.type == QUIT:
            running = False
        if e.type==MOUSEBUTTONDOWN:
            if blited== start_record_but and start_rect.collidepoint(x,y):
                blited=start_record_but1
                start=True
                mixer.music.play()
                show=True
            elif blited==start_record_but1 and start_rect.collidepoint(x,y):
                blited=start_record_but
                start=False
                mixer.music.stop()
                if record_buffer:
                    audio = np.array(record_buffer, dtype=np.int16)  # Перетворюємо у numpy масив
                    write(f'karaoke{a}.wav', fs, audio)
                    print(f"💾 Збережено karaoke{a}.wav")
                    record_buffer.clear()
                    sound = mixer.Sound('karaoke1.wav')
                    sound.set_volume(4)
                    length = sound.get_length()
            elif start==False and show_rect.collidepoint(x,y) and show==True:
                    mixer.music.play()
                    mixer.music.set_volume(0.2)
                    sound.play()
                    sleep(length)
                    mixer.music.stop()
                    show=False

    screen.fill(('#0a151f'))
    screen.blit(blited,(start_rect.x,start_rect.y))
    if start==False and blited==start_record_but and 'karaoke1.wav':
        screen.blit(show_record,(325,250))

    # Готуємо список точок для малювання хвилі

    points = []
    for i, sample in enumerate(data):
        x = int(i * width / chunk)          # Позиція X для точки
        y = int(height / 2 + sample)        # Позиція Y для точки
        points.append((x, y))               # Додаємо точку в список

    # Малюємо лінію по точках, якщо їх більше однієї
    if start == True:
        if len(points) > 1:
            draw.lines(screen, 'darkblue', False, points, 2)

    display.update()
    clock.tick(60)

stream.stop()
quit()

