import torch
import pandas as pd
import numpy as np
import os
from torchid.module.lti import SisoLinearDynamicalOperator
import matplotlib.pyplot as plt
import time
import functools
from util.extract_util import extract_weights, load_weights, f_par_mod_in


if __name__ == '__main__':

    # In[Set seed for reproducibility]
    np.random.seed(0)
    torch.manual_seed(0)

    # In[Settings]
    model_name = 'IIR'
    n_b = 2
    n_a = 2

    # In[Column names in the dataset]
    COL_T = ['time']
    COL_X = ['V_C', 'I_L']
    COL_U = ['V_IN']
    COL_Y = ['V_C']

    # In[Load dataset]
    df_X = pd.read_csv(os.path.join("data", "RLC_data_test.csv"))
    t = np.array(df_X[COL_T], dtype=np.float32)
    y = np.array(df_X[COL_Y], dtype=np.float32)
    x = np.array(df_X[COL_X], dtype=np.float32)
    u = np.array(df_X[COL_U], dtype=np.float32)

    # In[Output]
    y = np.copy(x[:, [0]])

    # Prepare data
    u_torch = torch.tensor(u[None, ...], dtype=torch.float, requires_grad=False)

    # In[Second-order dynamical system custom defined]
    G = SisoLinearDynamicalOperator(n_b, n_a)
    model_folder = os.path.join("models", model_name)
    G.load_state_dict(torch.load(os.path.join(model_folder, "G.pt")))

    # In[Parameter Jacobians]
    sim_y = G(u_torch)
    N_load = u_torch.numel()

    # extract the parameters from the model in order to be able to take jacobians using the convenient functional API
    # see the discussion in https://discuss.pytorch.org/t/get-gradient-and-jacobian-wrt-the-parameters/98240
    params, names = extract_weights(G)
    params_dict = dict(zip(names, params))
    n_param = sum(map(torch.numel, params))
    scalar_names = [f"{name}_{pos}" for name in params_dict for pos in range(params_dict[name].numel())]
    # [f"{names[i]}_{j}" for i in range(len(names)) for j in range(params[i].numel())]

    # from Pytorch module to function of the module parameters only
    f_par = functools.partial(f_par_mod_in, param_names=names, module=G, inputs=u_torch)
    f_par(*params)

    jacs = torch.autograd.functional.jacobian(f_par, params)
    jac_dict = dict(zip(names, jacs))

    with torch.no_grad():
        y_out_1d = torch.ravel(sim_y).detach().numpy()
        params_1d = list(map(torch.ravel, params))
        theta = torch.cat(params_1d, axis=0).detach().numpy()  # parameters concatenated
        jacs_2d = list(map(lambda x: x.reshape(N_load, -1), jacs))
        J = torch.cat(jacs_2d, dim=-1).detach().numpy()

    # Adaptation in parameter space
    sigma = 0.1
    Ip = np.eye(n_param)
    F = J.transpose() @ J
    P_est = sigma*np.linalg.inv(F)
    A = F + sigma * Ip
    theta_lin = np.linalg.solve(A, J.transpose() @ y_out_1d)
    np.save(os.path.join("models", model_name, "theta_lin.npy"), theta_lin)


