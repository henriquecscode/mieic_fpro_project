class MainClass:
    
    main = {}
    used = None
    def __init__(self):
        self.main['menu'] = MenuClass()
        self.main['game'] = ChildClass(self.fac)
        self.main['game'] = ChildClass(self.working_fac)
        self.used = self.main['game']
        
    def fac(self, name):
        def new_fac(name):
            self.used = self.main[name]
        return new_fac(name)
            
    def working_fac(self):
        self.used = self.main['menu']
            
class MenuClass:
    
    def __init__(self):
        pass
    
    def function(self):
        print('hello world')
  
    
class ChildClass:
    
    def __init__(self, fac):
        self.change = fac('menu')
        self.button = Button(fac('menu'))

        self.button = Button(fac)
        
class Button:
    
    def __init__(self,function):
        self.function = function
        
    def call(self):
        self.function()   
        
aclass = MainClass()
aclass.used.button.call()
aclass.used.function()