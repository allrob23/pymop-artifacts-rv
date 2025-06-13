from pythonmop import SpecParameter, call, getter, setter, deleter, target_param, ret_param, BaseInstrumentTarget, \
    BaseParameterDeclaration


def test_SpecParameter_creation():
    # Arrange
    param_id = 0
    param_type = int

    # Act
    param = SpecParameter(id=param_id, param_type=param_type)

    # Assert
    assert param.id == param_id
    assert param.param_type == param_type

def test_BaseInstrumentTarget_creation():
    # Arrange
    namespace = "module_name"
    field = "function_name"

    # Act
    instrument_target = BaseInstrumentTarget(namespace=namespace, field=field)

    # Assert
    assert instrument_target.namespace == namespace
    assert instrument_target.field == field

def test_call_creation():
    # Arrange
    namespace = "module_name"
    field = "function_name"

    # Act
    call_target = call(namespace=namespace, field=field)

    # Assert
    assert isinstance(call_target, BaseInstrumentTarget)
    assert call_target.namespace == namespace
    assert call_target.field == field


def test_BaseParameterDeclaration_creation():
    # Arrange
    param = SpecParameter(id=0, param_type=int)

    # Act
    param_decl = BaseParameterDeclaration(param=param)

    # Assert
    assert param_decl.param == param

def test_target_param_creation():
    # Arrange
    param = SpecParameter(id=0, param_type=int)

    # Act
    target_param_decl = target_param(param=param)

    # Assert
    assert isinstance(target_param_decl, BaseParameterDeclaration)
    assert target_param_decl.param == param


