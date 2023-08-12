import azure.cognitiveservices.speech as speechsdk
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_fixed
import xml.etree.ElementTree as ET
import tempfile


class AzureTTS:
    def __init__(self, key: str, region: str):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=key, region=region, speech_recognition_language="zh"
        )
        self.speech_config.speech_synthesis_voice_name = "zh-CN-XiaoxiaoNeural"

        # test whether tts works
        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            self.tts("test", Path(f.name))

    @retry(stop=stop_after_attempt(10), wait=wait_fixed(2))
    def tts(self, text: str, filename: Path):
        audio_config = speechsdk.audio.AudioOutputConfig(
            filename=str(filename.absolute())
        )
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config
        )

        try:
            ET.fromstring(text)
            is_valid_xml = True
        except Exception:
            is_valid_xml = False

        if is_valid_xml:
            speech_synthesis_result = speech_synthesizer.speak_ssml_async(text).get()
        else:
            speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if (
            speech_synthesis_result.reason
            == speechsdk.ResultReason.SynthesizingAudioCompleted
        ):
            # print("Speech synthesized for text [{}]".format(text))
            pass
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details

            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    filename.unlink(missing_ok=True)
                    raise Exception(
                        "Azure tts failed: {}".format(
                            cancellation_details.error_details
                        )
                    )

            filename.unlink(missing_ok=True)
            raise Exception("Azure tts failed: {}".format(cancellation_details.reason))
        else:
            filename.unlink(missing_ok=True)
            raise Exception(
                "Azure tts failed: {}".format(speech_synthesis_result.reason)
            )
