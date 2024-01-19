
import io

def crlf_to_lf_1(text : bytes):
    # bytes \r\n to bytes \n
    return text.replace(b"\r\n", b"\n")

def crlf_to_lf_2(file : str):
    with open(file, 'rb') as f:
        content = f.read()
        
    with open(file, 'wb') as f:
        f.write(crlf_to_lf_1(content))
        
def crlf_to_lf_3(file : io.TextIOWrapper):
    file.seek(0)
    
    content = file.read()
    #
    file.seek(0)
    
    file.write(crlf_to_lf_1(content))
    
    file.truncate()
    
