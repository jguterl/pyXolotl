import glob
import os.path
import h5py
filename = '/home/guterlj/simulations/XOLOTL/onlyDtest/supertest/retentionOut.txt'

class classinstancemethod(classmethod):
    def __get__(self, instance, type_):
        descr_get = super().__get__ if instance is None else self.__func__.__get__
        return descr_get(instance, type_)

class XolotlPlot():
    def __init__(self, *args, **kwargs):
        self.data_files={'retention':'retentionOut.txt', 'surface':'surface.txt'}
        self.output = {}
        super(XolotlPlot, self).__init__(*args, **kwargs)
    
   
    @classinstancemethod     
    def plot_profiles(self):
        fig = plt.figure()
        ax = plt.subplot(111)
        data = self.output['profile']
        for k in [k for k in data.keys() if k!='depth' and k!='filename']:
            print(k)
            ax.plot(data['depth'], data[k], ls='-', lw=4, marker='.', markersize=10, alpha=0.5, label=k)

        
        ## Formatting
        ax.set_xlabel("Depth [nm]",fontsize=25)
        ax.set_ylabel("Concentration [atoms/nm3]",fontsize=25)
        ax.set_yscale('log')
        #plotDist.set_yscale('log')
        #plotDist.set_xlim([0.0, 1000.0])
        #plotDist.set_ylim([0.0, 0.15])
        #plotDist.grid()
        ax.legend()
        ax.tick_params(axis='both', which='major', labelsize=25)
        ax.tick_params(axis='both', which='minor', labelsize=25)
        return ax
    
    @classinstancemethod     
    def plot_retention(self,datatype=['bulk','burst','surface','content'],kw=None, **kwargs):
        if type(datatype) == str: datatype = [datatype]
        x,y=get_spdim(len(datatype))
        fig ,axes = plt.subplots(x,y)
        _axes = axes.flatten()
        for i,k in enumerate(datatype):
            getattr(self,'plot_{}'.format(k))(kw=kw,ax=_axes[i],**kwargs)
            
    @classinstancemethod     
    def _plot_vs_fluence(self, contents, ax,kw=None  ):
        
        if kw is None:
            kw = contents
        else:
            if type(kw)== str:
                kw = [kw]
        assert type(kw) == list
        assert all([k in contents for k in kw])
    
        data = self.output['retention']
        for k in contents:
            ax.plot(data['fluence'], data[k], ls='-', lw=4, marker='.', markersize=10, alpha=0.5, label=k)

    @classinstancemethod     
    def _plot_retention_data(self, datatype, kw=None, ax=None, yscale='linear' ,xscale='linear',units=''):
        species = ['Helium', 'Deuterium', 'Vacancy', 'Interstitial']
        contents =['{}_{}'.format(k,datatype) for k in species if not (k in ['Vacancy','Interstitial'] and datatype=='burst')]
        if ax is None:
            fig,_ax = plt.subplots(1)
        else:
            _ax = ax
        
        self._plot_vs_fluence(contents, _ax, kw)
        
    
    @classinstancemethod     
    def _plot_retention_data(self, datatype, kw=None, ax=None, yscale='linear' ,xscale='linear',units=''):
        species = ['Helium', 'Deuterium', 'Vacancy', 'Interstitial']
        contents =['{}_{}'.format(k,datatype) for k in species if not (k in ['Vacancy','Interstitial'] and datatype=='burst')]
        if ax is None:
            fig,_ax = plt.subplots(1)
        else:
            _ax = ax
        
        self._plot_vs_fluence(contents, _ax, kw)

        
        ## Formatting
        _ax.set_ylabel('{} [{}]'.format(datatype,units))
        _ax.set_yscale(yscale)
        _ax.set_xscale('symlog')
        #plotDist.set_yscale('log')
        #plotDist.set_xlim([0.0, 1000.0])
        #plotDist.set_ylim([0.0, 0.15])
        #plotDist.grid()
        _ax.legend()
        #ax.tick_params(axis='both', which='major', labelsize=25)
        #ax.tick_params(axis='both', which='minor', labelsize=25)
        setattr(self,'ax_{}'.format(datatype),_ax)
        
    @classinstancemethod     
    def plot_bulk(self, kw=None, ax=None, **kwargs):
        self._plot_retention_data('bulk', kw, ax, **kwargs)
        
    @classinstancemethod     
    def plot_burst(self, kw=None, ax=None, **kwargs):
        self._plot_retention_data('burst', kw, ax, **kwargs)
        
    @classinstancemethod     
    def plot_surface(self, kw=None, ax=None, **kwargs):
        self._plot_retention_data('surface', kw, ax, **kwargs)
        
    @classinstancemethod     
    def plot_content(self, kw=None, ax=None, **kwargs):
        self._plot_retention_data('content', kw, ax, **kwargs)
        
    @classinstancemethod     
    def plot_flux(self, kw=None, ax=None, **kwargs):
        self._plot_retention_data('content', kw, ax, **kwargs)
        
        
        
    
            

    
    
def get_spdim(nplots):
    cols = int(ceil(sqrt(nplots)))
    rows = int(ceil(nplots / cols))
    return rows,cols