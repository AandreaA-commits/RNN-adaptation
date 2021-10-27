import torch
import torch.nn as nn
import torch.optim as optim

class OpenLSTM(nn.Module):
    def __init__(self, n_context, n_inputs):
        super(OpenLSTM, self).__init__()
        self.n_context = n_context # 64
        self.model = nn.LSTM(input_size=2, hidden_size=16, proj_size=2, num_layers=1, batch_first=True)
        self.n_inputs = n_inputs

    def forward(self, u_train):
        y1, (hn, cn) = self.estimate_state(u_train[:, :, :self.n_inputs],
                                           u_train[:, :, self.n_inputs:], self.n_context)
        y2 = self.predict_state(u_train[:, :, :self.n_inputs],
                                u_train[:, :, self.n_inputs:], self.n_context, (hn, cn))
        y_sim = torch.cat((y1, y2), dim=1)
        return y_sim

    def estimate_state(self, u_train, y_train, nstep):
        y_est = []
        hn = torch.zeros(1, u_train.size()[0], 2).requires_grad_()
        cn = torch.zeros(1, u_train.size()[0], 16).requires_grad_()

        for i in range(nstep):
            # Feed in the known output to estimate state
            # Hidden state (hn) stores the previous output
            # For state estimation, we feed in the known output value
            out, (hn, cn) = self.model(u_train[:, i, :].unsqueeze(1),
                                       (y_train[:, i, :].view(hn.shape), cn))
            y_est.append(out)

        y_sim = torch.cat(y_est, dim=1)
        return y_sim, (hn, cn)

    def predict_state(self, u_train, y_train, nstep, state):
        y_sim, _ = self.model(u_train[:, nstep:, :], state)
        return y_sim

    def get_model(self):
        return self.model