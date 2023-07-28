import azure.cognitiveservices.speech as speechsdk
from pathlib import Path

class AzureTTS:
    def __init__(self, key: str, region: str):
        self.speech_config = speechsdk.SpeechConfig(subscription=key, region=region)

    def tts(self, text: str, filename: Path):
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(filename.absolute()))
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
        else:
            raise Exception("Unknown reason: {}".format(speech_synthesis_result.reason))

# def tts():
#     # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
#     speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
#     # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
#     audio_config = speechsdk.audio.AudioOutputConfig(filename='1.wav')

#     # The language of the voice that speaks.
#     speech_config.speech_synthesis_voice_name='en-US-JennyNeural'

#     speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

#     # Get text from the console and synthesize to the default speaker.
#     print("Enter some text that you want to speak >")
#     text = input()

#     speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

#     if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#         print("Speech synthesized for text [{}]".format(text))
#     elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
#         cancellation_details = speech_synthesis_result.cancellation_details
#         print("Speech synthesis canceled: {}".format(cancellation_details.reason))
#         if cancellation_details.reason == speechsdk.CancellationReason.Error:
#             if cancellation_details.error_details:
#                 print("Error details: {}".format(cancellation_details.error_details))
#                 print("Did you set the speech resource key and region values?")