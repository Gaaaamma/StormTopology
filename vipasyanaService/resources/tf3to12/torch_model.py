import torch
from scipy import signal
from resnet18VAE import ResBlock,Res_VAE
import numpy as np 
import sys
class Model3to12():
    def __init__(self,args):
        self.args=args
        self.lead9 = [0,1,3,6,7,8,9,10,11]
        self.model = Res_VAE(layers_dims=[2,2,2,2], en_channels=[160,160,160, 80, 40]).to(args.device)
        self.loadVae()
        
    def loadVae(self):
        self.model.load_state_dict(torch.load(self.args.parameters,map_location=torch.device(self.args.device)),strict=False)
        # self.transfer(np.random.rand(1,1280,3))
        print(f'model parameters: {self.args.parameters}', file=sys.stderr)
        
    def transfer(self,inf_in):
        '''
        input : inf_in [N,1280,3]
        output : inf_in [N,1280,9]
        '''
        inf_in = torch.tensor(inf_in,dtype=torch.float32).to(self.args.device)
        inf_in = inf_in.permute(0,2,1)
        z_mean, z_log_var, z, output = self.model(inf_in) #[N,1280,12]
        output = output[:,:,self.lead9]
        Data_output = output.detach().cpu().numpy()
        return Data_output