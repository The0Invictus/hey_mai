from openwakeword.model import Model
from openwakeword.utils import download_models
import queue
import sounddevice as sd
import soundfile as sf
from mlx_audio.tts.utils import load_model
import litert_lm
from mlx_audio.vad import load
from mlx_audio.tts.audio_player import AudioPlayer
import time
import numpy as np
from tools import fetch_url, extract_content_from_url
from pathlib import Path


SAMPLE_RATE = 16000
CHANNELS = 1
audio_queue = queue.Queue()
BASE_DIR = Path(__file__).resolve().parent

hey_mai = BASE_DIR / "models" / "Hey_Mai.onnx"
gemma4_E2B = BASE_DIR / "models" / "gemma-4-E2B-it.litertlm"

wake_word_model = Model(
    wakeword_models=[str(hey_mai)],
    inference_framework = "onnx"
)

download_models()
vad_model = load("mlx-community/silero-vad")
messages = [litert_lm.Message.system("""
Function - you will have a conversation from user from audio, answer only in ENGLISH, that can be then turned to sound, meaning no special characters.
If you do not understand audio or it seems like it was not addressed to you (like background conversation) output "junior tomato".
It is best for you to frequently use web search tools: to get urls and the to extract content from selected urls. ALWAYS use this two tools in combination to get relevant information.
""")]
litert_lm.set_min_log_severity(litert_lm.LogSeverity.ERROR)

def audio_callback(indata, frames, status, time):
    """This function is called for every audio block by sounddevice."""
    audio_queue.put(indata[:, 0].copy())


def detect_wake_word(audio_batch):
    """Your custom function to process each audio array batch."""
    # audio_batch is a NumPy array of shape (BLOCK_SIZE, CHANNELS)
    prediction = wake_word_model.predict(
        audio_batch,
        patience={},
        threshold={
            "Hey_Mai":0.1
        },
        debounce_time=1,
    )
    if prediction["Hey_Mai"] > 0.1:
        return True
    return False

def wait_for_wake_word():
    wake_stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=1280,
        channels=CHANNELS,
        dtype="int16",
        callback=audio_callback,
    )
    with wake_stream:
        print("Listening... Press Ctrl+C to stop.")
        try:
            while True:
                batch = audio_queue.get()
                if detect_wake_word(batch):
                    return
        except KeyboardInterrupt:
            print("\nWaiting for wake word stopped.")

def get_audio_input(initial_wait, end_wait, threshold):
    speech_stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=512,
        channels=CHANNELS,
        dtype="int16",
        callback=audio_callback,
    )

    with speech_stream:
        all_sound = []
        start = time.time()
        to_end_time = time.time()

        print("Recording")

        try:
            while True:
                batch = audio_queue.get()
                all_sound.append(batch)
                probability, state = vad_model.feed(batch, sample_rate=SAMPLE_RATE)
                if probability[0][0] > threshold:
                    to_end_time = time.time()
                if time.time() - to_end_time > initial_wait:
                    return None, True
                if time.time() - start > initial_wait and time.time() - to_end_time > end_wait:
                    print("Finished Recording")
                    return np.concatenate(all_sound, axis=0), False

        except KeyboardInterrupt:
            print("\nAudio input stopped.")

class Mai:

    def __init__(self):
        self.tts_model = tts_model = load_model("mlx-community/Kokoro-82M-bf16")
        self.llm_engine = litert_lm.Engine(
                str(gemma4_E2B),
                audio_backend=litert_lm.Backend.CPU(),
                backend=litert_lm.Backend.GPU(),
                enable_speculative_decoding=True,
                max_num_tokens=32000
        )
        self.audio_player = AudioPlayer(sample_rate=tts_model.sample_rate)
        self.tools = [fetch_url, extract_content_from_url]

    def answer_question(self, audio_path):
        with self.llm_engine.create_conversation(messages=messages, tools=self.tools) as conversation:
            while True:
                audio, end_conversation = get_audio_input(2, 0.7, 0.7)
                if end_conversation:
                    break

                sf.write(audio_path, audio, SAMPLE_RATE)
                answer = conversation.send_message(
                    litert_lm.Contents.of(
                        "If you do not understand audio or it seems like it was not addressed to you (like background conversation) output only 'junior tomato'",
                        litert_lm.Content.AudioFile(absolute_path=audio_path),
                    )
                )
                print(answer["content"][0]["text"])
                if answer["content"][0]["text"] == "junior tomato":
                    break
                for result in self.tts_model.generate(
                    text=answer["content"][0]["text"],
                    voice="af_heart",
                    speed=1.0,
                    lang_code="a",
                ):
                    self.audio_player.queue_audio(result.audio)
                self.audio_player.wait_for_drain()
                self.audio_player.stop()

def main():
    mai = Mai()
    path = "output.wav"
    filename = './greeting.wav'
    data, fs = sf.read(filename, dtype='float32')
    while True:
        wait_for_wake_word()
        sd.play(data, fs)
        time.sleep(0.9)
        mai.answer_question(path)


if __name__ == "__main__":
    main()
