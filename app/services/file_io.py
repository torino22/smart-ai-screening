import os
import shutil
from datetime import datetime
import edge_tts
from faster_whisper import WhisperModel
from app.pydantics.schemas import GenericServiceResponse

from app.utils.logger import log_info, log_error

from app.config.settings import (
    MODEL_SIZE,
    DEVICE,
    COMPUTE_TYPE,
    UPLOADS_DIR,
    OUTPUT_AUDIO_DIR,
    AUDIO_VOICE
)

class FileTranscriptService:
    def __init__(self):
        self.upload_folder = UPLOADS_DIR
        self.output_audio_folder = OUTPUT_AUDIO_DIR
        self.model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

    def transcribe_and_save(self, upload_file) -> GenericServiceResponse:
        """
        Save the uploaded file to the server.
        """
        try:
            file_name = upload_file.filename
            file_path = os.path.join(self.upload_folder, file_name)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)

            transcript = self._transcribe(file_path)
            log_info(f"Generated transcript: {transcript} for the file: {file_name}")
            return GenericServiceResponse(
                result=transcript,
                path=str(file_path)
            )

        except Exception as e:
            log_error(f"Transcription failed for file {upload_file.filename}: {str(e)}")
            return GenericServiceResponse(
                success=False,
                error=str(e)
            )


    def _transcribe(self, file_path) -> str:
        """
        Transcribe audio using the Whisper model.
        """
        segments, _ = self.model.transcribe(file_path, beam_size=5)
        transcript = "".join([seg.text for seg in segments])
        return transcript


    async def text_to_audio(self, response_text: str):
        """
        Converts input text to speech using edge-tts and saves it as an MP3 file.
        Returns the file path.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"tts_{timestamp}.mp3"
            file_path = os.path.join(self.output_audio_folder, filename)

            communicate = edge_tts.Communicate(text=response_text, voice=AUDIO_VOICE)
            await communicate.save(file_path)
            log_info(f"Audio generated for the text and saved in the path: {file_path}")
            return GenericServiceResponse(
                   path=str(file_path)
                   )

        except Exception as e:
            log_info(f"Error while generating the audio for this text: {response_text}, error: {str(e)}")
            return GenericServiceResponse(
                   success=False,
                   error=str(e)
                   )

