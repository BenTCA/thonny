import tkinter as tk
from tkinter import ttk

from thonny.config_ui import ConfigurationPage
from thonny.globals import get_workbench, get_runner
from thonny.ui_utils import create_string_var
from thonny import workbench
from thonny.shared.thonny import backend

class OnlyTextConfigurationPage(ConfigurationPage):
    def __init__(self, master, text):
        ConfigurationPage.__init__(self, master)
        label = ttk.Label(self, text=text)
        label.grid()

class BackendConfigurationPage(ConfigurationPage):
    
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        
        self._backend_specs_by_desc = {spec.description : spec 
                                       for spec in get_workbench().get_backends().values()}
        self._conf_pages = {}
        self._current_page = None
        
        current_backend_name = get_workbench().get_option("run.backend_name")
        try:
            current_backend_desc = get_workbench().get_backends()[current_backend_name].description
        except ValueError:
            current_backend_desc = ""
            
        self._combo_variable = create_string_var(current_backend_desc)
        
        label = ttk.Label(self, text="Where should Thonny run your code?")
        label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self._combo = ttk.Combobox(self,
                              exportselection=False,
                              textvariable=self._combo_variable,
                              values=sorted(self._backend_specs_by_desc.keys()))
        
        self._combo.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=(0,10))
        self._combo.state(['!disabled', 'readonly'])
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        self._combo_variable.trace("w", self._backend_changed)
    
    def _backend_changed(self, *args):
        backend_desc = self._combo_variable.get()
        page = self._get_conf_page(backend_desc)
        
        if page != self._current_page:
            
            if self._current_page is not None:
                print("forgetting", self._current_page)
                self._current_page.grid_forget()
            
            print("gridding", page)
            page.grid(row=2, column=0, sticky="nsew")
            self._current_page = page
    
    def _get_conf_page(self, backend_desc):
        if backend_desc not in self._conf_pages:
            cp_constructor = self._backend_specs_by_desc[backend_desc].config_page_constructor
            if isinstance(cp_constructor, str):
                self._conf_pages[backend_desc] = OnlyTextConfigurationPage(self, cp_constructor)
            else:
                assert issubclass(cp_constructor, ConfigurationPage)
                self._conf_pages[backend_desc] = cp_constructor(self)
        
        return self._conf_pages[backend_desc]
    
    def apply(self):
        if not self._combo_variable.modified or self._current_page is None:
            return
        
        elif self._current_page.apply() is False:
            return False 
        
        else:
            backend_desc = self._combo_variable.get()
            backend_name = self._backend_specs_by_desc[backend_desc].name
            get_workbench().set_option("run.backend_name", backend_name)
            # TODO: Should it reset serial device or just connect to it?
            get_runner().reset_backend()
        
    

def load_plugin():
    get_workbench().add_configuration_page("Back-end", BackendConfigurationPage)
