from typing import List, Type, Any, TypeVar, Tuple, Dict, Optional, Set, Protocol
import sys
import inspect
import logging
import importlib
from abc import ABC, abstractmethod
import os

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ITypeFinder(Protocol):
    """Interface for finding types in modules."""
    
    def find_classes_of_type(self, assignable_to_type: Type[T], only_concrete: bool = True) -> List[Type[T]]:
        """
        Find classes that implement the specified type.
        
        Args:
            assignable_to_type: The type to find implementations of
            only_concrete: If True, only return concrete (non-abstract) classes
            
        Returns:
            List of discovered types
        """
        ...
        
    def find_generic_implementations(self, generic_type: Type, arg_types: Optional[List[Type]] = None) -> List[Tuple[Type, List[Type]]]:
        """
        Find implementations of a generic interface with their type arguments.
        
        Args:
            generic_type: The generic interface type (e.g., IRepository)
            arg_types: Optional list of types to filter by
            
        Returns:
            List of tuples containing (implementation_type, [type_args])
        """
        ...

class TypeFinder(ITypeFinder):
    """
    Implementation of ITypeFinder that scans loaded modules to find types.
    This is the Python equivalent of NopCommerce's AppDomainTypeFinder.
    """
    
    def __init__(self, ignore_modules: Optional[List[str]] = None):
        """
        Initialize the TypeFinder.
        
        Args:
            ignore_modules: List of module names to ignore (e.g., ['builtins', 'typing'])
        """
        self._ignore_modules = ignore_modules or ['builtins', 'typing', 'collections', 'abc', 'asyncio', 'ctypes', 'concurrent', 'multiprocessing']
        self._loaded_modules: Dict[str, Any] = {}
        self._scan_loaded_modules()

    def _is_likely_startup_module(self, module_name: str) -> bool:
        """
        Check if a module is likely to contain startup tasks.
        
        Args:
            module_name: The name of the module to check
            
        Returns:
            True if the module is likely to contain startup tasks
        """
        # Skip test modules
        if 'test_' in module_name or '_test' in module_name:
            return False
            
        # Skip all example modules - they should not be loaded for startup tasks
        if 'example' in module_name:
            return False
            
        # Skip modules that are clearly not startup-related
        skip_patterns = ['__init__', 'conftest', 'setup', 'build', 'dist', 'egg-info', '__version__', 'cli']
        if any(pattern in module_name for pattern in skip_patterns):
            return False
            
        # Only load modules from specific packages that are likely to contain startup tasks
        startup_packages = [
            'openbiocure_corelib.core',
            'openbiocure_corelib.data'
        ]
        
        return any(module_name.startswith(pkg) for pkg in startup_packages)
    
    def _scan_loaded_modules(self) -> None:
        """Scan all loaded modules and cache them for faster lookups."""
        # First scan sys.modules
        for module_name, module in list(sys.modules.items()):
            # Skip modules that we can't inspect or should ignore
            if not module or not hasattr(module, "__dict__") or any(module_name.startswith(m) for m in self._ignore_modules):
                continue
            
            self._loaded_modules[module_name] = module
        
        # Get all Python paths
        python_paths = sys.path
        
        # Scan each Python path for Python files
        for path in python_paths:
            if not os.path.exists(path):
                continue
                
            for root, _, files in os.walk(path):
                for file in files:
                    if not file.endswith('.py'):
                        continue
                        
                    # Convert file path to module name
                    try:
                        # Get the relative path from the Python path
                        rel_path = os.path.relpath(os.path.join(root, file), path)
                        module_name = rel_path.replace(os.sep, '.').replace('.py', '')
                        
                        # Skip if already loaded or should be ignored
                        if module_name in self._loaded_modules or any(module_name.startswith(m) for m in self._ignore_modules):
                            continue
                            
                        # Skip modules that are unlikely to contain startup tasks
                        if not self._is_likely_startup_module(module_name):
                            continue
                        
                        # Try to import the module
                        try:
                            # First ensure the package is imported
                            package_name = module_name.split('.')[0]
                            if package_name not in sys.modules:
                                importlib.import_module(package_name)
                            
                            # Then import the specific module
                            module = importlib.import_module(module_name)
                            self._loaded_modules[module_name] = module
                            logger.debug(f"Loaded module: {module_name}")
                        except ImportError as e:
                            logger.debug(f"Failed to load module {module_name}: {str(e)}")
                    except ValueError:
                        # Skip if the file is not relative to the Python path
                        continue
    
    def load_module(self, module_name: str) -> None:
        """
        Load a module by name and add it to the cached modules.
        
        Args:
            module_name: The name of the module to load
        """
        try:
            module = importlib.import_module(module_name)
            self._loaded_modules[module_name] = module
            logger.debug(f"Loaded module: {module_name}")
        except ImportError as e:
            logger.warning(f"Failed to load module {module_name}: {str(e)}")
    
    def find_classes_of_type(self, assignable_to_type: Type[T], only_concrete: bool = True) -> List[Type[T]]:
        """
        Find classes that implement the specified type by scanning loaded modules.
        
        Args:
            assignable_to_type: The type to find implementations of
            only_concrete: If True, only return concrete (non-abstract) classes
            
        Returns:
            List of discovered types
        """
        result: List[Type[T]] = []
        discovered_types: Set[Type] = set()
        
        logger.info(f"Searching for classes assignable to {assignable_to_type.__name__}")
        logger.info(f"Total loaded modules: {len(self._loaded_modules)}")
        logger.info(f"Ignored module prefixes: {self._ignore_modules}")
        
        # Scan all cached modules
        for module_name, module in self._loaded_modules.items():
            try:
                # Find all classes in the module
                module_classes = list(inspect.getmembers(module, inspect.isclass))
                logger.debug(f"Module {module_name} has {len(module_classes)} classes")
                
                for _, class_obj in module_classes:
                    # Skip if we've already processed this class
                    if class_obj in discovered_types:
                        continue
                    
                    discovered_types.add(class_obj)
                    
                    # Skip classes from ignored modules
                    if any(class_obj.__module__.startswith(m) for m in self._ignore_modules):
                        logger.debug(f"Skipping {class_obj.__name__} from ignored module {class_obj.__module__}")
                        continue
                    
                    # Check if it's an implementation of the target type
                    try:
                        is_assignable = self._is_assignable_to(class_obj, assignable_to_type)
                    except Exception as assign_err:
                        logger.warning(f"Error checking assignability for {class_obj.__name__}: {assign_err}")
                        continue
                    
                    if is_assignable:
                        # Check if we should skip abstract classes
                        if only_concrete and (inspect.isabstract(class_obj) or ABC in class_obj.__bases__):
                            logger.debug(f"Skipping abstract class {class_obj.__name__}")
                            continue
                        
                        logger.info(f"Found assignable class: {class_obj.__name__} from module {class_obj.__module__}")
                        result.append(class_obj)
            except Exception as e:
                logger.error(f"Error scanning module {module_name}: {str(e)}", exc_info=True)
        
        logger.info(f"Total classes found: {len(result)}")
        logger.info(f"Found classes: {[cls.__name__ for cls in result]}")
        
        return result
    
    def find_generic_implementations(self, generic_type: Type, arg_types: Optional[List[Type]] = None) -> List[Tuple[Type, List[Type]]]:
        """
        Find implementations of a generic interface with their type arguments.
        For example, find all IRepository[SomeEntity] implementations.
        
        Args:
            generic_type: The generic interface type (e.g., IRepository)
            arg_types: Optional list of types to filter by (e.g., only find IRepository[Todo])
            
        Returns:
            List of tuples containing (implementation_type, [type_args])
        """
        result: List[Tuple[Type, List[Type]]] = []
        discovered_types: Set[Type] = set()
        
        # Scan all cached modules
        for module_name, module in self._loaded_modules.items():
            try:
                # Find all classes in the module
                for _, class_obj in inspect.getmembers(module, inspect.isclass):
                    # Skip if we've already processed this class
                    if class_obj in discovered_types:
                        continue
                    
                    discovered_types.add(class_obj)
                    
                    # Skip classes from ignored modules
                    if any(class_obj.__module__.startswith(m) for m in self._ignore_modules):
                        continue
                    
                    # Check if class implements the generic interface
                    if hasattr(class_obj, "__orig_bases__"):
                        for base in class_obj.__orig_bases__:
                            if (hasattr(base, "__origin__") and 
                                base.__origin__ is generic_type and 
                                hasattr(base, "__args__")):
                                
                                type_args = list(base.__args__)
                                
                                # If arg_types is specified, check if this class uses those types
                                if arg_types:
                                    if not all(arg in type_args for arg in arg_types):
                                        continue
                                
                                result.append((class_obj, type_args))
                                break
            except Exception as e:
                logger.debug(f"Error scanning module {module_name} for generic implementations: {str(e)}")
        
        return result
    
    def _is_assignable_to(self, class_obj: Type, target_type: Type) -> bool:
        """
        Check if a class is assignable to a target type.
        This is the Python equivalent of C#'s IsAssignableFrom.
        
        Args:
            class_obj: The class to check
            target_type: The target type to check against
            
        Returns:
            True if class_obj is assignable to target_type, False otherwise
        """
        # Handle Protocol types (structural typing)
        if hasattr(target_type, '_is_protocol') and target_type._is_protocol:
            # For protocols, we need to check if the class has all the required methods/attributes
            protocol_attrs = {
                attr for attr in dir(target_type) 
                if not attr.startswith('_') or attr == '__call__'
            }
            class_attrs = set(dir(class_obj))
            return protocol_attrs.issubset(class_attrs)
        
        # Handle regular inheritance
        try:
            return issubclass(class_obj, target_type)
        except TypeError:
            return False 