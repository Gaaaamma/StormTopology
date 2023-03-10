# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import MIInference_pb2 as MIInference__pb2


class MIInferenceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.doInference = channel.unary_unary(
                '/inference.MIInference/doInference',
                request_serializer=MIInference__pb2.Input.SerializeToString,
                response_deserializer=MIInference__pb2.Msg.FromString,
                )
        self.doMultiInference = channel.unary_unary(
                '/inference.MIInference/doMultiInference',
                request_serializer=MIInference__pb2.MultiInput.SerializeToString,
                response_deserializer=MIInference__pb2.MultiMsg.FromString,
                )


class MIInferenceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def doInference(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def doMultiInference(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MIInferenceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'doInference': grpc.unary_unary_rpc_method_handler(
                    servicer.doInference,
                    request_deserializer=MIInference__pb2.Input.FromString,
                    response_serializer=MIInference__pb2.Msg.SerializeToString,
            ),
            'doMultiInference': grpc.unary_unary_rpc_method_handler(
                    servicer.doMultiInference,
                    request_deserializer=MIInference__pb2.MultiInput.FromString,
                    response_serializer=MIInference__pb2.MultiMsg.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'inference.MIInference', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class MIInference(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def doInference(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/inference.MIInference/doInference',
            MIInference__pb2.Input.SerializeToString,
            MIInference__pb2.Msg.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def doMultiInference(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/inference.MIInference/doMultiInference',
            MIInference__pb2.MultiInput.SerializeToString,
            MIInference__pb2.MultiMsg.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
