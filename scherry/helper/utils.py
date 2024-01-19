
import io

def crlf_to_lf_1(text : str):
    return text.replace("\r\n", "\n")

def crlf_to_lf_2(file : str):
    with open(file, 'r') as f:
        content = f.read()
        
    with open(file, 'w') as f:
        f.write(crlf_to_lf_1(content))
        
def crlf_to_lf_3(file : io.TextIOWrapper):
    file.seek(0)
    
    content = file.read()
    #
    file.seek(0)
    
    file.write(crlf_to_lf_1(content))
    
    file.truncate()
    
