# generated from rosidl_generator_py/resource/_idl.py.em
# with input from my_robot_wallinterfaces:msg/SelectionWall.idl
# generated code does not contain a copyright notice


# Import statements for member types

# Member 'picked_position'
# Member 'default_position'
import array  # noqa: E402, I100

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SelectionWall(type):
    """Metaclass of message 'SelectionWall'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('my_robot_wallinterfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'my_robot_wallinterfaces.msg.SelectionWall')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__selection_wall
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__selection_wall
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__selection_wall
            cls._TYPE_SUPPORT = module.type_support_msg__msg__selection_wall
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__selection_wall

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SelectionWall(metaclass=Metaclass_SelectionWall):
    """Message class 'SelectionWall'."""

    __slots__ = [
        '_wallselection',
        '_typeselection',
        '_sectionselection',
        '_picked_position',
        '_default_position',
    ]

    _fields_and_field_types = {
        'wallselection': 'string',
        'typeselection': 'string',
        'sectionselection': 'int32',
        'picked_position': 'sequence<int32>',
        'default_position': 'sequence<int32>',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('int32')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('int32')),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.wallselection = kwargs.get('wallselection', str())
        self.typeselection = kwargs.get('typeselection', str())
        self.sectionselection = kwargs.get('sectionselection', int())
        self.picked_position = array.array('i', kwargs.get('picked_position', []))
        self.default_position = array.array('i', kwargs.get('default_position', []))

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.wallselection != other.wallselection:
            return False
        if self.typeselection != other.typeselection:
            return False
        if self.sectionselection != other.sectionselection:
            return False
        if self.picked_position != other.picked_position:
            return False
        if self.default_position != other.default_position:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def wallselection(self):
        """Message field 'wallselection'."""
        return self._wallselection

    @wallselection.setter
    def wallselection(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'wallselection' field must be of type 'str'"
        self._wallselection = value

    @builtins.property
    def typeselection(self):
        """Message field 'typeselection'."""
        return self._typeselection

    @typeselection.setter
    def typeselection(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'typeselection' field must be of type 'str'"
        self._typeselection = value

    @builtins.property
    def sectionselection(self):
        """Message field 'sectionselection'."""
        return self._sectionselection

    @sectionselection.setter
    def sectionselection(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'sectionselection' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'sectionselection' field must be an integer in [-2147483648, 2147483647]"
        self._sectionselection = value

    @builtins.property
    def picked_position(self):
        """Message field 'picked_position'."""
        return self._picked_position

    @picked_position.setter
    def picked_position(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'i', \
                "The 'picked_position' array.array() must have the type code of 'i'"
            self._picked_position = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, int) for v in value) and
                 all(val >= -2147483648 and val < 2147483648 for val in value)), \
                "The 'picked_position' field must be a set or sequence and each value of type 'int' and each integer in [-2147483648, 2147483647]"
        self._picked_position = array.array('i', value)

    @builtins.property
    def default_position(self):
        """Message field 'default_position'."""
        return self._default_position

    @default_position.setter
    def default_position(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'i', \
                "The 'default_position' array.array() must have the type code of 'i'"
            self._default_position = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, int) for v in value) and
                 all(val >= -2147483648 and val < 2147483648 for val in value)), \
                "The 'default_position' field must be a set or sequence and each value of type 'int' and each integer in [-2147483648, 2147483647]"
        self._default_position = array.array('i', value)
