from . import parser

def check_duplicate(chatdata):
    max_range = len(chatdata)-1 
    tbl_offset = [None] * max_range
    tbl_id = [None] * max_range
    tbl_type = [None] * max_range

    def create_table(chatdata, max_range):
        for i in range(max_range):
            tbl_offset[i] = parser.get_offset(chatdata[i])
            tbl_id[i] = parser.get_id(chatdata[i]) 
            tbl_type[i] = parser.get_type(chatdata[i])

    def is_duplicate(i, j):
        return ( 
            tbl_offset[i] == tbl_offset[j]
                and
            tbl_id[i] == tbl_id[j]
                and
            tbl_type[i] == tbl_type[j]
        )

    print("creating table...")
    create_table(chatdata,max_range)
    print("searching duplicate data...")

    return [{ "i":{
                "index" : i, "id" : parser.get_id(chatdata[i]),
                "offsetTime" : parser.get_offset(chatdata[i])
                },
            "j":{
                "index" : j, "id" : parser.get_id(chatdata[j]),
                "offsetTime" : parser.get_offset(chatdata[j])
                }
            }
        for i in range(max_range) for j in range(i+1,max_range) 
        if is_duplicate(i,j)]

def duplicate_head(blocks):
    if len(blocks) == 1 : return blocks

    def is_duplicate_head(index):
        id_0 = parser.get_id(blocks[index].chat_data[0])
        id_1 = parser.get_id(blocks[index+1].chat_data[0])
        type_0 = parser.get_type(blocks[index].chat_data[0])
        type_1 = parser.get_type(blocks[index+1].chat_data[0])
        return (
            blocks[index].first == blocks[index+1].first
                and
            id_0 == id_1
                and
            type_0 == type_1
        )

    ret = [blocks[i] for i in range(len(blocks)-1)
        if (len(blocks[i].chat_data)>0 and 
        not is_duplicate_head(i) )]
    ret.append(blocks[-1])
    return ret

def duplicate_tail(blocks):
    if len(blocks) == 1 : return blocks    

    def is_duplicate_tail(index):
        id_0 = parser.get_id(blocks[index-1].chat_data[-1])
        id_1 = parser.get_id(blocks[index].chat_data[-1])
        type_0 = parser.get_type(blocks[index-1].chat_data[-1])
        type_1 = parser.get_type(blocks[index].chat_data[-1])
        return (
            blocks[index-1].last == blocks[index].last
                and
            id_0 == id_1
                and
            type_0 == type_1
        )

    ret = [blocks[i] for i in range(0,len(blocks)-1)
        if i == 0 or not  is_duplicate_tail(i) ]
    ret.append(blocks[-1])
    return ret

def overwrap(blocks):
    if len(blocks) == 1 : return blocks

    ret = []
    a = 0
    b = 1
    jmp = False
    ret.append(blocks[0])
    while a < len(blocks)-2:
        while blocks[a].last > blocks[b].first:
            b+=1
            if b == len(blocks)-1:
                jmp = True    
                break
        if jmp: break
        if b-a == 1:
            a = b
        else:
            a = b-1
        ret.append(blocks[a])
        b = a+1
    ret.append(blocks[-1])
    return ret
