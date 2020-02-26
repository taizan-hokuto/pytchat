import json
from pytchat.processors.jsonfile_archiver import JsonfileArchiver
from unittest.mock import patch, mock_open
from tests.testdata.jsonfile_archiver.chat_component import chat_component

def _open_file(path):
    with open(path,mode ='r',encoding = 'utf-8') as f:
        return f.read()

def test_checkpath(mocker):
    processor = JsonfileArchiver("path")
    mocker.patch('os.path.exists').side_effect = exists_file
    '''Test no duplicate file.'''
    assert processor._checkpath("z:/other.txt") == "z:/other.txt"
    
    '''Test duplicate filename. 
    The case the name first renamed ('test.txt -> test(0).txt')
    is also duplicated.
    '''
    assert processor._checkpath("z:/test.txt") == "z:/test(1).txt"
    
    '''Test no extention file (duplicate).'''
    assert processor._checkpath("z:/test") == "z:/test(0)"


def test_read_write():
    '''Test read and write chatdata'''
    mock = mock_open(read_data = "")
    with patch('builtins.open',mock):
        processor = JsonfileArchiver("path")
        save_path = processor.process([chat_component])
    fh = mock()
    actuals = [args[0] for (args, kwargs) in fh.writelines.call_args_list]
    '''write format is json dump string  with 0x0A'''
    to_be_written = [json.dumps(action, ensure_ascii=False)+'\n' 
        for action in chat_component["chatdata"]]
    for i in range(len(actuals)):
        assert actuals[i] == to_be_written[i]
    assert save_path == {'save_path': 'path', 'total_lines': 7}    


def exists_file(path):
    if path == "z:/test.txt":
        return True
    if path == "z:/test(0).txt":
        return True
    if path == "z:/test":
        return True
