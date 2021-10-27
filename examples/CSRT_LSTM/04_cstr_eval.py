import os
import time
import numpy as np
import torch
import matplotlib.pyplot as plt
from open_lstm import OpenLSTM
from diffutil.products import jvp, unflatten_like
from models import LSTMWrapper
from torchid import metrics


if __name__ == '__main__':

    # In[Set seed for reproducibility]
    np.random.seed(0)
    torch.manual_seed(0)

    # In[Settings]
    n_skip = 0 # skip initial n_skip samples for metrics (ignore transient)
    context = 25

    model_name = "lstm"
    # dataset_name = "transf"
    dataset_name = "eval"

    # In[Load dataset]
    u_new = torch.from_numpy(np.load(os.path.join("data", "cstr", f"u_{dataset_name}.npy")).astype(np.float32)[0, :, :])  # seq_len, input_size
    y_new = torch.from_numpy(np.load(os.path.join("data", "cstr", f"y_{dataset_name}.npy")).astype(np.float32)[0, :, :])  # seq_len, output_size

    # In[Check dimensions]
    batch_size = 1
    seq_len, input_size = u_new.shape
    seq_len_, output_size = y_new.shape
    assert(seq_len == seq_len_)

    n_inputs = u_new.shape[-1]

    # In[Load LSTM model]
    # Setup neural model structure and load fitted model parameters
    model = OpenLSTM(context, n_inputs)
    model_filename = f"{model_name}.pt"
    model.load_state_dict(torch.load(os.path.join("models", model_filename)))

    # In[Model wrapping]
    model_wrapped = LSTMWrapper(model, seq_len, input_size)
    """
    u_torch_new = torch.tensor(u_new, dtype=torch.float, requires_grad=False)
    y_torch_new = torch.tensor(y_new, dtype=torch.float)
    u_torch_new_f = torch.clone(u_torch_new.view((input_size * seq_len, 1)))  # [bsize*seq_len, n_in]
    y_torch_new_f = torch.clone(y_torch_new.view(output_size * seq_len, 1))  # [bsize*seq_len, ]
    """
    u = torch.unsqueeze(u_new, dim=0)
    y = torch.unsqueeze(y_new, dim=0)
    print("Input shape: ", y.shape, u.shape)

    u_torch_new = torch.cat((u[:, 1:, :], y[:, :-1, :]), -1)
    y_torch_new = y[:, 1:, :]

    # In[Load theta_lin]
    # theta_lin = np.zeros_like(theta_lin)
    theta_lin = np.load(os.path.join("models", "theta_lin_cf.npy"))  # closed-form
    # theta_lin = np.load(os.path.join("models", "theta_lin_gd.npy"))  # gradient descent
    # theta_lin = np.load(os.path.join("models", "theta_lin_lbfgs.npy"))  # L-BFGS
    theta_lin = torch.tensor(theta_lin)
    # In[Nominal model output]
    y_sim_new_f = model_wrapped(u_torch_new)
    print("Sizes: ", y_sim_new_f.size(), seq_len, output_size, theta_lin.size())
    y_sim_new = y_sim_new_f.reshape(seq_len-1, output_size).detach().numpy()
    # y_sim_new = torch.squeeze(y_sim_new_f).detach().numpy()

    # In[Linearized model output]
    theta_lin_f = unflatten_like(theta_lin, tensor_lst=list(model_wrapped.parameters()))
    time_jvp_start = time.time()
    y_lin_new_f = jvp(y_sim_new_f, model_wrapped.parameters(), theta_lin_f)[0]
    time_jvp = time.time() - time_jvp_start
    print(" y_lin_new_f ", y_lin_new_f.shape)
    y_lin_new = y_lin_new_f.reshape((seq_len-1), output_size).detach().numpy()

    # In[Plot]
    fig, ax = plt.subplots(2, 1, sharex=True)
    ax[0].plot(y_new[:, 0], 'k', label="True")
    ax[0].plot(y_sim_new[:, 0], 'r', label="Sim")
    ax[0].plot(y_lin_new[:, 0], 'b', label="Lin")
    ax[0].legend()

    ax[1].plot(y_new[:, 1], 'k')
    ax[1].plot(y_sim_new[:, 1], 'r')
    ax[1].plot(y_lin_new[:, 1], 'b')
    plt.show()

    # R-squared metrics
    R_sq_lin = metrics.r_squared(y_new[n_skip:, :], y_lin_new[n_skip:, :])
    print(f"R-squared linear model: {R_sq_lin}")

    R_sq_sim = metrics.r_squared(y_new[n_skip:, :], y_sim_new[n_skip:, :])
    print(f"R-squared nominal model: {R_sq_sim}")
