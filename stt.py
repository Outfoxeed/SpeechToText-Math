import speech_recognition as sr
import pyttsx3 # Also need pyaudio
import pyautogui
import pyperclip
import sys
import os

running = True
dictionary = {}
last_copied_text:str = ""

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def __create_dictionary() -> dict:
    result = {}
    f = open(resource_path("dictionary.txt"), "r", encoding="utf-8")
    for line in f:
        if line == "\n" or line.startswith("--"):
            continue
        (value, key) = line.rsplit(':', maxsplit=1)
        key = key.removesuffix("\n")
        
        if "{" in key and "}" in key: # Multiple keys are possible for the same value
            key = key[key.index("{")+1:key.index("}")]
            for sub_key in key.split(";"):
                result[sub_key] = value 
        else: # Only one key exists for this value
            result[key] = value
    f.close()
    return result

# Returns true if a function has been correctly handled
def __handle_function(function: str) -> bool:
    global running
    global dictionary
    global last_copied_text
    
    # STOP
    if function == "stop()":
        running = False
        return True
        
    # PRESS KEY
    if function.startswith("key("):
        keys = function.split("(")[-1].removesuffix(")").split(",")
        pyautogui.hotkey(keys)
        print(f"Pressed keys: {keys}")
        return True
    
    # UNDO
    if function == "undo()":
        if last_copied_text != "":
            pyautogui.press("backspace", presses=len(last_copied_text))
            print(f"Removed {len(last_copied_text)} elements.")
        return True
    
    # UPDATE:
    if function == "update()":
        dictionary = __create_dictionary()
        print("Dictionary up-to-date!")
        return True
    return False

def main():
    global dictionary
    global last_copied_text
    
    dictionary = __create_dictionary()
    print(dictionary)

    r = sr.Recognizer()
    
    while True:
        try:
            with sr.Microphone() as mic:
                print("Adjusting for ambient noises..")
                r.adjust_for_ambient_noise(mic, duration=0.2)
                
                print("Listening...")
                audio = r.listen(mic)
                
                print("Interpreting...")
                text: str = r.recognize_google(audio, language="fr-FR")
                text = text.lower()

                print(f"Recognized: {text}")
                
                for (key, value) in dictionary.items():
                    if not running:
                        return
                    
                    if text == key and "(" in value and ")" in value:
                        if __handle_function(value):
                            text = ""
                            break # Stop iteration here if a function has been processed
                    else:
                        while key in text:
                            print(f"Replaced '{key}' by '{value}'")
                            text = text.replace(key, value)
                            
                if text != "":
                    pyperclip.copy(text)
                    pyautogui.hotkey("ctrl", "v")
                    print(f"Typed: {text}")
                last_copied_text = text
                    
                if not running:
                    return
                                
        except sr.UnknownValueError:
            print("Understood nothing")
            r = sr.Recognizer()
        except:
            print("Unexpected error. Continuing process")
        print("\n")
            
if __name__ == "__main__":
    main()
    print("Bye! :D")