from preprocessor import PreProcessor


p = PreProcessor()
example_dutch_text = "Het is erg belangrijk om pythonig te zijn terwijl je pythont met python. Iedere pythoner heeft ten minste een keer slecht gepythont."
words = p.preProcess(example_dutch_text)
print (words)


example_multiple_words = "het het het Het Het is Is is moet moeten zal zullen kroeg kroegen Kroeg Kroegen test Test testen Testen"
words = p.preProcess(example_multiple_words)
print (words)
