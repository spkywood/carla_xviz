from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#定义坐标轴
# fig = plt.figure()
# ax1 = plt.axes(projection='3d')
#ax = fig.add_subplot(111,projection='3d')  #这种方法也可以画多个子图


#方法二，利用三维轴方法
# from matplotlib import pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

#定义图像和三维格式坐标轴
fig=plt.figure()
ax1 = Axes3D(fig)

import numpy as np

x1, y1, z1 = (-66.4684601, 56.4365044, 0)
x2, y2, z2 = (-68.469, 56.4573402, 0)
x3, y3, z3 = (-68.4325485, 59.9571495, 0)
x4, y4, z4 = (-66.4320068, 59.9363136, 0)

z = np.linspace(0,13,1000)
x = 5*np.sin(z)
y = 5*np.cos(z)
zd = 13*np.random.random(100)
xd = 5*np.sin(zd)
yd = 5*np.cos(zd)
ax1.scatter3D(xd, yd, zd, cmap='Blues')  #绘制散点图
ax1.scatter3D(x1, y1, z1, cmap='Blues')  #绘制散点图
ax1.scatter3D(x2, y2, z2, cmap='Blues')  #绘制散点图
ax1.scatter3D(x3, y3, z3, cmap='Blues')  #绘制散点图
ax1.scatter3D(x4, y4, z4, cmap='Blues')  #绘制散点图
ax1.plot3D(x,y,z,'gray')    #绘制空间曲线
plt.show()