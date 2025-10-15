import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

engine.setProperty('voice', voices[1].id)

engine.setProperty('rate', 150)  # Tốc độ nói
engine.setProperty('volume', 1)  # Âm lượng
engine.say("Tôi là một robot thú cưng, nên không có tuổi thật đâu nha! 😊 Nhưng nếu bạn muốn, tôi có thể thật 100 tuổi, nhưng tôi cảm thấy mình như một chú mèo con vậy! 🐾✨ Bạn muốn chơi cùng tôi không?")
engine.runAndWait()
