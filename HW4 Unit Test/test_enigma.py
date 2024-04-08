import unittest
from unittest.mock import patch
from io import StringIO
from components import Rotor, ROTOR_WIRINGS, ROTOR_NOTCHES, ALPHABET, Reflector, Plugboard 
from machine import Enigma

class TestRotorBasic(unittest.TestCase):
    '''
    Focus on Test Rotor init
    Test 5. Test whether Rotor can be set up correctly
    '''
    def test_rotor_initialization_valid(self):
        """Test rotor initialization with valid parameters."""
        rotor = Rotor('I', 'A')
        self.assertEqual(rotor.window, 'A')
        self.assertEqual(rotor.rotor_num, 'I')
        self.assertEqual(rotor.offset, 0)

    def test_initialization_invalid_rotor_number(self):
        """Initialization should fail with an invalid rotor number."""
        with self.assertRaises(ValueError):
            Rotor('IV', 'A')
    
class TestRotorStep(unittest.TestCase):
    '''Focus on Testing Rotor Step Function'''
    def setUp(self):
        """Setup common test scenarios for efficiency."""
        # Simple setup without linked rotors
        self.simple_rotor = Rotor('I', 'A')

        # Setup for testing notch behavior
        self.notch_rotor = Rotor('I', 'Q')
        self.next_rotor = Rotor('II', 'A')
        self.notch_rotor.next_rotor = self.next_rotor

        # Setup for testing double-step scenario
        self.middle_rotor = Rotor('II', 'E')
        self.left_rotor = Rotor('I', 'A', next_rotor=self.middle_rotor)
        self.right_rotor = Rotor('III', 'V', next_rotor=self.left_rotor, prev_rotor=self.middle_rotor)
        self.middle_rotor.prev_rotor = self.right_rotor

    def test_step_normal_behavior(self):
        """Test 4. Test whether Rotor can step normally"""
        self.simple_rotor.step()
        self.assertEqual(self.simple_rotor.window, 'B')

    def test_step_at_notch_behavior(self):
        """Next rotor should step when current rotor is at its notch."""
        self.notch_rotor.step() 
        self.assertEqual(self.notch_rotor.window, 'R')
        self.assertEqual(self.next_rotor.window, 'B')

    def test_double_step_scenario(self):
        """Test 2,7,10 Test the double-step scenario."""
        self.right_rotor.window = 'V' 
        self.right_rotor.step() 
        self.assertEqual(self.middle_rotor.window, 'F')
        self.assertEqual(self.left_rotor.window, 'B')

class TestRotorEncodeLetter(unittest.TestCase):
    """Test 8. Covers the encode_letter function"""
    def test_encode_letter_forward_return_index(self):
        rotor = Rotor('I', 'A')
        output = rotor.encode_letter('A', forward=True, return_letter=False)
        self.assertEqual(output, 4)

    def test_encode_letter_backward_return_index(self):
        rotor = Rotor('I', 'A')
        output = rotor.encode_letter('E', forward=False, return_letter=False)
        self.assertEqual(output, 0)

    def test_encode_letter_forward_return_letter(self):
        rotor = Rotor('I', 'A')
        output = rotor.encode_letter('A', forward=True, return_letter=True)
        self.assertEqual(output, 'E')

    def test_encode_letter_backward_return_letter(self):
        rotor = Rotor('I', 'A')
        output = rotor.encode_letter('E', forward=False, return_letter=True)
        self.assertEqual(output, 'A')

    def test_encode_letter_with_next_rotor_forward(self):
        rotor1 = Rotor('I', 'A')
        rotor2 = Rotor('II', 'A')
        rotor1.next_rotor = rotor2
        output = rotor1.encode_letter('A', forward=True)
        self.assertEqual(output, 18)

    def test_encode_letter_with_next_rotor_backward(self):
        rotor1 = Rotor('I', 'A')
        rotor2 = Rotor('II', 'A')
        rotor1.next_rotor = rotor2
        output = rotor1.encode_letter('E', forward=False)
        self.assertEqual(output, 0)
    
    def test_encode_letter_with_prev_rotor_forward(self):
        rotor1 = Rotor('I', 'A')
        rotor2 = Rotor('II', 'A')
        rotor1.prev_rotor = rotor2
        output = rotor1.encode_letter('E', forward=True)
        self.assertEqual(output, 11)

    def test_encode_letter_with_prev_rotor_backward(self):
        rotor1 = Rotor('I', 'A')
        rotor2 = Rotor('II', 'A')
        rotor1.prev_rotor = rotor2
        output = rotor1.encode_letter('A', forward=False)
        self.assertEqual(output, 7)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_encode_letter_printit(self, mock_stdout):
        rotor = Rotor('I', 'A')
        rotor.encode_letter('A', forward=True, printit=True)
        self.assertEqual(mock_stdout.getvalue().strip(), 'Rotor I: input = A, output = E')

    def test_encode_letter_without_rotor(self):
        rotor = Rotor('I', 'A')
        output = rotor.encode_letter('A', forward=True)
        self.assertEqual(output, 4)

class TestRotorChangeSetting(unittest.TestCase):
    """Test the change_setting function"""
    def test_change_setting_valid_input(self):
        rotor = Rotor('I', 'A')
        rotor.change_setting('C')
        self.assertEqual(rotor.window, 'C')
        self.assertEqual(rotor.offset, 2)

    def test_change_setting_invalid_input(self):
        rotor = Rotor('I', 'A')
        with self.assertRaises(ValueError):
            rotor.change_setting('!')

class TestReflector(unittest.TestCase):
    """Test the Reflector Class"""
    def test_init(self):
        reflector = Reflector()
        self.assertEqual(reflector.wiring, {
            'A': 'Y', 'B': 'R', 'C': 'U', 'D': 'H', 'E': 'Q', 'F': 'S', 'G': 'L', 'H': 'D',
            'I': 'P', 'J': 'X', 'K': 'N', 'L': 'G', 'M': 'O', 'N': 'K', 'O': 'M', 'P': 'I',
            'Q': 'E', 'R': 'B', 'S': 'F', 'T': 'Z', 'U': 'C', 'V': 'W', 'W': 'V', 'X': 'J',
            'Y': 'A', 'Z': 'T'})

    def test_repr(self):
        reflector = Reflector()
        expected_repr = "Reflector wiring: \n{'A': 'Y', 'B': 'R', 'C': 'U', 'D': 'H', 'E': 'Q', 'F': 'S', 'G': 'L', 'H': 'D', 'I': 'P', 'J': 'X', 'K': 'N', 'L': 'G', 'M': 'O', 'N': 'K', 'O': 'M', 'P': 'I', 'Q': 'E', 'R': 'B', 'S': 'F', 'T': 'Z', 'U': 'C', 'V': 'W', 'W': 'V', 'X': 'J', 'Y': 'A', 'Z': 'T'}"
        self.assertEqual(repr(reflector), expected_repr)

class TestPlugboard(unittest.TestCase):
    def test_init_no_swaps(self):
        plugboard = Plugboard(None)
        self.assertEqual(plugboard.swaps, {})

    def test_init_with_swaps(self):
        swaps = ['AB', 'XR', 'CF']
        plugboard = Plugboard(swaps)
        expected_swaps = {'A': 'B', 'B': 'A', 'X': 'R', 'R': 'X', 'C': 'F', 'F': 'C'}
        self.assertEqual(plugboard.swaps, expected_swaps)

    def test_init_with_invalid_swaps(self):
        with self.assertRaises(IndexError):
            Plugboard('AB')

    def test_repr(self):
        swaps = ['AB', 'XR', 'CF']
        plugboard = Plugboard(swaps)
        expected_repr = "A <-> B\nX <-> R\nC <-> F"
        self.assertEqual(repr(plugboard), expected_repr)

    def test_update_swaps_replace_true(self):
        plugboard = Plugboard(None)
        new_swaps = ['AB', 'XR', 'CF']
        plugboard.update_swaps(new_swaps, replace=True)
        expected_swaps = {'A': 'B', 'B': 'A', 'X': 'R', 'R': 'X', 'C': 'F', 'F': 'C'}
        self.assertEqual(plugboard.swaps, expected_swaps)

    def test_update_swaps_replace_false(self):
        plugboard = Plugboard(None)
        initial_swaps = ['AB', 'XR']
        plugboard.update_swaps(initial_swaps)
        new_swaps = ['CF', 'GH']
        plugboard.update_swaps(new_swaps)
        expected_swaps = {'A': 'B', 'B': 'A', 'X': 'R', 'R': 'X', 'C': 'F', 'F': 'C', 'G': 'H', 'H': 'G'}
        self.assertEqual(plugboard.swaps, expected_swaps)

    def test_update_swaps_max_limit(self):
        plugboard = Plugboard(None)
        new_swaps = ['AB', 'XR', 'CF', 'GH', 'IJ', 'KL', 'MN']
        with unittest.mock.patch('builtins.print') as mocked_print:
            plugboard.update_swaps(new_swaps)
            mocked_print.assert_called_with('Only a maximum of 6 swaps is allowed.')

class TestEnigma(unittest.TestCase):
    def test_init(self):
        enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])
        self.assertEqual(enigma.key, 'AAA')
        self.assertEqual(enigma.rotor_order, ['I', 'II', 'III'])

    def test_repr(self):
        enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])
        expected_repr = ("Keyboard <-> Plugboard <->  Rotor I <-> Rotor  II <-> Rotor  III <-> Reflector \n"
                         "Key:  + AAA")
        self.assertEqual(repr(enigma), expected_repr)

    def test_encipher_decipher(self):
        enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])
        message = "HELLO"
        encoded_message = enigma.encipher(message)
        self.assertEqual(encoded_message, 'LXFOP')
        decoded_message = enigma.decipher(encoded_message)
        self.assertEqual(decoded_message, message)

    def test_encode_decode_letter(self):
        enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])
        letter = 'H'
        encoded_letter = enigma.encode_decode_letter(letter)
        self.assertEqual(encoded_letter, 'L')

if __name__ == '__main__':
    unittest.main()





