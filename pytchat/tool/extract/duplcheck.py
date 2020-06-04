from . import parser


def check_duplicate(chatdata):
    max_range = len(chatdata) - 1
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
            and tbl_id[i] == tbl_id[j]
            and tbl_type[i] == tbl_type[j]
        )
    print("creating table...")
    create_table(chatdata, max_range)
    print("searching duplicate data...")
    return [{"i": {
        "index": i, "id": parser.get_id(chatdata[i]),
        "offsetTime": parser.get_offset(chatdata[i]),
        "type": parser.get_type(chatdata[i])
    },
        "j":{
        "index": j, "id": parser.get_id(chatdata[j]),
        "offsetTime": parser.get_offset(chatdata[j]),
        "type": parser.get_type(chatdata[j])
    }
    }
        for i in range(max_range) for j in range(i + 1, max_range)
        if is_duplicate(i, j)]


def check_duplicate_offset(chatdata):
    max_range = len(chatdata)
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
            and tbl_id[i] == tbl_id[j]
        )

    print("creating table...")
    create_table(chatdata, max_range)
    print("searching duplicate data...")

    return [{
        "index": i, "id": tbl_id[i],
        "offsetTime": tbl_offset[i],
        "type:": tbl_type[i]
    }
        for i in range(max_range - 1)
        if is_duplicate(i, i + 1)]


def remove_duplicate_head(blocks):
    if len(blocks) == 0 or len(blocks) == 1:
        return blocks

    def is_duplicate_head(index):

        if len(blocks[index].chat_data) == 0:
            return True
        elif len(blocks[index + 1].chat_data) == 0:
            return False

        id_0 = parser.get_id(blocks[index].chat_data[0])
        id_1 = parser.get_id(blocks[index + 1].chat_data[0])
        type_0 = parser.get_type(blocks[index].chat_data[0])
        type_1 = parser.get_type(blocks[index + 1].chat_data[0])
        return (
            blocks[index].first == blocks[index + 1].first
            and id_0 == id_1
            and type_0 == type_1
        )
    ret = [blocks[i] for i in range(len(blocks) - 1)
           if (len(blocks[i].chat_data) > 0
               and not is_duplicate_head(i))]
    ret.append(blocks[-1])
    return ret


def remove_duplicate_tail(blocks):
    if len(blocks) == 0 or len(blocks) == 1:
        return blocks

    def is_duplicate_tail(index):
        if len(blocks[index].chat_data) == 0:
            return True
        elif len(blocks[index - 1].chat_data) == 0:
            return False
        id_0 = parser.get_id(blocks[index - 1].chat_data[-1])
        id_1 = parser.get_id(blocks[index].chat_data[-1])
        type_0 = parser.get_type(blocks[index - 1].chat_data[-1])
        type_1 = parser.get_type(blocks[index].chat_data[-1])
        return (
            blocks[index - 1].last == blocks[index].last
            and id_0 == id_1
            and type_0 == type_1
        )

    ret = [blocks[i] for i in range(0, len(blocks))
           if i == 0 or not is_duplicate_tail(i)]
    return ret


def remove_overlap(blocks):
    """
    Fix overlapped blocks after ready_blocks().
    Align the last offset of each block to the first offset
    of next block (equals `end` offset of each block).
    """
    if len(blocks) == 0 or len(blocks) == 1:
        return blocks

    for block in blocks:
        if block.is_last:
            break
        if len(block.chat_data) == 0:
            continue
        block_end = block.end
        if block.last >= block_end:
            for line in reversed(block.chat_data):
                if parser.get_offset(line) < block_end:
                    break
                block.chat_data.pop()
            block.last = parser.get_offset(line)
            block.remaining = 0
            block.done = True
            block.continuation = None
    return blocks


def _dump(blocks):
    print("----------        first         last         end---")
    for i, block in enumerate(blocks):
        print(
            f"block[{i:3}]   {block.first:>10}   {block.last:>10}  {block.end:>10}")
