
ops=["+", "-", "*", "/"]
ops_ascii = [str(ord(op)) for op in ops]


def load_op_inputs(input_type, op_ascii):
    test_input = []
    truth_data = []
    with open('test/{}_{}_test_input.txt'.format(input_type, str(ord(op_ascii))), 'r') as fd:
        for line in fd:
            test_input.append(line.strip())
    with open('test/{}_{}_test_truth.txt'.format(input_type, str(ord(op_ascii))), 'r') as fd:
        for line in fd:
            truth_data.append(float(line))
    return test_input, truth_data

def load_inputs(input_type):
    test_input = []
    truth_data = []
    with open('test/{}_test_input.txt'.format(input_type), 'r') as fd:
        for line in fd:
            test_input.append(line.strip())
    with open('test/{}_test_truth.txt'.format(input_type), 'r') as fd:
        for line in fd:
            truth_data.append(float(line))
    return test_input, truth_data