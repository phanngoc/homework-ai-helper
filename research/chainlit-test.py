from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
import speech_recognition as sr
import os
import tempfile
from datetime import datetime
import numpy as np
import wave
import io
from phonemizer import phonemize

import chainlit as cl
from chainlit.types import AskFileResponse, InputAudioChunk, OutputAudioChunk
import uuid


def text_to_phonemes(text, language='en-us'):
    """Convert text to phonemes using Phonemizer"""
    try:
        phonemes = phonemize(text, language=language, backend='espeak', strip=True)
        return phonemes
    except Exception as e:
        print(f"Error converting text to phonemes: {e}")
        return text  # Return original text if phonemization fails

@cl.on_chat_start
async def on_chat_start():
    # Initialize our language model
    model = ChatOpenAI(model="gpt-4o", streaming=True)
    
    # Create prompt for generating practice sentences
    sentence_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an English language tutor. Generate a single, clear English sentence for the user to practice pronunciation. The sentence should be appropriate for language learners."
            ),
            ("human", "Generate a practice sentence for me."),
        ]
    )
    
    # Create prompt for evaluating pronunciation
    evaluation_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an English pronunciation coach. Compare the expected sentence with what the user actually said.
                
                Analyze the phonetic representation (IPA) of both sentences and identify specific sounds the user struggled with.
                Focus on vowel sounds, consonant clusters, and syllable stress that might be challenging.
                
                Provide helpful, encouraging feedback on their pronunciation with specific examples of sounds to improve.
                Rate their pronunciation on a scale of 1-10 and offer 2-3 targeted exercises to improve the problematic sounds."""
            ),
            ("human", "Expected text: {expected_text}\nExpected phonemes: {expected_phonemes}\nUser said: {user_text}\nUser phonemes: {user_phonemes}\nProvide pronunciation feedback."),
        ]
    )

    def sentence_generator_fn():
        sentence_generator = sentence_prompt | model | StrOutputParser()
        return sentence_generator.invoke({})
    
    def evaluation_prompt_fn(expected_text, user_text):
        # Convert both texts to phonemes for comparison
        expected_phonemes = text_to_phonemes(expected_text)
        user_phonemes = text_to_phonemes(user_text)
        print("evaluation_prompt_fn")
        print('expected_phonemes', expected_phonemes)
        print('user_phonemes', user_phonemes)
        pronunciation_evaluator = evaluation_prompt | model | StrOutputParser()
        return pronunciation_evaluator.invoke({
            "expected_text": expected_text, 
            "expected_phonemes": expected_phonemes,
            "user_text": user_text,
            "user_phonemes": user_phonemes
        })
    
    # Store in session
    cl.user_session.set("sentence_generator", sentence_generator_fn)
    cl.user_session.set("pronunciation_evaluator", evaluation_prompt_fn)
    cl.user_session.set("current_sentence", "")
    
    # Generate first practice sentence
    sentence_generator = cl.user_session.get("sentence_generator")
    sentence = await cl.make_async(sentence_generator)()
    cl.user_session.set("current_sentence", sentence)
    
    # Send welcome message with first practice sentence
    await cl.Message(
        content=f"Welcome to your daily English practice! Please read the following sentence aloud:\n\n**{sentence}**\n\nClick the microphone button below to record yourself.",
        actions=[
            cl.Action(name="new_sentence", label="Get New Sentence", payload={"value" : "generate"}),
            cl.Action(name="record_audio", label="🎤 Record Pronunciation", payload={"value": "record"}),
        ]
    ).send()


@cl.action_callback("new_sentence")
async def on_action(action):
    # Generate new practice sentence
    sentence_generator = cl.user_session.get("sentence_generator")
    sentence = await cl.make_async(sentence_generator)()
    cl.user_session.set("current_sentence", sentence)
    
    await cl.Message(
        content=f"Here is a new sentence for you to practice:\n\n**{sentence}**\n\nPlease read it aloud.",
        actions=[
            cl.Action(name="new_sentence", label="Get New Sentence", payload={"value": "generate"}),
            cl.Action(name="record_audio", label="🎤 Record Pronunciation", payload={"value": "record"}),
        ]
    ).send()

@cl.action_callback("record_audio")
async def on_record_action(action):
    # Enable microphone recording
    await cl.Message(content="Please read the sentence aloud...").send()

@cl.on_audio_start
async def on_audio_start():
    cl.user_session.set("silent_duration_ms", 0)
    cl.user_session.set("is_speaking", False)
    cl.user_session.set("audio_chunks", [])
    return True

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    # Real-time processing if needed
    print('on_audio_chunk', chunk.mimeType)
    audio_chunks = cl.user_session.get("audio_chunks")
    
    if audio_chunks is not None:
        audio_chunk = np.frombuffer(chunk.data, dtype=np.int16)
        audio_chunks.append(audio_chunk)


@cl.on_audio_end
async def on_audio_end():
    audio_chunks = cl.user_session.get("audio_chunks")
    print('on_audio_end', len(audio_chunks))
    # Ensure audio_chunks is not empty before processing
    if audio_chunks:
        await process_audio_recording(audio_chunks)
    else:
        await cl.Message(content="No audio recorded. Please try recording again.").send()

async def process_audio_recording(audio_chunks):
    # Get current practice sentence
    expected_text = cl.user_session.get("current_sentence")
    # Create temp directory if it doesn't exist
    temp_dir = "./temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique filename with UUID
    temp_filename = f"{uuid.uuid4()}.wav"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    if audio_chunks := cl.user_session.get("audio_chunks"):
        # Concatenate all chunks
        concatenated = np.concatenate(list(audio_chunks))
        print("Start saving audio")
        # Create WAV file with proper parameters
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wav_file.setframerate(24000)  # sample rate (24kHz PCM)
            wav_file.writeframes(concatenated.tobytes())
        
        cl.user_session.set("audio_chunks", [])
    
    # Convert speech to text
    user_text = ""
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)
            print("text to speech: audio_data", audio_data)
            user_text = recognizer.recognize_google(audio_data)
            print("text to speech: user_text", user_text)
        
                # Generate phonemes for expected and actual text
        expected_phonemes = text_to_phonemes(expected_text)
        user_phonemes = text_to_phonemes(user_text)

        input_audio_el = cl.Audio(path=temp_path, mime="audio/wav")

        # Evaluate pronunciation
        pronunciation_evaluator = cl.user_session.get("pronunciation_evaluator")
        evaluation = await cl.make_async(pronunciation_evaluator)(
            expected_text=expected_text, user_text=user_text
        )
        # Send evaluation feedback with phonetic information
        await cl.Message(
            content=f"""**Your recording:** {user_text}
            
**Expected phonemes:** `{expected_phonemes}`
**Your phonemes:** `{user_phonemes}`

**Evaluation:**
{evaluation}""",
elements=[input_audio_el],
            actions=[
                cl.Action(name="new_sentence", label="Get New Sentence", payload={"value": "generate"}),
                cl.Action(name="record_audio", label="🎤 Try Again", payload={"value": "record"}),
            ]
        ).send()
    except Exception as e:
        await cl.Message(content=f"Error processing audio: {str(e)}. Please try again.").send()


@cl.on_message
async def on_message(message: cl.Message):
    # If user sends a text message, generate a response
    msg = cl.Message(content="To practice pronunciation, please use the buttons to get a sentence and record your speech.")
    await msg.send()