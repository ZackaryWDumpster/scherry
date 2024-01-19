

question : str = globals().get("question", "What is your question?")

w = input(question)

print(f"you answered {w}")
