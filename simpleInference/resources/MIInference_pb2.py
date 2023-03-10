# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: MIInference.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11MIInference.proto\x12\tinference\"\r\n\x0bVoidRequest\"-\n\nMultiInput\x12\x1f\n\x05input\x18\x01 \x03(\x0b\x32\x10.inference.Input\"5\n\x05Input\x12\n\n\x02id\x18\x01 \x01(\t\x12 \n\x04\x64\x61ta\x18\x02 \x03(\x0b\x32\x12.inference.EcgData\"L\n\x07\x45\x63gData\x12\x11\n\ttimestamp\x18\x01 \x01(\x05\x12\x0e\n\x06\x64iff_1\x18\x02 \x03(\x02\x12\x0e\n\x06\x64iff_2\x18\x03 \x03(\x02\x12\x0e\n\x06\x64iff_3\x18\x04 \x03(\x02\"2\n\x03Msg\x12\x0e\n\x06status\x18\x01 \x01(\x08\x12\x0e\n\x06result\x18\x02 \x01(\x08\x12\x0b\n\x03msg\x18\x03 \x01(\t\"7\n\x08MultiMsg\x12\x0e\n\x06status\x18\x01 \x03(\x08\x12\x0e\n\x06result\x18\x02 \x03(\x08\x12\x0b\n\x03msg\x18\x03 \x01(\t2~\n\x0bMIInference\x12/\n\x0b\x64oInference\x12\x10.inference.Input\x1a\x0e.inference.Msg\x12>\n\x10\x64oMultiInference\x12\x15.inference.MultiInput\x1a\x13.inference.MultiMsgb\x06proto3')



_VOIDREQUEST = DESCRIPTOR.message_types_by_name['VoidRequest']
_MULTIINPUT = DESCRIPTOR.message_types_by_name['MultiInput']
_INPUT = DESCRIPTOR.message_types_by_name['Input']
_ECGDATA = DESCRIPTOR.message_types_by_name['EcgData']
_MSG = DESCRIPTOR.message_types_by_name['Msg']
_MULTIMSG = DESCRIPTOR.message_types_by_name['MultiMsg']
VoidRequest = _reflection.GeneratedProtocolMessageType('VoidRequest', (_message.Message,), {
  'DESCRIPTOR' : _VOIDREQUEST,
  '__module__' : 'MIInference_pb2'
  # @@protoc_insertion_point(class_scope:inference.VoidRequest)
  })
_sym_db.RegisterMessage(VoidRequest)

MultiInput = _reflection.GeneratedProtocolMessageType('MultiInput', (_message.Message,), {
  'DESCRIPTOR' : _MULTIINPUT,
  '__module__' : 'MIInference_pb2'
  # @@protoc_insertion_point(class_scope:inference.MultiInput)
  })
_sym_db.RegisterMessage(MultiInput)

Input = _reflection.GeneratedProtocolMessageType('Input', (_message.Message,), {
  'DESCRIPTOR' : _INPUT,
  '__module__' : 'MIInference_pb2'
  # @@protoc_insertion_point(class_scope:inference.Input)
  })
_sym_db.RegisterMessage(Input)

EcgData = _reflection.GeneratedProtocolMessageType('EcgData', (_message.Message,), {
  'DESCRIPTOR' : _ECGDATA,
  '__module__' : 'MIInference_pb2'
  # @@protoc_insertion_point(class_scope:inference.EcgData)
  })
_sym_db.RegisterMessage(EcgData)

Msg = _reflection.GeneratedProtocolMessageType('Msg', (_message.Message,), {
  'DESCRIPTOR' : _MSG,
  '__module__' : 'MIInference_pb2'
  # @@protoc_insertion_point(class_scope:inference.Msg)
  })
_sym_db.RegisterMessage(Msg)

MultiMsg = _reflection.GeneratedProtocolMessageType('MultiMsg', (_message.Message,), {
  'DESCRIPTOR' : _MULTIMSG,
  '__module__' : 'MIInference_pb2'
  # @@protoc_insertion_point(class_scope:inference.MultiMsg)
  })
_sym_db.RegisterMessage(MultiMsg)

_MIINFERENCE = DESCRIPTOR.services_by_name['MIInference']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _VOIDREQUEST._serialized_start=32
  _VOIDREQUEST._serialized_end=45
  _MULTIINPUT._serialized_start=47
  _MULTIINPUT._serialized_end=92
  _INPUT._serialized_start=94
  _INPUT._serialized_end=147
  _ECGDATA._serialized_start=149
  _ECGDATA._serialized_end=225
  _MSG._serialized_start=227
  _MSG._serialized_end=277
  _MULTIMSG._serialized_start=279
  _MULTIMSG._serialized_end=334
  _MIINFERENCE._serialized_start=336
  _MIINFERENCE._serialized_end=462
# @@protoc_insertion_point(module_scope)
