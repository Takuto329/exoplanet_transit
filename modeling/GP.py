#!/usr/bin/env python3
import GPy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

kernel = GPy.kern.RBF(1)
# kernel = GPy.kern.RBF(1) + GPy.kern.Bias(1) + GPy.kern.Linear(1)

d = pd.read_csv('http://kasugano.sakura.ne.jp/images/2016/20161112/data-GPbook-Fig2_05.txt')
model = GPy.models.GPRegression(d.X[:, None], d.Y[:, None], kernel=kernel)
model.optimize()
model.plot()
plt.savefig('output/fig2.png')
