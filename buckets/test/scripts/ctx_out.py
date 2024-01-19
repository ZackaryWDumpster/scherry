

seq = globals().get("ctx").currentSeq

print("current sequence is " + str(seq))

assert globals().get("dataOut")["a"] == 1
assert globals().get("dataOut")["b"] == 2