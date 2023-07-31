import azure.cognitiveservices.speech as speechsdk
from pathlib import Path
from tenacity import retry, stop_after_attempt


class AzureTTS:
    def __init__(self, key: str, region: str):
        self.speech_config = speechsdk.SpeechConfig(subscription=key, region=region, speech_recognition_language='zh')
        self.speech_config.speech_synthesis_voice_name='zh-CN-YunxiNeural'

    @retry(stop=stop_after_attempt(3))
    def tts(self, text: str, filename: Path):
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(filename.absolute()))
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    raise Exception("Azure tts failed: {}".format(cancellation_details.error_details))
                
            raise Exception("Azure tts failed: {}".format(cancellation_details.reason))
        else:
            raise Exception("Azure tts failed: {}".format(speech_synthesis_result.reason))