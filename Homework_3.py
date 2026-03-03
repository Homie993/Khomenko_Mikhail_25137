import warnings
from functools import wraps

#4
def wraps_1(f1):
    
    def decorator(f):
        
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        wrapper.name = f1.name
        wrapper.doc = f1.doc
        wrapper.module = f1.module
        return wrapper
        
    return decorator
        
    

#3
def mock(return_value):
    def mock_lol(f):
        @wraps_1(f)
        def wrapper(*args, **kwargs):
            print(return_value)
        
        return wrapper
    return mock_lol
    

#1, 2
def deprecated_v2(text):
    def deprecated(f):
        @wraps_1(f)
        def wrapper(*args, **kwargs):
            warnings.warn(text)
            return f(*args, **kwargs)
            
        return wrapper
    return deprecated

    
@deprecated_v2("Pepe")
@mock(return_value = "Net")
def f(x: int):
    "Это функция y = x"
    return x
    

#5
class singledispatch_1:
    
    def init(self, f):
        self.func_dict = {}
        self.func = f
    
    def register(self, f):
        first_type = next(iter(f.annotations.values()))
        if first_type.name not in self.func_dict:
            self.func_dict[first_type.name] = f
                
        return f
    
    def call(self, *args, **kwargs):
        if (type(args[0]).name in self.func_dict):
            exit = self.func_dict[type(args[0]).name]
            return exit(*args, **kwargs)
        else:
            return self.func(*args, **kwargs)
    
    

def singledispatch(f):
    wrapper = singledispatch_1(f)
    wrapper.name = f.name
    wrapper.doc = f.doc
    wrapper.module = f.module
    
    return wrapper


@singledispatch
def func(x):
    print(x, " im not implemented!!")
    
@func.register
def _(x: int):
    print(x, " im int")
    
    
@func.register
def _(x: str):
    print(x, " im string")
    

func(1)
func("abra")
func([])