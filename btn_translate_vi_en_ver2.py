import paho.mqtt.client as mqtt
import sounddevice as sd
from scipy.io.wavfile import write
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.effects import normalize
import RPi.GPIO as GPIO
import time

# Constants
DURATION = 5  # Recording duration in seconds
SAMPLE_RATE = 44100  # Sampling rate in Hz
FOLDER_PATH = "/home/every2345/Microphone/Sound_archive"  # Storage folder path
BUTTON_PIN = 26  # GPIO pin connected to the record button
LANGUAGE_PIN = 23  # GPIO pin connected to the language toggle button

# MQTT Information
mqtt_server = "100.100.108.1"  # ESP32 IP address
mqtt_port = 1883
mqtt_topic = "esp32/test"

# Setup folder
if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)

# Initialize recognizer, MQTT client, and language setting
recognizer = sr.Recognizer()
client = mqtt.Client()

language = 'en-EN'  # Default language

# Connect to MQTT server
client.connect(mqtt_server, mqtt_port, 60)
client.loop_start()

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LANGUAGE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Audio recording function
def record_audio(filename):
    print("Recording...")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=2, dtype='int16')
    sd.wait()  # Wait for recording to complete
    print("Recording finished.")

    # Save audio file as .wav
    file_path = os.path.join(FOLDER_PATH, filename)
    write(file_path, SAMPLE_RATE, audio_data)
    print(f"Audio file saved at: {file_path}")
    return file_path

# Audio preprocessing function
def preprocess_audio(file):
    audio = AudioSegment.from_wav(file).set_channels(1).set_frame_rate(16000)
    audio = normalize(audio)
    processed_file = os.path.join(FOLDER_PATH, "processed_audio.wav")
    audio.export(processed_file, format="wav")
    return processed_file

# Speech-to-text function
def audio_to_text(file):
    with sr.AudioFile(file) as source:
        try:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language=language)
            print(f"Recognized text ({language}): {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print(f"Error with Google Speech Recognition: {e}")
        return None

# Command function to send to ESP32
def send_command(command):
    command_map = {
        "turn on the light": "1", # English command example
        "turn off the light": "0",
        "turn on the fan": "2",
        "turn off the fan": "3",
        "open the door": "4",
        "close the door": "5",
        "turn on bedroom light": "6", #Bedroom
        "turn off bedroom light": "7",
        "turn on bedroom fan": "8",
        "turn off bedroom fan": "9",
        "open bedroom door": "10",
        "close bedroom door": "11",
        "turn on bathroom light": "12", #Bathroom
        "turn off bathroom light": "13",
        "turn on bathroom fan": "14",
        "turn off bathroom fan": "15",
        "close bathroom door": "16",
        "open bathroom door": "17",
        "turn on living room light": "18", #Livingroom
        "turn off living room light": "19",
        "turn on living room fan": "20",
        "turn off living room fan": "21",
        "open living room door": "22",
        "close living room door": "23",
        "turn on lights kitchen": "24",
        "turn off kitchen light": "25", #Kitchen
        "open kitchen door": "26",
        "close kitchen door": "27",
        "open garden door": "28", #Room
        "close garden door": "29",
        "turn on garden light": "30", 
        "turn off garden light": "31",
        "open main door": "32", #Hallway
        "close main door": "33",
        "turn on hallway light": "34",
        "turn off hallway light": "35",
        "turn off all device": "36", #All
        "turn on all device": "37",
        "turn on all the light": "38",
        "turn off all the light": "39",
        "turn on all the fan": "40",
        "turn off all the light": "41",
        "turn off all the fan": "42",
        "close all the door": "43",
        
        "bật đèn": "1",  # Vietnamese command example
        "tắt đèn": "0",
        "bật quạt": "2",
        "tắt quạt": "3",
        "mở cửa": "4",
        "đóng cửa": "5",
        "bật đèn phòng ngủ" : "6", #Phong ngu
        "tắt đèn phòng ngủ": "7",
        "bật quạt phòng ngủ": "8",
        "tắt quạt phòng ngủ": "9",
        "mở cửa phòng ngủ": "10",
        "đóng cửa phòng ngủ": "11",
        "bật đèn phòng tắm": "12", #Phong tam
        "tắt đèn phòng tắm": "13",
        "bật quạt phòng tắm": "14",
        "tắt quạt phòng tắm": "15",
        "đóng cửa phòng tắm": "16",
        "mở cửa phòng tắm": "17",
        "bật đèn phòng khách": "18", #Phong khach
        "tắt đèn phòng khách": "19",
        "bật quạt phòng khách": "20",
        "tắt quạt phòng khách": "21",
        "mở cửa phòng khách": "22",
        "đóng cửa phòng khách": "23",
        "bật đèn phòng bếp": "24", #Phong bep
        "tắt đèn phòng bếp": "25",
        "mở cửa phòng bếp": "26",
        "đóng cửa phòng bếp": "27", 
        "mở cửa sân vườn": "28", #San vuon
        "đóng cửa sân vườn": "29",
        "bật đèn sân vườn": "30",
        "tắt đèn sân vườn": "31",
        "mở cửa chính": "32", #Hanh lang
        "đóng cửa chính": "33",
        "bật đèn hành lang": "34",
        "tắt đèn hành lang": "35",
        "mở tất cả thiết bị": "36", #Lệnh tổng 
        "tắt tất cả thiết bị": "37",
        "bật tất cả đèn": "38",
        "bật tất cả quạt": "39",
        "mở tất cả cửa": "40",
        "tắt tất cả đèn": "41",
        "tắt tất cả quạt": "42",
        "đóng tất cả cửa": "43",
    }
    if command in command_map:
        client.publish(mqtt_topic, command_map[command])
        print(f"Command '{command}' sent as signal '{command_map[command]}' to ESP32.")
    else:
        print("No matching command found for:", command)

# Main loop to wait for button press
try:
    print("Waiting for button press...")
    while True:
        # Check for language toggle button press
        if GPIO.input(LANGUAGE_PIN) == GPIO.LOW:
            language = 'vi-VN' if language == 'en-EN' else 'en-EN'
            print(f"Language switched to {'Vietnamese' if language == 'vi-VN' else 'English'}")
            time.sleep(0.2)  # Debounce delay

        # Check for recording button press
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("Button pressed, starting recording...")

            # Record and process audio
            filename = "recording.wav"
            recorded_audio = record_audio(filename)
            processed_audio_file = preprocess_audio(recorded_audio)
            recognized_text = audio_to_text(processed_audio_file)

            if recognized_text:
                send_command(recognized_text)

            # Cleanup audio files
            os.remove(recorded_audio)
            os.remove(processed_audio_file)
            print("Audio files deleted")
            print("Returning to wait for button press...")

            # Small delay to avoid debounce effect
            time.sleep(0.2)

except KeyboardInterrupt:
    print("Program terminated.")

finally:
    GPIO.cleanup()  # Reset GPIO pins to default state
    client.disconnect()  # Disconnect MQTT client
