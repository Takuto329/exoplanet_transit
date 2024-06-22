#!/usr/bin/env python3
import GPy
#ガウス過程に用いるカーネルの設定
kernel = GPy.kern.RBF(input_dim=1, variance=1., lengthscale=1.)
#モデルの設定
m = GPy.models.GPRegression(X,y,kernel)
#matplotlib出力
GPy.plotting.change_plotting_library('matplotlib')
m.plot()
plt.xlim(-5,5)
plt.ylim(-5,5)
plt.show()