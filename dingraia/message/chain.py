from typing import Any, TypeVar, List

from .element import At

_T = TypeVar('_T')


class MessageChain:
    trace_id: str = None
    
    def __init__(self, *elements, at: list = None):
        self.mes = [s for s in list(elements)]
        self.display = ''.join([str(x) for x in self.mes])
        if at is not None:
            self.mes += [At(at_id) for at_id in at]
    
    def include(self, __obj: _T) -> List[_T]:
        return self.get(__obj)  # __class__([i for i in self.mes if isinstance(i, __obj)])
    
    def get_first(self, __obj: _T) -> _T:
        return self.get(__obj)[0]
    
    def get(self, element_class: type, count: int = -1) -> list:
        """
        获取消息链中所有特定类型的消息元素

        Args:
            element_class (type): 指定的消息元素的类型, 例如 "Plain", "At", "Image" 等.
            count (int, optional): 至多获取的元素个数

        Return
            list[E]: 获取到的符合要求的所有消息元素; 另: 可能是空列表([]).
        """
        if count == -1:
            count = len(self.mes)
        return [i for i in self.mes if isinstance(i, element_class)][:count]
    
    def __str__(self):
        return self.display
    
    def __getitem__(self, item: type) -> Any:
        if issubclass(item, type):
            return self.get(item)
        else:
            raise NotImplementedError("{0} 不能使用 getitem 方法".format(type(item)))
    
    def __add__(self, other):
        self.mes += other.mes
        self.display = ''.join([str(x) for x in self.mes])
        return self
    
    def __len__(self) -> int:
        return len(self.mes)
