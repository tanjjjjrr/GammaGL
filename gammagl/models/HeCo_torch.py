import numpy as np
import tensorlayerx as tlx
import tensorlayerx.nn as nn
from layers.attention.HeCo_encoder import Mp_encoder
from layers.attention.HeCo_encoder import Sc_encoder
from Contrast_learning_heco.contrast_for_torch import Contrast_for_torch

class ggl_HeCo_for_torch(nn.Module):
    def __init__(self, hidden_dim, feats_dim_list, feat_drop, attn_drop, P, sample_rate,
                 nei_num):
        super(ggl_HeCo_for_torch, self).__init__()
        self.hidden_dim = hidden_dim
        self.fc_list = nn.ModuleList([nn.Linear(in_features=feats_dim, out_features=hidden_dim, W_init='xavier_normal'
                                                ,b_init = 'constant') 
                                      for feats_dim in feats_dim_list])
        if feat_drop > 0:
            self.feat_drop = nn.Dropout(feat_drop)
        else:
            self.feat_drop = lambda x: x
        self.mp = Mp_encoder(P, hidden_dim, attn_drop)
        self.sc = Sc_encoder(hidden_dim, sample_rate, nei_num, attn_drop)
    def forward(self, datas, pos):  
        feats = datas.get("feats")
        mps = datas.get("mps")
        nei_index = datas.get("nei_index")
        h_all = []
        for i in range(len(feats)):
            h_all.append(tlx.elu(self.feat_drop(self.fc_list[i](feats[i]))))        
        z_mp = self.mp(h_all[0], mps)
        z_sc = self.sc(h_all, nei_index)
        z= {
            "z_mp": z_mp,
            "z_sc": z_sc,
        }
        return z

    def get_embeds(self, feats, mps):
        z_mp = tlx.elu(self.fc_list[0](feats[0]))
        z_mp = self.mp(z_mp, mps)
        return z_mp
