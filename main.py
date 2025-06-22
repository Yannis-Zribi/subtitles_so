import whisper
import argparse

from deep_translator import GoogleTranslator
from moviepy import *



def extract_autdio(input_file, output_dir):
    # Load the video clip
    video_clip = VideoFileClip(input_file)

    print(video_clip)

    # Extract the audio from the video clip
    audio_clip = video_clip.audio

    # Write the audio to a separate file
    audio_clip.write_audiofile(f"{output_dir}/temp_audio.mp3")

    # Close the video and audio clips
    audio_clip.close()
    video_clip.close()



def transcribe_with_whisper(input_file, max_words):
    # Load the Whisper model (large-v3 in this case)
    model = whisper.load_model("turbo")
    

    # Perform transcription
    result = model.transcribe(
        input_file,
        language="fr",
        word_timestamps=True,
    )
    
    
    # Extract the transcription text and word timestamps
    # transcribed_text = result["text"]
    segments = result["segments"]


    # Splitting segments in smaller segments
    if max_words != 0 :
        final_segments = []
        buffer_text = ""
        start_time = None
        end_time = None

        for segment in segments:
            words = segment["text"].strip().split()

            if start_time is None:
                start_time = segment["start"]

            for word in words:
                buffer_text += word + " "

                if len(buffer_text.strip().split()) >= max_words:
                    end_time = segment["end"]
                    final_segments.append({
                        "start": start_time,
                        "end": end_time,
                        "text": buffer_text.strip()
                    })
                    buffer_text = ""
                    start_time = end_time

        # Ajouter le reste s’il en reste
        if buffer_text:
            final_segments.append({
                "start": start_time,
                "end": segment["end"],
                "text": buffer_text.strip()
            })


    # Si le nombre de mots max n'est pas définit
    else :
        final_segments = segments


    # Controle des segments finaux
    print(final_segments)


    # Renvoi des segments finaux
    return final_segments



# def split_segments(segments, max_words) :

    
    


def create_srt_file_from_segments(segments, output_dir) :
    # Save to an SRT file (as specified in the original parameters)
    srt_file = f"{output_dir}/output.srt"
    with open(srt_file, "w") as f:
        for idx, segment in enumerate(segments):
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"].strip()
            
            # Convert start and end times to SRT time format (HH:MM:SS,MS)
            start_time_srt = f"{int(start_time // 3600):02}:{int((start_time % 3600) // 60):02}:{int(start_time % 60):02},{int((start_time * 1000) % 1000):03}"
            end_time_srt = f"{int(end_time // 3600):02}:{int((end_time % 3600) // 60):02}:{int(end_time % 60):02},{int((end_time * 1000) % 1000):03}"
            
            # Write the segment to the SRT file
            f.write(f"{idx + 1}\n")
            f.write(f"{start_time_srt} --> {end_time_srt}\n")
            f.write(f"{text}\n\n")
    
    print(f"Transcription saved to: {srt_file}")

# Example usage
input_video_file = "./input_video/video.mov"
output_directory = "./output"


segments = transcribe_with_whisper(input_video_file, 7)
create_srt_file_from_segments(segments, output_directory)