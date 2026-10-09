import builtins, inspect
import navigation_controller
print('module',navigation_controller.__file__)
print('source',inspect.getsource(navigation_controller.NavigationController.__init__))
n=getattr(builtins,'_warehouse_navigation',None)
if n:
    print('controller',vars(n.controller))
    print('runner source',inspect.getsource(type(n).run)[:1800])
