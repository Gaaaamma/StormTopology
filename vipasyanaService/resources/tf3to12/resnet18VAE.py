import torch
import numpy as np
import torch.nn.functional as F
import os
from torch import nn
class ResBlock(nn.Module):
  def __init__(self,in_channel, filter_nums, stride=1, identity=False):
      super(ResBlock, self).__init__()

      self.conv_1 = nn.Conv1d(in_channel,filter_nums,kernel_size=9,stride=stride,padding=4)
      self.bn_1 = nn.BatchNorm1d(filter_nums)
      self.act_relu = nn.ReLU()

      self.conv_2 = nn.Conv1d(filter_nums,filter_nums,kernel_size=9,stride=1,padding=4)
      self.bn_2 = nn.BatchNorm1d(filter_nums)
      
      if stride !=1 or identity==False:
        self.block = []
        self.block.append(nn.Conv1d(in_channel,filter_nums,kernel_size=1,stride=stride))
        self.block = nn.Sequential(*self.block)
      else:
        self.block = lambda x:x

  def forward(self, inputs):
      x = self.conv_1(inputs)
      x = self.bn_1(x)
      x = self.act_relu(x)
      x = self.conv_2(x)
      x = self.bn_2(x)
      
      identity = self.block(inputs)
      outputs = x + identity
      outputs = self.act_relu(outputs)

      return outputs

class Res_VAE(torch.nn.Module):
    def __init__(self,layers_dims=None,nums_class=10,en_channels=None,de_channels=None):
        super(Res_VAE, self).__init__()
        self.layers_dims = layers_dims if layers_dims is not None else [2,2,2,2] # default ResNet18
        self.en_channels = en_channels if en_channels is not None else [80, 80, 80, 40, 20] 
        self.de_channels = de_channels if de_channels is not None else [20, 40, 40, 40, 80, 80, 12]
        self.lstm1 = nn.LSTM(3,12,batch_first=True)
        self.model = nn.Sequential(*[nn.Conv1d(12,self.en_channels[0],kernel_size=49,stride=1,padding=24),
                                nn.BatchNorm1d(self.en_channels[0]),
                                nn.ReLU(),
                                nn.MaxPool1d(kernel_size=2,stride=2)])#padding need check

        self.layer_1 = self.ResNet_build(self.en_channels[0],self.en_channels[1],self.layers_dims[0],identity=True)
        self.layer_2 = self.ResNet_build(self.en_channels[1],self.en_channels[2],self.layers_dims[1],stride=2)   
        self.layer_3 = self.ResNet_build(self.en_channels[2],self.en_channels[3],self.layers_dims[2],stride=2) #160->80
        self.layer_4 = self.ResNet_build(self.en_channels[3],self.en_channels[4],self.layers_dims[3],stride=1)   
        self.de_layer_1 = nn.Sequential(*[
            nn.ConvTranspose1d(1,self.de_channels[0], kernel_size=17, stride=1,padding =8,bias=True),
            nn.BatchNorm1d(self.de_channels[0]),
            nn.ELU(),
        ])
        self.de_layer_2=nn.Sequential(*[
            nn.ConvTranspose1d(60,self.de_channels[1], kernel_size=16, stride=1, padding=7,bias=True),
            nn.BatchNorm1d(self.de_channels[1]),
            nn.ELU(),
        ])
        self.de_layer_3=nn.Sequential(*[
            nn.ConvTranspose1d(40,self.de_channels[2], kernel_size=16, stride=1, padding=8, bias=True),
            nn.BatchNorm1d(self.de_channels[2]),
            nn.ELU(),
        ])
        self.de_layer_4=nn.Sequential(*[
            nn.ConvTranspose1d(120,self.de_channels[3], kernel_size=16, stride=2,padding=7,bias=True),
            nn.BatchNorm1d(self.de_channels[3]),
            nn.ELU(),
        ])
        self.de_layer_5 =nn.Sequential(*[
            nn.ConvTranspose1d(200,self.de_channels[4], kernel_size=16, stride=2, padding=7, bias=True),
            nn.BatchNorm1d(self.de_channels[4]),
            nn.ELU(),
        ])
        self.de_layer_6=nn.Sequential(*[
            nn.ConvTranspose1d(240,self.de_channels[5], kernel_size=16, stride=2, padding=7, bias=True),
            nn.BatchNorm1d(self.de_channels[5]),
            nn.ELU(),
        ])
        self.de_layer_7=nn.Sequential(*[
            nn.ConvTranspose1d(80,self.de_channels[6], kernel_size=9, stride=1, padding=4, bias=True),
            nn.BatchNorm1d(self.de_channels[6]),
            nn.ELU(),
        ])
        self.zmean = nn.Conv1d(self.en_channels[4],1, kernel_size=16, bias=True)
        self.zlogvar = nn.Conv1d(self.en_channels[4],1, kernel_size=16, bias=True)
        self.lstm = nn.LSTM(self.de_channels[6],12,batch_first=True)
        self.lc = nn.Linear(12,12)
        self.de_layer = [40,1,60,40,120,200,240,80,1280]
        # self.avg_pool = layers.GlobalAveragePooling2D()                 
        # self.fc_model = layers.Dense(nums_class)
    def reparameterization(self, mean, var):
        var = torch.exp(0.5 * var)
        epsilon = torch.randn_like(var)  # sampling epsilon        
        z = mean + var*epsilon                          # reparameterization trick
        return z
        
    def ResNet_build(self,in_channel,filter_nums,block_nums,stride=1,identity=False):
        build_model = []
        build_model.append(ResBlock(in_channel,filter_nums,stride,identity))
        for _ in range(1,block_nums):
            build_model.append(ResBlock(filter_nums,filter_nums,stride=1))
        return nn.Sequential(*build_model)
    def forward(self, x):
        encoder_inputs = x #[b,3,1280]
        encoder_inputs = encoder_inputs.permute(0,2,1)
        encoder_inputs,_ = self.lstm1(encoder_inputs)
        # encoder_inputs,_ = self.lstm1(x)
        encoder_inputs = encoder_inputs.permute(0,2,1)
        x = self.model(encoder_inputs)
        x1 = self.layer_1(x) # 
        x2 = self.layer_2(x1) # (320, 80)

        x3 = self.layer_3(x2) # (160, 40)
        x4 = self.layer_4(x3) # (160, 20)

        x4_1 = F.pad(x4,(7,8))
        z_mean = self.zmean(x4_1)
        z_log_var = self.zlogvar(x4_1)

        z = self.reparameterization(z_mean,z_log_var)

        x = self.de_layer_1(z)

        x = torch.cat([x,x4],1)
        x = self.de_layer_2(x)

        x = self.de_layer_3(x)

        x = torch.cat([x,x3],1)
        x = self.de_layer_4(x)

        x = torch.cat([x,x2],1)
        x = self.de_layer_5(x)

        x = torch.cat([x,x1],1)
        x = self.de_layer_6(x)

        x = self.de_layer_7(x)

        x = x.permute(0,2,1) 

        decoder_output,_ = self.lstm(x)
        decoder_output = self.lc(decoder_output)
        return z_mean, z_log_var, z, decoder_output
