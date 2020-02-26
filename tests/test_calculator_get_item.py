from pytchat.processors.superchat.calculator import SuperchatCalculator

get_item = SuperchatCalculator()._get_item

dict_test = {
    'root':{
        'node0' : 'value0',
        'node1' : 'value1',
        'node2' : {
            'node2-0' : 'value2-0'
        },
    
        'node3' : [
            {'node3-0' : 'value3-0'},
            {'node3-1' : 
                {'node3-1-0' : 'value3-1-0'}
            }
        ],
        'node4' : [],
        'node5' : [
            [
                {'node5-1-0' : 'value5-1-0'},
                {'node5-1-1' : 'value5-1-1'},
            ],
                {'node5-0' : 'value5-0'},
            
        ]
    }
}

items_test0 = [
    'root',
    'node1'
]


items_test_not_found0 = [
    'root',
    'other_data'
]


items_test_nest = [
    'root',
    'node2',
    'node2-0'
]

items_test_list0 = [
    'root',
    'node3',
    1,
    'node3-1'
]

items_test_list1 = [
    'root',
    'node3',
    1,
    'node3-1',
    'node3-1-0'
]

items_test_list2 = [
    'root',
    'node4',
    None
]

items_test_list3 = [
    'root',
    'node4'
]
items_test_list_nest = [
    'root',
    'node5',
    0,
    1,
    'node5-1-1'
]

items_test_list_nest_not_found1 = [
    'root',
    'node5',
    0,
    1,
    'node5-1-1',
    'nodez'
]

items_test_not_found1 = [
    'root',
    'node3',
    2,
    'node3-1',
    'node3-1-0'
]

items_test_not_found2 = [
    'root',
    'node3',
    2,
    'node3-1',
    'node3-1-0',
    'nodex'
]
def test_get_items_0():
    assert get_item(dict_test, items_test0) == 'value1'

def test_get_items_1():
    assert get_item(dict_test, items_test_not_found0) is None

def test_get_items_2():
    assert get_item(dict_test, items_test_nest) == 'value2-0'

def test_get_items_3():
    assert get_item(dict_test, items_test_list0) ==  {'node3-1-0' : 'value3-1-0'}

def test_get_items_4():
    assert get_item(dict_test, items_test_list1) ==  'value3-1-0'

def test_get_items_5():
    assert get_item(dict_test, items_test_not_found1) ==  None

def test_get_items_6():
    assert get_item(dict_test, items_test_not_found2) ==  None

def test_get_items_7():
    assert get_item(dict_test, items_test_list2) ==  None

def test_get_items_8():
    assert get_item(dict_test, items_test_list_nest) ==  'value5-1-1'

def test_get_items_9():
    assert get_item(dict_test, items_test_list_nest_not_found1) ==  None

def test_get_items_10():
    assert get_item(dict_test, items_test_list3) ==  []
