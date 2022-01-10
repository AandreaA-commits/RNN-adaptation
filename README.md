# On the adaptation of recurrent neural networks for system identification

This repository contains the Python code to reproduce the results
of the paper [On the adaptation of recurrent neural networks for system identification](https://arxiv.org/pdf/2006.02250.pdf) by Marco Forgione, Marco Gallieri, Aneri Muni, and Dario Piga.


We introduce a **transfer learning** approach which enables fast and efficient adaptation
of Recurrent Neural Network models. A nominal RNN model is first identified using available measurements.
The system dynamics are then assumed to change, leading to an unacceptable degradation of the nominal model performance  on the perturbed system.

To cope with the  mismatch, the model is augmented  with an additive correction term trained on fresh data from the new dynamic regime.
The correction term is learned through a **Bayesian Linear Regression** (BLR) method defined
in terms of the features spanned by the nominal model's **Jacobian** with respect to its parameters.

A **non-parametric view** of the approach is also proposed, which extends recent work on **Gaussian Process**  with Neural Tangent Kernel (NTK-GP) [1] to the RNN case (RNTK-GP). 

# Folders:
* [examples](examples): examples transfer learning with
  * [CSTR reactor](examples/CSTR)
  * [Non-linear RLC circuit](examples/RLC)
  * [Wiener-Hammerstein system](examples/WH) (not discussed in the paper)
* [diffutil](diffutil): computation of:
  * full parameter Jacobians matrix in [jacobian.py](diffutil/jacobian.py)
  * Jacobian-vector / transposed Jacobian-vector products in [products.py](diffutil/products.py)
* [torchid](torchid):  system identification tools with PyTorch. Copied from https://github.com/forgi86/pytorch-ident


# Software requirements:
Simulations were performed on a Python 3.8 conda environment with

 * numpy
 * matplotlib
 * pandas
 * pytorch (version 1.8.1)
 
These dependencies may be installed through the commands:

```
conda install numpy scipy pandas matplotlib
conda install pytorch torchvision cudatoolkit=10.2 -c pytorch
```

# Citing

If you find this project useful, we encourage you to

* Star this repository :star: 
* Cite the [paper](https://onlinelibrary.wiley.com/doi/abs/10.1002/acs.3216) 

To cite the paper, you may use the following BibTex entry:
```
@article{forgione2022adapt,
  title={On the adaptation of recurrent neural networks for system identification},
  author={Forgione, M. and Muni, A. and Gallieri, M. and Piga, D.},
  journal={arXiv e-prints},
  year={2022}
}
```

Using the IEEEtran bibliography style, it should look like:

M. Forgione, A. Muni, M. Gallieri, and D. Piga, "On the adaptation of recurrent neural networks for system identification,"
*arXiv preprint arXiv:XXXX.YYYY*, 2022. <br/><br/>

# Bibliograby
[1] W. Maddox, S. Tang, P. Moreno, A. Wilson, and A. Damianou, "Fast Adaptation with Linearized Neural Networks",  
in *Proc. of the International Conference on Artificial Intelligence and Statistics*, 2021. <br/><br/>
