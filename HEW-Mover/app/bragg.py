import numpy as np
from scipy import interpolate
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

class Bragg():
    def __init__(self, crystal, hkl1=111, hkl2=333, energy=8):
        self.energy = energy
        self.wl = l2e(self.energy)
        self.crystal = crystal
        #print(hkl1)
        #print(sum([int(i)**2 for i in str(hkl1)]))
        self.hkl1 = sum([int(i)**2 for i in str(hkl1)])
        self.hkl2 = sum([int(i)**2 for i in str(hkl2)])
        #print(self.hkl1)
        #print(self.hkl2)
        self.choose_cal(self.crystal)
    def choose_cal(self, crystal):
        if crystal == 'Si':
            self.xtal = 5.4307
            self.a1 = 5.663
            self.a2 = 3.072
            self.a3 = 2.625
            self.a4 = 1.393
            self.b1 = 2.665
            self.b2 = 38.663
            self.b3 = 0.9169
            self.b4 = 93.546
            self.c1 = 1.247
            self.crystal = 'Si'
        if crystal == 'Ge':
            self.xtal = 5.65685
            self.a1 = 16.082
            self.a2 = 6.375
            self.a3 = 3.707
            self.a4 = 3.683
            self.b1 = 2.851
            self.b2 = 0.2516
            self.b3 = 11.447
            self.b4 = 54.763
            self.c1 = 2.131
            self.crystal = 'Ge'
        if crystal == 'Graphite':
            self.xtal = 6.708
            self.crystal = 'Graphite'

    def fit_wl(self, th1, th2):
        th1 *= np.pi/180.0
        th2 *= np.pi/180.0
        d1 = self.xtal/np.sqrt(self.hkl1)
        d2 = self.xtal/np.sqrt(self.hkl2)
        dt = (d2/d1 - np.cos(th1-th2))/np.sin(th1-th2)
        df = np.sqrt(1+dt**2)
        wl = 2*d2/df
        return wl
    def l2e(self, wl):
        return 12.39842/wl
    def tth_q(tth, wl):
        return 4*np.pi/wl*sin(tth*np.pi/360.0)
    def q_tth(q, wl):
        return 2*np.arcsin(wl*q/(4*np.pi))*180/np.pi
    def offset(self, th1, th2):
        th1 *= np.pi/180.0
        th2 *= np.pi/180.0
        d1 = self.xtal/np.sqrt(self.hkl1)
        d2 = self.xtal/np.sqrt(self.hkl2)
        dt = (d2/d1 - np.cos(th1-th2))/np.sin(th1-th2)
        df = np.sqrt(1+dt**2)
        wl = 2*d2/df
        ang1 = np.arcsin(wl/(2*d1))
        ang2 = np.arcsin(wl/(2*d2))
        offs = 180/np.pi*((th1+th2)-(ang1+ang2))/2.0
        return offs

    def cal_energy(self, th1, th2):
        self.wl = self.fit_wl(th1, th2)
        self.energy = l2e(self.wl)

    def calc_th_tth(self, dspace):
        th = np.arcsin(self.wl/2/dspace)*180/np.pi
        return th, 2*th

    def struct(self, ang, wl):
        stc = self.a1*np.exp(-self.b1*np.sin((np.pi/180.0*ang)**2)/wl**2)
        stc += self.a2*np.exp(-self.b2*np.sin((np.pi/180.0*ang)**2)/wl**2)
        stc += self.a3*np.exp(-self.b3*np.sin((np.pi/180.0*ang)**2)/wl**2)
        stc += self.a4*np.exp(-self.b4*np.sin((np.pi/180.0*ang)**2)/wl**2)
        stc += self.c1
        #print(stc*4*np.sqrt(2))
        return stc*4*np.sqrt(2)

    def darwin(self, wl, ang, struc):
        dw = 0.00001794*wl**2*struc/(self.xtal**3*np.sin(2*np.pi/180.0*ang))
        #print(dw)
        return dw#/0.00000485
    def delE(self, wl, ang1, ang2, fw1, fw2, ):
        wd = (fw2**2-fw1**2)*(np.pi/180)**2
        #print(wd)
        dd = -self.darwin(wl, ang1, self.struct(ang1, wl))**2 +\
            self.darwin(wl, ang2, self.struct(ang2, wl))**2
        #print(dd)
        td = (np.tan(np.pi/180.0*ang2))**2 - (np.tan(np.pi/180.0*ang1))**2
        #print(td)
        dE = np.sqrt(abs((wd-dd)/td))*self.l2e(wl)
        return dE
    def divergance(self, ang1, ang2, fw1, fw2, wl):
        dar1 = self.darwin(wl, ang1, self.struct(ang1, wl))**2
        dar2 = self.darwin(wl, ang2, self.struct(ang2, wl))**2
        del1 = ((fw2*np.pi/180)**2 - dar2)*(np.tan(np.pi/180.0*ang1))**2 -\
                ((fw1*np.pi/180)**2 - dar1)*(np.tan(np.pi/180.0*ang2))**2
        delm = np.sqrt(abs(del1/((np.tan(np.pi/180.0*ang1))**2 -\
                (np.tan(np.pi/180.0*ang2))**2)))
        return delm




def l2e(wl):
    return 12.39842/wl
def tth_q(tth, wl):
    return 4*np.pi/wl*np.sin(tth*np.pi/360.0)
def q_tth(q, wl):
    return 2*np.arcsin(wl*q/(4*np.pi))*180/np.pi

class Attenuation():
    def __init__(self, element, energy, thickness=100):
        self.element = element
        self.energy = energy
        self.thick = thickness

        self.choose_element()
        #self.calc_attenuation

    def choose_element(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        if self.element == 'Cu':
            self.table = np.loadtxt(dir_path+'/../data/Cu_linatten.txt')
        if self.element == 'Al':
            self.table = np.loadtxt(dir_path+'/../data/Al_linatten.txt')
        if self.element == 'Pb':
            self.table = np.loadtxt(dir_path+'/../data/Pb_linatten.txt')
        #print(self.element)
        #self.attenuation = interpolate.interp1d(self.table[:,0], self.table[:,1])

    def calc_attenuation(self):
        x = float(self.thick/100)
        #print(x)
        f = interpolate.interp1d(self.table[:,0],\
                                np.exp(-self.table[:,1]*0.01))
        #print(f(self.energy))
        return float(f(self.energy))**x
