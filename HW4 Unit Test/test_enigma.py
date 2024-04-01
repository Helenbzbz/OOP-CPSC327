from components import Rotor, Reflector, Plugboard

## Test Rotor class
def test_rotor_init_valid():
    # Test valid rotor initialization
    rotor = Rotor('I', 'A')
    assert rotor.rotor_num == 'I' and rotor.window == 'A', "Rotor initialization with valid parameters failed."

def test_rotor_init_invalid():
    # Test initialization with invalid rotor number
    try:
        Rotor('X', 'A')
        assert False, "Rotor initialization should have failed with an invalid rotor number."
    except ValueError as e:
        assert str(e) == 'Please select I, II, III, or V for your rotor number and provide the initial window setting (i.e. the letter on the wheel initially visible to the operator.'

def test_rotor_repr():
    # Test string representation
    rotor = Rotor('II', 'B')
    expected_repr = "Wiring:\n{'forward': 'AJDKSIRUXBLHWTMCQGZNPYFVOE', 'backward': 'AJPCZWRLFBDKOTYUQGENHXMIVS'}\nWindow: B"
    assert rotor.__repr__() == expected_repr, "Rotor __repr__ output did not match expected."

def test_rotor_step():
    # Test stepping without next rotor
    rotor = Rotor('I', 'A')
    rotor.step()
    assert rotor.window == 'B', "Rotor did not step correctly."

def test_rotor_step_with_notch():
    # Test stepping with notch triggering next rotor
    next_rotor = Rotor('II', 'A')
    rotor = Rotor('I', 'Q', next_rotor=next_rotor)
    rotor.step()
    assert rotor.window == 'R' and next_rotor.window == 'B', "Rotor did not step correctly when notch was reached."

def test_encode_letter_forward():
    # Test forward encoding
    rotor = Rotor('I', 'A')
    output = rotor.encode_letter('A', forward=True, return_letter=True)
    assert output == 'E', "Forward encoding failed."

def test_encode_letter_backward():
    # Test backward encoding
    rotor = Rotor('I', 'A')
    output = rotor.encode_letter('E', forward=False, return_letter=True)
    assert output == 'A', "Backward encoding failed."

def test_change_setting():
    # Test changing rotor setting
    rotor = Rotor('I', 'A')
    rotor.change_setting('Z')
    assert rotor.window == 'Z', "Rotor setting change failed."

## Reflector tests
def test_reflector_init():
    # Test the initialization of the reflector and its wiring
    reflector = Reflector()
    assert reflector.wiring['A'] == 'Y', "Reflector initialization failed: wiring incorrect."

def test_reflector_repr():
    # Test the string representation of the reflector's wiring
    reflector = Reflector()
    expected_start = "Reflector wiring: \n{"
    assert reflector.__repr__().startswith(expected_start), "Reflector __repr__ does not match expected format."

## Plugboard tests
def test_plugboard_init_empty():
    # Test initialization without any swaps
    plugboard = Plugboard([])
    assert not plugboard.swaps, "Plugboard should have no swaps."

def test_plugboard_init_with_swaps():
    # Test initialization with some swaps
    plugboard = Plugboard(['AB', 'CD'])
    assert plugboard.swaps['A'] == 'B' and plugboard.swaps['C'] == 'D', "Plugboard swaps not initialized correctly."

def test_plugboard_repr():
    # Test string representation of the plugboard swaps
    plugboard = Plugboard(['AB', 'CD'])
    expected_output = "A <-> B\nC <-> D"
    assert plugboard.__repr__() == expected_output, "Plugboard __repr__ does not match expected."


