#! /usr/bin/env python

### tf-nightly==2.5.0-dev20210104
### https://google.github.io/flatbuffers/flatbuffers_guide_tutorial.html

"""
Command Sample:

$ python3 tflite2tensorflow.py \
  --model_path magenta_arbitrary-image-stylization-v1-256_fp16_transfer_1.tflite \
  --flatc_path ./flatc \
  --schema_path schema.fbs \
  --input_node_names content_image:0,mobilenet_conv/Conv/BiasAdd:0 \
  --output_node_names transformer/expand/conv3/conv/Sigmoid:0 \
  --output_pb True \
  --output_no_quant_float32_tflite True \
  --output_weight_quant_tflite True \
  --output_float16_quant_tflite True
"""


import os
import sys
import numpy as np
import json
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import tensorflow.compat.v1 as tf
import tensorflow as tfv2
import shutil
import pprint
import argparse
from pathlib import Path

class Color:
    BLACK          = '\033[30m'
    RED            = '\033[31m'
    GREEN          = '\033[32m'
    YELLOW         = '\033[33m'
    BLUE           = '\033[34m'
    MAGENTA        = '\033[35m'
    CYAN           = '\033[36m'
    WHITE          = '\033[37m'
    COLOR_DEFAULT  = '\033[39m'
    BOLD           = '\033[1m'
    UNDERLINE      = '\033[4m'
    INVISIBLE      = '\033[08m'
    REVERCE        = '\033[07m'
    BG_BLACK       = '\033[40m'
    BG_RED         = '\033[41m'
    BG_GREEN       = '\033[42m'
    BG_YELLOW      = '\033[43m'
    BG_BLUE        = '\033[44m'
    BG_MAGENTA     = '\033[45m'
    BG_CYAN        = '\033[46m'
    BG_WHITE       = '\033[47m'
    BG_DEFAULT     = '\033[49m'
    RESET          = '\033[0m'

"""
From:
    {
      "deprecated_builtin_code": 99,
      "version": 1,
      "builtin_code": "ADD"
    },
    {
      "deprecated_builtin_code": 100,
      "version": 1,
      "builtin_code": "ADD"
    },
    {
      "deprecated_builtin_code": 6,
      "version": 2,
      "builtin_code": "ADD"
    }

To:
    {
      "deprecated_builtin_code": 99,
      "version": 1,
      "builtin_code": "SQUARED_DIFFERENCE"
    },
    {
      "deprecated_builtin_code": 100,
      "version": 1,
      "builtin_code": "MIRROR_PAD"
    },
    {
      "deprecated_builtin_code": 6,
      "version": 2,
      "builtin_code": "DEQUANTIZE"
    }

"deprecated_builtin_code": "builtin_code"
op_types = {
    0: 'ADD',
    1: 'AVERAGE_POOL_2D',
    2: 'CONCATENATION',
    3: 'CONV_2D',
    4: 'DEPTHWISE_CONV_2D',
    5: 'DEPTH_TO_SPACE',
    6: 'DEQUANTIZE',
    7: 'EMBEDDING_LOOKUP',
    8: 'FLOOR',
    9: 'FULLY_CONNECTED',
    10: 'HASHTABLE_LOOKUP',
    11: 'L2_NORMALIZATION',
    12: 'L2_POOL_2D',
    13: 'LOCAL_RESPONSE_NORMALIZATION',
    14: 'LOGISTIC',
    15: 'LSH_PROJECTION',
    16: 'LSTM',
    17: 'MAX_POOL_2D',
    18: 'MUL',
    19: 'RELU',
    20: 'RELU_N1_TO_1',
    21: 'RELU6',
    22: 'RESHAPE',
    23: 'RESIZE_BILINEAR',
    24: 'RNN',
    25: 'SOFTMAX',
    26: 'SPACE_TO_DEPTH',
    27: 'SVDF',
    28: 'TANH',
    29: 'CONCAT_EMBEDDINGS',
    30: 'SKIP_GRAM',
    31: 'CALL',
    32: 'CUSTOM',
    33: 'EMBEDDING_LOOKUP_SPARSE',
    34: 'PAD',
    35: 'UNIDIRECTIONAL_SEQUENCE_RNN',
    36: 'GATHER',
    37: 'BATCH_TO_SPACE_ND',
    38: 'SPACE_TO_BATCH_ND',
    39: 'TRANSPOSE',
    40: 'MEAN',
    41: 'SUB',
    42: 'DIV',
    43: 'SQUEEZE',
    44: 'UNIDIRECTIONAL_SEQUENCE_LSTM',
    45: 'STRIDED_SLICE',
    46: 'BIDIRECTIONAL_SEQUENCE_RNN',
    47: 'EXP',
    48: 'TOPK_V2',
    49: 'SPLIT',
    50: 'LOG_SOFTMAX',
    51: 'DELEGATE',
    52: 'BIDIRECTIONAL_SEQUENCE_LSTM',
    53: 'CAST',
    54: 'PRELU',
    55: 'MAXIMUM',
    56: 'ARG_MAX',
    57: 'MINIMUM',
    58: 'LESS',
    59: 'NEG',
    60: 'PADV2',
    61: 'GREATER',
    62: 'GREATER_EQUAL',
    63: 'LESS_EQUAL',
    64: 'SELECT',
    65: 'SLICE',
    66: 'SIN',
    67: 'TRANSPOSE_CONV',
    68: 'SPARSE_TO_DENSE',
    69: 'TILE',
    70: 'EXPAND_DIMS',
    71: 'EQUAL',
    72: 'NOT_EQUAL',
    73: 'LOG',
    74: 'SUM',
    75: 'SQRT',
    76: 'RSQRT',
    77: 'SHAPE',
    78: 'POW',
    79: 'ARG_MIN',
    80: 'FAKE_QUANT',
    81: 'REDUCE_PROD',
    82: 'REDUCE_MAX',
    83: 'PACK',
    84: 'LOGICAL_OR',
    85: 'ONE_HOT',
    86: 'LOGICAL_AND',
    87: 'LOGICAL_NOT',
    88: 'UNPACK',
    89: 'REDUCE_MIN',
    90: 'FLOOR_DIV',
    91: 'REDUCE_ANY',
    92: 'SQUARE',
    93: 'ZEROS_LIKE',
    94: 'FILL',
    95: 'FLOOR_MOD',
    96: 'RANGE',
    97: 'RESIZE_NEAREST_NEIGHBOR',
    98: 'LEAKY_RELU',
    99: 'SQUARED_DIFFERENCE',
    100: 'MIRROR_PAD',
    101: 'ABS',
    102: 'SPLIT_V',
    103: 'UNIQUE',
    104: 'CEIL',
    105: 'REVERSE_V2',
    106: 'ADD_N',
    107: 'GATHER_ND',
    108: 'COS',
    109: 'WHERE',
    110: 'RANK',
    111: 'ELU',
    112: 'REVERSE_SEQUENCE',
    113: 'MATRIX_DIAG',
    114: 'QUANTIZE',
    115: 'MATRIX_SET_DIAG',
    116: 'ROUND',
    117: 'HARD_SWISH',
    118: 'IF',
    119: 'WHILE',
    120: 'NON_MAX_SUPPRESSION_V4',
    121: 'NON_MAX_SUPPRESSION_V5',
    122: 'SCATTER_ND',
    123: 'SELECT_V2',
    124: 'DENSIFY',
    125: 'SEGMENT_SUM',
    126: 'BATCH_MATMUL',
    127: 'PLACEHOLDER_FOR_GREATER_OP_CODES',
    128: 'CUMSUM',
    129: 'CALL_ONCE',
    130: 'BROADCAST_TO',
    131: 'RFFT2D'
}
"""

#################################################################
# Change to True when converting to EdgeTPU model.
optimizing_for_edgetpu_flg = False
#################################################################

def gen_model_json(flatc_path, model_output_path, jsonfile_path, schema_path, model_path):
    if not os.path.exists(jsonfile_path):
        cmd = (f'{flatc_path} -t --strict-json --defaults-json -o . {schema_path} -- {model_path}')
        print(f'output json command = {cmd}')
        os.system(cmd)


def parse_json(jsonfile_path):
    j = json.load(open(jsonfile_path))
    op_types = [v['builtin_code'] for v in j['operator_codes']]
    print('op_types:', op_types)
    if op_types.count('ADD') > 1:
        print(f'{Color.RED}ERROR:{Color.RESET} The version of schema.fbs does not match the format version of .tflite. Please modify the "builtin_code" in the "operator_codes" section.')
        sys.exit(-1)
    ops = j['subgraphs'][0]['operators']
    print('num of ops:', len(ops))
    return ops, op_types

def optimizing_hardswish_for_edgetpu(input_op, name=None):
    ret_op = None
    if not optimizing_for_edgetpu_flg:
        ret_op = input_op * tf.nn.relu6(input_op + 3) * 0.16666667
    else:
        ret_op = input_op * tf.nn.relu6(input_op + 3) * 0.16666666
    return ret_op

def make_graph(ops, op_types, interpreter, replace_swish_and_hardswish, optimizing_hardswish_for_edgetpu, replace_prelu_and_minmax):

    tensors = {}
    input_details = interpreter.get_input_details()

    pprint.pprint(input_details)
    for input_detail in input_details:
        tensors[input_detail['index']] = tf.placeholder(
            dtype=input_detail['dtype'],
            shape=input_detail['shape'],
            name=input_detail['name'])

    for op in ops:
        print('@@@@@@@@@@@@@@ op:', op)
        op_type = op_types[op['opcode_index']]
        print('@@@@@@@@@@@@@@ op_type:', op_type)

        if op_type == 'CONV_2D':
            input_tensor = None
            weights = None
            bias = None
            if len(op['inputs']) == 1:
                input_tensor = tensors[op['inputs'][0]]
                weights_detail = interpreter._get_tensor_details(op['inputs'][1])
                weights = interpreter.get_tensor(weights_detail['index']).transpose(1,2,3,0)
                bias_detail = interpreter._get_tensor_details(op['inputs'][2])
                bias = interpreter.get_tensor(bias_detail['index'])
            elif len(op['inputs']) == 2:
                input_tensor = tensors[op['inputs'][0]]
                weights = tensors[op['inputs'][1]].transpose(1,2,3,0)
                bias_detail = interpreter._get_tensor_details(op['inputs'][2])
                bias = interpreter.get_tensor(bias_detail['index'])
            elif len(op['inputs']) == 3:
                input_tensor = tensors[op['inputs'][0]]
                weights = tensors[op['inputs'][1]].transpose(1,2,3,0)
                bias = tensors[op['inputs'][2]]

            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            options = op['builtin_options']
            output_tensor = tf.nn.conv2d(
                input_tensor,
                weights,
                strides=[1, options['stride_h'], options['stride_w'], 1],
                padding=options['padding'],
                dilations=[
                    1, options['dilation_h_factor'],
                    options['dilation_w_factor'], 1
                ])

            options = op['builtin_options']
            activation = options['fused_activation_function']
            if activation == 'NONE':
                output_tensor = tf.add(output_tensor, bias, name=output_detail['name'])
            elif activation == 'RELU':
                output_tensor = tf.add(output_tensor, bias)
                output_tensor = tf.nn.relu(output_tensor, name=output_detail['name'])
            elif activation == 'RELU6':
                output_tensor = tf.add(output_tensor, bias)
                output_tensor = tf.nn.relu6(output_tensor, name=output_detail['name'])
            else:
                raise ValueError(activation)

            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** CONV_2D')

        elif op_type == 'DEPTHWISE_CONV_2D':
            input_tensor = None
            weights = None
            bias = None
            if len(op['inputs']) == 1:
                input_tensor = tensors[op['inputs'][0]]
                weights_detail = interpreter._get_tensor_details(op['inputs'][1])
                weights = interpreter.get_tensor(weights_detail['index']).transpose(1,2,3,0)
                bias_detail = interpreter._get_tensor_details(op['inputs'][2])
                bias = interpreter.get_tensor(bias_detail['index'])
            elif len(op['inputs']) == 2:
                input_tensor = tensors[op['inputs'][0]]
                weights = tensors[op['inputs'][1]].transpose(1,2,3,0)
                bias_detail = interpreter._get_tensor_details(op['inputs'][2])
                bias = interpreter.get_tensor(bias_detail['index'])
            elif len(op['inputs']) == 3:
                input_tensor = tensors[op['inputs'][0]]
                weights = tensors[op['inputs'][1]].transpose(1,2,3,0)
                bias = tensors[op['inputs'][2]]

            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            options = op['builtin_options']
            output_tensor = tf.nn.depthwise_conv2d(
                input_tensor,
                weights,
                strides=[1, options['stride_h'], options['stride_w'], 1],
                padding=options['padding'],
                dilations=[options['dilation_h_factor'], options['dilation_w_factor']])

            options = op['builtin_options']
            activation = options['fused_activation_function']
            if activation == 'NONE':
                output_tensor = tf.add(output_tensor, bias, name=output_detail['name'])
            elif activation == 'RELU':
                output_tensor = tf.add(output_tensor, bias)
                output_tensor = tf.nn.relu(output_tensor, name=output_detail['name'])
            elif activation == 'RELU6':
                output_tensor = tf.add(output_tensor, bias)
                output_tensor = tf.nn.relu6(output_tensor, name=output_detail['name'])
            else:
                raise ValueError(activation)

            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** DEPTHWISE_CONV_2D')

        elif op_type == 'MAX_POOL_2D':
            input_tensor = tensors[op['inputs'][0]]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            options = op['builtin_options']
            output_tensor = tf.nn.max_pool(
                input_tensor,
                ksize=[
                    1, options['filter_height'], options['filter_width'], 1
                ],
                strides=[1, options['stride_h'], options['stride_w'], 1],
                padding=options['padding'],
                name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** MAX_POOL_2D')

        elif op_type == 'PAD':
            input_tensor = tensors[op['inputs'][0]]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            paddings_detail = interpreter._get_tensor_details(op['inputs'][1])
            paddings_array = interpreter.get_tensor(paddings_detail['index'])
            output_tensor = tf.pad(input_tensor, paddings_array, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** PAD')

        elif op_type == 'MIRROR_PAD':
            input_tensor = tensors[op['inputs'][0]]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            paddings_detail = interpreter._get_tensor_details(op['inputs'][1])
            paddings_array = interpreter.get_tensor(paddings_detail['index'])
            options = op['builtin_options']
            mode = options['mode']
            output_tensor = tf.raw_ops.MirrorPad(input=input_tensor, paddings=paddings_array, mode=mode, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** MIRROR_PAD')

        elif op_type == 'RELU':
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            input_tensor = tensors[op['inputs'][0]]
            output_tensor = tf.nn.relu(input_tensor, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** RELU')

        elif op_type == 'PRELU':
            input_tensor = tensors[op['inputs'][0]]
            alpha_detail = interpreter._get_tensor_details(op['inputs'][1])
            alpha_array = interpreter.get_tensor(alpha_detail['index'])
            output_tensor = tf.keras.layers.PReLU(alpha_initializer=tf.keras.initializers.Constant(alpha_array),
                                                  shared_axes=[1, 2])(input_tensor)
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** PRELU')

        elif op_type == 'RELU6':
            input_tensor = tensors[op['inputs'][0]]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.nn.relu6(input_tensor, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor 
            print('**************************************************************** RELU6')

        elif op_type == 'RESHAPE':
            input_tensor = tensors[op['inputs'][0]]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            options = op['builtin_options']
            output_tensor = tf.reshape(input_tensor, options['new_shape'], name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** RESHAPE')

        elif op_type == 'ADD':
            input_tensor_0 = tensors[op['inputs'][0]]

            input_tensor_1 = None
            if len(op['inputs']) == 1:
                param = interpreter._get_tensor_details(op['inputs'][1])
                input_tensor_1 = interpreter.get_tensor(param['index'])
            elif len(op['inputs']) == 2:
                try:
                    input_tensor_1 = tensors[op['inputs'][1]]
                except:
                    param = interpreter._get_tensor_details(op['inputs'][1])
                    input_tensor_1 = interpreter.get_tensor(param['index'])

            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            options = op['builtin_options']
            activation = options['fused_activation_function']
            if activation == 'NONE':
                output_tensor = tf.add(input_tensor_0, input_tensor_1, name=output_detail['name'])
            elif activation == 'RELU':
                output_tensor = tf.add(input_tensor_0, input_tensor_1)
                output_tensor = tf.nn.relu(output_tensor, name=output_detail['name'])
            elif activation == 'RELU6':
                output_tensor = tf.add(input_tensor_0, input_tensor_1)
                output_tensor = tf.nn.relu6(output_tensor, name=output_detail['name'])
            else:
                raise ValueError(activation)

            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** ADD')

        elif op_type == 'SUB':
            input_tensor_0 = tensors[op['inputs'][0]]

            input_tensor_1 = None
            if len(op['inputs']) == 1:
                param = interpreter._get_tensor_details(op['inputs'][1])
                input_tensor_1 = interpreter.get_tensor(param['index'])            
            elif len(op['inputs']) == 2:
                try:
                    input_tensor_1 = tensors[op['inputs'][1]]
                except:
                    param = interpreter._get_tensor_details(op['inputs'][1])
                    input_tensor_1 = interpreter.get_tensor(param['index'])
            
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            options = op['builtin_options']
            activation = options['fused_activation_function']
            if activation == 'NONE':
                output_tensor = tf.math.subtract(input_tensor_0, input_tensor_1, name=output_detail['name'])
            elif activation == 'RELU':
                output_tensor = tf.math.subtract(input_tensor_0, input_tensor_1)
                output_tensor = tf.nn.relu(output_tensor, name=output_detail['name'])
            elif activation == 'RELU6':
                output_tensor = tf.math.subtract(input_tensor_0, input_tensor_1)
                output_tensor = tf.nn.relu6(output_tensor, name=output_detail['name'])
            else:
                raise ValueError(activation)

            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** SUB')

        elif op_type == 'CONCATENATION':
            inputs = [tensors[input] for input in op['inputs']]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            options = op['builtin_options']
            output_tensor = tf.concat(inputs,
                                    options['axis'],
                                    name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** CONCATENATION')

        elif op_type == 'LOGISTIC':
            input_tensor = tensors[op['inputs'][0]]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.math.sigmoid(input_tensor, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** LOGISTIC')

        elif op_type == 'TRANSPOSE_CONV':
            input_tensor = tensors[op['inputs'][2]]
            weights_detail = interpreter._get_tensor_details(op['inputs'][1])
            output_shape_detail = interpreter._get_tensor_details(op['inputs'][0])
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            weights_array = interpreter.get_tensor(weights_detail['index'])
            weights_array = np.transpose(weights_array, (1, 2, 0, 3))
            output_shape_array = interpreter.get_tensor(output_shape_detail['index'])
            weights = tf.Variable(weights_array, name=weights_detail['name'])
            shape = tf.Variable(output_shape_array, name=output_shape_detail['name'])
            options = op['builtin_options']
            output_tensor = tf.nn.conv2d_transpose(input_tensor,
                                                   weights,
                                                   shape,
                                                   [1, options['stride_h'], options['stride_w'], 1],
                                                   padding=options['padding'],
                                                   name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** TRANSPOSE_CONV')

        elif op_type == 'MUL':
            input_tensor_0 = tensors[op['inputs'][0]]

            input_tensor_1 = None
            if len(op['inputs']) == 1:
                param = interpreter._get_tensor_details(op['inputs'][1])
                input_tensor_1 = interpreter.get_tensor(param['index'])
            elif len(op['inputs']) == 2:
                try:
                    input_tensor_1 = tensors[op['inputs'][1]]
                except:
                    param = interpreter._get_tensor_details(op['inputs'][1])
                    input_tensor_1 = interpreter.get_tensor(param['index'])

            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            options = op['builtin_options']
            activation = options['fused_activation_function']
            if activation == 'NONE':
                output_tensor = tf.multiply(input_tensor_0, input_tensor_1, name=output_detail['name'])
            elif activation == 'RELU':
                output_tensor = tf.multiply(input_tensor_0, input_tensor_1)
                output_tensor = tf.nn.relu(output_tensor, name=output_detail['name'])
            elif activation == 'RELU6':
                output_tensor = tf.multiply(input_tensor_0, input_tensor_1)
                output_tensor = tf.nn.relu6(output_tensor, name=output_detail['name'])
            else:
                raise ValueError(activation)

            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** MUL')

        elif op_type == 'HARD_SWISH':
            input_tensor = tensors[op['inputs'][0]]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = optimizing_hardswish_for_edgetpu(input_tensor, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** HARD_SWISH')

        elif op_type == 'AVERAGE_POOL_2D':
            input_tensor = tensors[op['inputs'][0]]
            options = op['builtin_options']
            pool_size = [options['filter_height'], options['filter_width']]
            strides = [options['stride_h'], options['stride_w']]
            padding = options['padding']
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.keras.layers.AveragePooling2D(pool_size=pool_size,
                                                             strides=strides,
                                                             padding=padding,
                                                             name=output_detail['name'])(input_tensor)
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** AVERAGE_POOL_2D')

        elif op_type == 'FULLY_CONNECTED':
            input_tensor = tensors[op['inputs'][0]]
            weights = tensors[op['inputs'][1]].transpose(1,0)
            bias = tensors[op['inputs'][2]]
            output_shape_detail = interpreter._get_tensor_details(op['inputs'][0])
            output_shape_array = interpreter.get_tensor(output_shape_detail['index'])
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.keras.layers.Dense(units=output_shape_array.shape[3],
                                                  use_bias=True,
                                                  kernel_initializer=tf.keras.initializers.Constant(weights),
                                                  bias_initializer=tf.keras.initializers.Constant(bias),
                                                  name=output_detail['name'])(input_tensor)
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** FULLY_CONNECTED')

        elif op_type == 'RESIZE_BILINEAR':
            input_tensor = tensors[op['inputs'][0]]
            size_detail = interpreter._get_tensor_details(op['inputs'][1])
            size = interpreter.get_tensor(size_detail['index'])
            size_height = size[0]
            size_width  = size[1]

            def upsampling2d_bilinear(x, size_height, size_width):
                if optimizing_for_edgetpu_flg:
                    return tf.image.resize_bilinear(x, (size_height, size_width))
                else:
                    return tfv2.image.resize(x, [size_height, size_width], method='bilinear')

            output_tensor = tf.keras.layers.Lambda(upsampling2d_bilinear, arguments={'size_height': size_height, 'size_width': size_width})(input_tensor)
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** RESIZE_BILINEAR')

        elif op_type == 'RESIZE_NEAREST_NEIGHBOR':
            input_tensor = tensors[op['inputs'][0]]
            size_detail = interpreter._get_tensor_details(op['inputs'][1])
            size = interpreter.get_tensor(size_detail['index'])
            size_height = size[0]
            size_width  = size[1]

            def upsampling2d_nearrest(x, size_height, size_width):
                if optimizing_for_edgetpu_flg:
                    return tf.image.resize_nearest_neighbor(x, (size_height, size_width))
                else:
                    return tfv2.image.resize(x, [size_height, size_width], method='nearest')

            output_tensor = tf.keras.layers.Lambda(upsampling2d_nearrest, arguments={'size_height': size_height, 'size_width': size_width})(input_tensor)
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** RESIZE_NEAREST_NEIGHBOR')

        elif op_type == 'MEAN':
            input_tensor_0 = tensors[op['inputs'][0]]

            input_tensor_1 = None
            if len(op['inputs']) == 1:
                param = interpreter._get_tensor_details(op['inputs'][1])
                input_tensor_1 = interpreter.get_tensor(param['index'])
            elif len(op['inputs']) == 2:
                try:
                    input_tensor_1 = tensors[op['inputs'][1]]
                except:
                    param = interpreter._get_tensor_details(op['inputs'][1])
                    input_tensor_1 = interpreter.get_tensor(param['index'])

            options = op['builtin_options']
            keepdims = options['keep_dims']
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.math.reduce_mean(input_tensor_0, input_tensor_1, keepdims=keepdims, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** MEAN')

        elif op_type == 'SQUARED_DIFFERENCE':
            input_tensor_0 = tensors[op['inputs'][0]]

            input_tensor_1 = None
            if len(op['inputs']) == 1:
                param = interpreter._get_tensor_details(op['inputs'][1])
                input_tensor_1 = interpreter.get_tensor(param['index'])
            elif len(op['inputs']) == 2:
                try:
                    input_tensor_1 = tensors[op['inputs'][1]]
                except:
                    param = interpreter._get_tensor_details(op['inputs'][1])
                    input_tensor_1 = interpreter.get_tensor(param['index'])
            
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.math.squared_difference(input_tensor_0, input_tensor_1, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** SQUARED_DIFFERENCE')

        elif op_type == 'RSQRT':
            input_tensor = tensors[op['inputs'][0]]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.math.rsqrt(input_tensor, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** RSQRT')

        elif op_type == 'DEQUANTIZE':
            weights_detail = interpreter._get_tensor_details(op['inputs'][0])
            weights = interpreter.get_tensor(weights_detail['index'])
            output_tensor = weights.astype(np.float32)
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** DEQUANTIZE')

        elif op_type == 'FLOOR':
            input_tensor = tensors[op['inputs'][0]]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.math.floor(input_tensor, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** FLOOR')

        elif op_type == 'TANH':
            input_tensor = tensors[op['inputs'][0]]
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.math.tanh(input_tensor, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** TANH')

        elif op_type == 'DIV':
            input_tensor1 = tensors[op['inputs'][0]]
            input_tensor2 = None
            try:
                input_tensor2 = tensors[op['inputs'][1]]
            except:
                weights_detail = interpreter._get_tensor_details(op['inputs'][1])
                input_tensor2 = interpreter.get_tensor(weights_detail['index'])
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.math.divide(input_tensor1, input_tensor2, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** DIV')

        elif op_type == 'FLOOR_DIV':
            input_tensor1 = tensors[op['inputs'][0]]
            input_tensor2 = None
            try:
                input_tensor2 = tensors[op['inputs'][1]]
            except:
                weights_detail = interpreter._get_tensor_details(op['inputs'][1])
                input_tensor2 = interpreter.get_tensor(weights_detail['index'])
            output_detail = interpreter._get_tensor_details(op['outputs'][0])
            output_tensor = tf.math.floordiv(input_tensor1, input_tensor2, name=output_detail['name'])
            tensors[output_detail['index']] = output_tensor
            print('**************************************************************** FLOOR_DIV')

        else:
            print(f'The {op_type} layer is not yet implemented.')
            sys.exit(-1)

        # pprint.pprint(tensors[output_detail['index']])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', type=str, required=True, help='input tflite model path (*.tflite)')
    parser.add_argument('--flatc_path', type=str, required=True, help='flatc file path (flatc)')
    parser.add_argument('--schema_path', type=str, required=True, help='schema.fbs path (schema.fbs)')
    parser.add_argument('--input_node_names', type=str, required=True, help='(e.g.1) input:0,input:1,input:2 / (e.g.2) images:0,input:0,param:0')
    parser.add_argument('--output_node_names', type=str, required=True, help='(e.g.1) output:0,output:1,output:2 / (e.g.2) Identity:0,Identity:1,output:0')

    parser.add_argument('--model_output_path', type=str, default='saved_model', help='The output folder path of the converted model file')
    parser.add_argument('--output_pb', type=bool, default=False, help='.pb output switch')
    parser.add_argument('--output_no_quant_float32_tflite', type=bool, default=False, help='float32 tflite output switch')
    parser.add_argument('--output_weight_quant_tflite', type=bool, default=False, help='weight quant tflite output switch')
    parser.add_argument('--output_float16_quant_tflite', type=bool, default=False, help='float16 quant tflite output switch')
    parser.add_argument('--output_integer_quant_tflite', type=bool, default=False, help='integer quant tflite output switch')
    parser.add_argument('--output_full_integer_quant_tflite', type=bool, default=False, help='full integer quant tflite output switch')
    parser.add_argument('--output_integer_quant_type', type=str, default='int8', help='Input and output types when doing Integer Quantization (\'int8 (default)\' or \'uint8\')')
    parser.add_argument('--string_formulas_for_normalization', type=str, default='(data - [127.5,127.5,127.5]) / [127.5,127.5,127.5]', help='String formulas for normalization. It is evaluated by Python\'s eval() function. Default: \'(data - [127.5,127.5,127.5]) / [127.5,127.5,127.5]\'')
    parser.add_argument('--calib_ds_type', type=str, default='tfds', help='Types of data sets for calibration. tfds or numpy(Future Implementation)')
    parser.add_argument('--ds_name_for_tfds_for_calibration', type=str, default='coco/2017', help='Dataset name for TensorFlow Datasets for calibration. https://www.tensorflow.org/datasets/catalog/overview')
    parser.add_argument('--split_name_for_tfds_for_calibration', type=str, default='validation', help='Split name for TensorFlow Datasets for calibration. https://www.tensorflow.org/datasets/catalog/overview')
    tfds_dl_default_path = f'{str(Path.home())}/TFDS'
    parser.add_argument('--download_dest_folder_path_for_the_calib_tfds', type=str, default=tfds_dl_default_path, help='Download destination folder path for the calibration dataset. Default: $HOME/TFDS')
    parser.add_argument('--tfds_download_flg', type=bool, default=True, help='True to automatically download datasets from TensorFlow Datasets. True or False')
    parser.add_argument('--output_tfjs', type=bool, default=False, help='tfjs model output switch')
    parser.add_argument('--output_tftrt', type=bool, default=False, help='tftrt model output switch')
    parser.add_argument('--output_coreml', type=bool, default=False, help='coreml model output switch')
    parser.add_argument('--output_edgetpu', type=bool, default=False, help='edgetpu model output switch')
    parser.add_argument('--replace_swish_and_hardswish', type=bool, default=False, help='Replace swish and hard-swish with each other')
    parser.add_argument('--optimizing_hardswish_for_edgetpu', type=bool, default=False, help='Optimizing hardswish for edgetpu')
    parser.add_argument('--replace_prelu_and_minmax', type=bool, default=False, help='Replace prelu and minimum/maximum with each other')
    args = parser.parse_args()

    model, ext = os.path.splitext(args.model_path)
    model_path = args.model_path
    if ext != '.tflite':
        print('The specified model is not \'.tflite\' file.')
        sys.exit(-1)
    flatc_path = args.flatc_path
    schema_path = args.schema_path
    input_node_names = args.input_node_names.split(',')
    output_node_names = args.output_node_names.split(',')

    model_output_path = args.model_output_path.rstrip('/')
    output_pb = args.output_pb
    output_no_quant_float32_tflite =  args.output_no_quant_float32_tflite
    output_weight_quant_tflite = args.output_weight_quant_tflite
    output_float16_quant_tflite = args.output_float16_quant_tflite
    output_integer_quant_tflite = args.output_integer_quant_tflite
    output_full_integer_quant_tflite = args.output_full_integer_quant_tflite
    output_integer_quant_type = args.output_integer_quant_type.lower()
    string_formulas_for_normalization = args.string_formulas_for_normalization.lower()
    calib_ds_type = args.calib_ds_type.lower()
    ds_name_for_tfds_for_calibration = args.ds_name_for_tfds_for_calibration
    split_name_for_tfds_for_calibration = args.split_name_for_tfds_for_calibration
    download_dest_folder_path_for_the_calib_tfds = args.download_dest_folder_path_for_the_calib_tfds
    tfds_download_flg = args.tfds_download_flg
    output_tfjs = args.output_tfjs
    output_tftrt = args.output_tftrt
    output_coreml = args.output_coreml
    output_edgetpu = args.output_edgetpu
    replace_swish_and_hardswish = args.replace_swish_and_hardswish
    optimizing_hardswish_for_edgetpu = args.optimizing_hardswish_for_edgetpu
    replace_prelu_and_minmax = args.replace_prelu_and_minmax

    if output_edgetpu:
        output_full_integer_quant_tflite = True

    from pkg_resources import working_set
    package_list = []
    for dist in working_set:
        package_list.append(dist.project_name)

    if output_tfjs:
        if not 'tensorflowjs' in package_list:
            print('\'tensorflowjs\' is not installed. Please run the following command to install \'tensorflowjs\'.')
            print('pip3 install --upgrade tensorflowjs')
            sys.exit(-1)
    if output_tftrt:
        if not 'tensorrt' in package_list:
            print('\'tensorrt\' is not installed. Please check the following website and install \'tensorrt\'.')
            print('https://docs.nvidia.com/deeplearning/tensorrt/install-guide/index.html')
            sys.exit(-1)
    if output_coreml:
        if not 'coremltools' in package_list:
            print('\'coremltoos\' is not installed. Please run the following command to install \'coremltoos\'.')
            print('pip3 install --upgrade coremltools')
            sys.exit(-1)
    if output_integer_quant_tflite or output_full_integer_quant_tflite:
        if not 'tensorflow-datasets' in package_list:
            print('\'tensorflow-datasets\' is not installed. Please run the following command to install \'tensorflow-datasets\'.')
            print('pip3 install --upgrade tensorflow-datasets')
            sys.exit(-1)

    if output_integer_quant_type == 'int8' or output_integer_quant_type == 'uint8':
        pass
    else:
        print('Only \'int8\' or \'uint8\' can be specified for output_integer_quant_type.')
        sys.exit(-1)

    if calib_ds_type == 'tfds':
        pass
    elif calib_ds_type == 'numpy':
        print('The Numpy mode of the data set for calibration will be implemented in the future.')
        sys.exit(-1)
    else:
        print('Only \'tfds\' or \'numpy\' can be specified for calib_ds_type.')
        sys.exit(-1)
    del package_list

    shutil.rmtree(model_output_path, ignore_errors=True)

    tf.disable_eager_execution()

    jsonfile_path = f'./{model}.json'
    gen_model_json(flatc_path, model_output_path, jsonfile_path, schema_path, model_path)
    ops, op_types = parse_json(jsonfile_path)

    interpreter = tf.lite.Interpreter(model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print(input_details)
    print(output_details)

    print(f'{Color.REVERCE}TensorFlow/Keras model building process starts{Color.RESET}', '=' * 38)
    make_graph(ops, op_types, interpreter, replace_swish_and_hardswish, optimizing_hardswish_for_edgetpu, replace_prelu_and_minmax)
    print(f'{Color.GREEN}TensorFlow/Keras model building process complete!{Color.RESET}')

    # saved_model / .pb output
    try:
        print(f'{Color.REVERCE}saved_model / .pb output started{Color.RESET}', '=' * 52)
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        graph = tf.get_default_graph()
        with tf.Session(config=config, graph=graph) as sess:
            sess.run(tf.global_variables_initializer())
            graph_def = tf.graph_util.convert_variables_to_constants(
                sess=sess,
                input_graph_def=graph.as_graph_def(),
                output_node_names=[name.rstrip(':0') for name in output_node_names])

            tf.saved_model.simple_save(
                sess,
                model_output_path,
                inputs= {t.rstrip(":0"): graph.get_tensor_by_name(t) for t in input_node_names},
                outputs={t.rstrip(":0"): graph.get_tensor_by_name(t) for t in output_node_names}
            )

            if output_pb:
                with tf.io.gfile.GFile(f'{model_output_path}/model_float32.pb', 'wb') as f:
                    f.write(graph_def.SerializeToString())

        print(f'{Color.GREEN}saved_model / .pb output complete!{Color.RESET}')
    except Exception as e:
        print(f'{Color.RED}ERROR:{Color.RESET}', e)
        import traceback
        traceback.print_exc()
        sys.exit(-1)


    # No Quantization - Input/Output=float32
    if output_no_quant_float32_tflite:
        try:
            print(f'{Color.REVERCE}tflite Float32 convertion started{Color.RESET}', '=' * 51)
            converter = tfv2.lite.TFLiteConverter.from_saved_model(model_output_path)
            converter.target_spec.supported_ops = [tfv2.lite.OpsSet.TFLITE_BUILTINS, tfv2.lite.OpsSet.SELECT_TF_OPS]
            tflite_model = converter.convert()
            with open(f'{model_output_path}/model_float32.tflite', 'wb') as w:
                w.write(tflite_model)
            print(f'{Color.GREEN}tflite Float32 convertion complete!{Color.RESET} - {model_output_path}/model_float32.tflite')
        except Exception as e:
            print(f'{Color.RED}ERROR:{Color.RESET}', e)
            import traceback
            traceback.print_exc()

    # Weight Quantization - Input/Output=float32
    if output_weight_quant_tflite:
        try:
            print(f'{Color.REVERCE}Weight Quantization started{Color.RESET}', '=' * 57)
            converter = tfv2.lite.TFLiteConverter.from_saved_model(model_output_path)
            converter.optimizations = [tfv2.lite.Optimize.OPTIMIZE_FOR_SIZE]
            converter.target_spec.supported_ops = [tfv2.lite.OpsSet.TFLITE_BUILTINS, tfv2.lite.OpsSet.SELECT_TF_OPS]
            tflite_model = converter.convert()
            with open(f'{model_output_path}/model_weight_quant.tflite', 'wb') as w:
                w.write(tflite_model)
            print(f'{Color.GREEN}Weight Quantization complete!{Color.RESET} - {model_output_path}/model_weight_quant.tflite')
        except Exception as e:
            print(f'{Color.RED}ERROR:{Color.RESET}', e)
            import traceback
            traceback.print_exc()

    # Float16 Quantization - Input/Output=float32
    if output_float16_quant_tflite:
        try:
            print(f'{Color.REVERCE}Float16 Quantization started{Color.RESET}', '=' * 56)
            converter = tfv2.lite.TFLiteConverter.from_saved_model(model_output_path)
            converter.optimizations = [tfv2.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tfv2.float16]
            converter.target_spec.supported_ops = [tfv2.lite.OpsSet.TFLITE_BUILTINS, tfv2.lite.OpsSet.SELECT_TF_OPS]
            tflite_quant_model = converter.convert()
            with open(f'{model_output_path}/model_float16_quant.tflite', 'wb') as w:
                w.write(tflite_quant_model)
            print(f'{Color.GREEN}Float16 Quantization complete!{Color.RESET} - {model_output_path}/model_float16_quant.tflite')
        except Exception as e:
            print(f'{Color.RED}ERROR:{Color.RESET}', e)
            import traceback
            traceback.print_exc()



if __name__ == '__main__':
    main()
