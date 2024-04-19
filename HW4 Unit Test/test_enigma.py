import unittest
from unittest.mock import patch
from io import StringIO
from components import Rotor, Reflector, Plugboard 
from machine import Enigma

class TestRotorBasic(unittest.TestCase):
    """Focus on Test Rotor init
    Test 5. Test whether Rotor can be set up correctly"""
    def test_rotor_initialization_valid(self):
        rotor = Rotor('I', 'A')
        self.assertEqual(rotor.window, 'A')
        self.assertEqual(rotor.rotor_num, 'I')
        self.assertEqual(rotor.offset, 0)
        expected_repr = "Wiring:\n{'forward': 'EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'backward': 'UWYGADFPVZBECKMTHXSLRINQOJ'}\nWindow: A"
        self.assertEqual(repr(rotor), expected_repr)

    def test_initialization_invalid_rotor_number(self):
        with self.assertRaises(ValueError):
            Rotor('IV', 'A')
    
    def test_initialization_with_invalid_window_letter(self):
        with self.assertRaises(ValueError):
            Rotor('I', '1')
    
    def test_invalid_key_characters(self):
        with self.assertRaises(ValueError):
            Enigma(key='A1B')

    def test_initialization_lowercase(self):
        rotor = Rotor('I', 'a')
        self.assertEqual(rotor.window, 'A')
        self.assertEqual(rotor.rotor_num, 'I')
        self.assertEqual(rotor.offset, 0)
        expected_repr = "Wiring:\n{'forward': 'EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'backward': 'UWYGADFPVZBECKMTHXSLRINQOJ'}\nWindow: A"
        self.assertEqual(repr(rotor), expected_repr)
    
class TestRotorStep(unittest.TestCase):
    """Focus on Testing Rotor Step Function"""
    def setUp(self):
        self.simple_rotor = Rotor('I', 'A')

        self.notch_rotor = Rotor('I', 'Q')
        self.next_rotor = Rotor('II', 'A')
        self.notch_rotor.next_rotor = self.next_rotor

        self.middle_rotor = Rotor('II', 'E')
        self.left_rotor = Rotor('I', 'A', next_rotor=self.middle_rotor)
        self.right_rotor = Rotor('III', 'V', next_rotor=self.left_rotor, prev_rotor=self.middle_rotor)
        self.middle_rotor.prev_rotor = self.right_rotor

    def test_step_normal_behavior(self):
        """Test 4. Test whether Rotor can step normally"""
        self.simple_rotor.step()
        self.assertEqual(self.simple_rotor.window, 'B')

    def test_step_at_notch_behavior(self):
        self.notch_rotor.step() 
        self.assertEqual(self.notch_rotor.window, 'R')
        self.assertEqual(self.next_rotor.window, 'B')

    def test_repeated_encipherment_different_output(self):
        enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])
        first_encipherment = enigma.encipher('A')
        second_encipherment = enigma.encipher('A')
        self.assertNotEqual(first_encipherment, second_encipherment)

    def test_double_step_scenario(self):
        """Test 2,7,10 Test the double-step scenario."""
        self.right_rotor.window = 'V' 
        self.right_rotor.step() 
        self.assertEqual(self.middle_rotor.window, 'F')
        self.assertEqual(self.left_rotor.window, 'B')
    
    def test_step_from_z_to_a(self):
        rotor = Rotor('I', 'Z')
        rotor.step()
        self.assertEqual(rotor.window, 'A')
    
    def test_full_cycle_interaction_among_rotors(self):
        left_rotor = Rotor('I', 'A')
        middle_rotor = Rotor('II', 'A', next_rotor=left_rotor)
        right_rotor = Rotor('III', 'A', next_rotor=middle_rotor)
        for _ in range(26):
            right_rotor.step()
        self.assertEqual(right_rotor.window, 'A') 

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
    
    def test_encode_letter_with_invalid_input(self):
        rotor = Rotor('I', 'A')
        with self.assertRaises(TypeError):
            rotor.encode_letter('AB', forward=True)
    
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
   
    def test_invalid_initialization(self):
        with self.assertRaises(TypeError):
            Reflector('a')

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

    def test_duplicate_entries(self):
        plugboard = Plugboard(['AB', 'BA']) 
        self.assertEqual(plugboard.swaps, {'A': 'B', 'B': 'A'})

class TestEnigmaBasicCipher(unittest.TestCase):
    """Test the initial setup; Encode/Decode; Encipher/Decipher"""
    def test_init_default_parameters(self):
        enigma = Enigma()
        self.assertEqual(enigma.key, 'AAA')
        self.assertEqual(enigma.rotor_order, ['I', 'II', 'III'])
        self.assertIsInstance(enigma.reflector, Reflector)
        self.assertIsInstance(enigma.plugboard, Plugboard)
        self.assertEqual(repr(enigma), "Keyboard <-> Plugboard <->  Rotor I <-> Rotor  II <-> Rotor  III <-> Reflector \nKey:  + AAA")

    def test_init_custom_parameters(self):
        enigma = Enigma(key='BDF', swaps=[('A', 'B'), ('T', 'G')], rotor_order=['III', 'II', 'I'])
        self.assertEqual(enigma.key, 'BDF')
        self.assertEqual(enigma.rotor_order, ['III', 'II', 'I'])
        self.assertIsInstance(enigma.reflector, Reflector)
        self.assertIsInstance(enigma.plugboard, Plugboard)
        self.assertEqual(enigma.plugboard.swaps, {'A': 'B', 'B': 'A', 'T': 'G', 'G': 'T'})
        expected_repr = "Keyboard <-> Plugboard <->  Rotor III <-> Rotor  II <-> Rotor  I <-> Reflector \nKey:  + BDF"
        self.assertEqual(repr(enigma), expected_repr)
    
    def test_init_invalid_key_length(self):
        with self.assertRaises(ValueError):
            Enigma(key='ABCD')
    
    ## Test 1 covers encode decode functions
    def test_encode_decode_letter_valid_input_without_swap(self):
        enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])
        encoded_letter = enigma.encode_decode_letter('H')
        self.assertEqual(encoded_letter, 'I')
    
    def test_encode_decode_letter_valid_input_with_swap_initial(self):
        enigma = Enigma(key='AAA', swaps=[('H', 'D')], rotor_order=['I', 'II', 'III'])
        encoded_letter = enigma.encode_decode_letter('H')
        self.assertEqual(encoded_letter, 'M')

    def test_encode_decode_letter_valid_input_with_swap_final(self):
        enigma = Enigma(key='AAA', swaps=[('I', 'D')], rotor_order=['I', 'II', 'III'])
        encoded_letter = enigma.encode_decode_letter('H')
        self.assertEqual(encoded_letter, 'D')

    def test_encode_decode_letter_invalid_input(self):
        enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])
        with self.assertRaises(ValueError):
            enigma.encode_decode_letter('123')

    ## Test 3 covers encipher decipher functions
    def test_encipher_decipher_valid_input(self):
        enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])
        message = "HELLO WORLD"
        encoded_message = enigma.encipher(message)
        self.assertEqual(encoded_message, 'ILBDAAMTAZ')
        decoded_message = enigma.decipher(encoded_message)
        self.assertEqual(decoded_message, 'BRAFMCNIPN')

    def test_encipher_decipher_empty_input(self):
        enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])
        message = ""
        encoded_message = enigma.encipher(message)
        self.assertEqual(encoded_message, "")
        decoded_message = enigma.decipher(encoded_message)
        self.assertEqual(decoded_message, "")

    def test_encipher_decipher_invalid_input(self):
        enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])
        with self.assertRaises(ValueError):
            enigma.encipher("123")

## Test 9. Test the Engima set rotor position function
class TestSetRotorPosition(unittest.TestCase):
    def setUp(self):
        self.enigma = Enigma(key='AAA', swaps=None, rotor_order=['I', 'II', 'III'])

    def test_set_rotor_position_valid_input(self):
        self.enigma.set_rotor_position('BDF')
        self.assertEqual(self.enigma.key, 'BDF')
        self.assertEqual(self.enigma.l_rotor.window, 'B')
        self.assertEqual(self.enigma.m_rotor.window, 'D')
        self.assertEqual(self.enigma.r_rotor.window, 'F')

    def test_set_rotor_position_valid_input_with_print(self):
        with patch('builtins.print') as mocked_print:
            self.enigma.set_rotor_position('BDF', printIt=True)
            mocked_print.assert_called_with('Rotor position successfully updated. Now using BDF.')
        self.assertEqual(self.enigma.key, 'BDF')
        self.assertEqual(self.enigma.l_rotor.window, 'B')
        self.assertEqual(self.enigma.m_rotor.window, 'D')
        self.assertEqual(self.enigma.r_rotor.window, 'F')

    def test_set_rotor_position_invalid_input(self):
        with patch('builtins.print') as mocked_print:
            self.enigma.set_rotor_position('BD')
            mocked_print.assert_called_with('Please provide a three letter position key such as AAA.')
        self.assertEqual(self.enigma.key, 'AAA')
        self.assertEqual(self.enigma.l_rotor.window, 'A')
        self.assertEqual(self.enigma.m_rotor.window, 'A')
        self.assertEqual(self.enigma.r_rotor.window, 'A')

    def test_printing_on_valid_input(self):
        position_key = 'XYZ'
        with patch('builtins.print') as mock_print:
            self.enigma.set_rotor_position(position_key, printIt=True)
            mock_print.assert_called_once_with('Rotor position successfully updated. Now using XYZ.')

    def test_no_printing_on_valid_input(self):
        position_key = 'LMN'
        with patch('builtins.print') as mock_print:
            self.enigma.set_rotor_position(position_key, printIt=False)
            mock_print.assert_not_called()

class TestSetRotorOrder(unittest.TestCase):
    def setUp(self):
        self.enigma = Enigma(key='ABC')

    def test_rotor_order_initialization(self):
        self.enigma.set_rotor_order(['I', 'II', 'III'])
        
        self.assertEqual(self.enigma.l_rotor.rotor_num, 'I')
        self.assertEqual(self.enigma.m_rotor.rotor_num, 'II')
        self.assertEqual(self.enigma.r_rotor.rotor_num, 'III')
        
        self.assertEqual(self.enigma.l_rotor.window, 'A')
        self.assertEqual(self.enigma.m_rotor.window, 'B')
        self.assertEqual(self.enigma.r_rotor.window, 'C')

        self.assertIs(self.enigma.l_rotor.prev_rotor, self.enigma.m_rotor)
        self.assertIs(self.enigma.r_rotor.next_rotor, self.enigma.m_rotor)
        self.assertIs(self.enigma.m_rotor.next_rotor, self.enigma.l_rotor)
        self.assertIs(self.enigma.m_rotor.prev_rotor, self.enigma.r_rotor)

    def test_rotor_order_change(self):
        """Ensure changing rotor order updates the machine configuration correctly."""
        new_order = ['III', 'I', 'II']
        self.enigma.set_rotor_order(new_order)
        
        self.assertEqual(self.enigma.l_rotor.rotor_num, 'III')
        self.assertEqual(self.enigma.m_rotor.rotor_num, 'I')
        self.assertEqual(self.enigma.r_rotor.rotor_num, 'II')
        
        self.assertEqual(self.enigma.l_rotor.window, 'A')
        self.assertEqual(self.enigma.m_rotor.window, 'B')
        self.assertEqual(self.enigma.r_rotor.window, 'C')

        self.assertIs(self.enigma.l_rotor.prev_rotor, self.enigma.m_rotor)
        self.assertIs(self.enigma.r_rotor.next_rotor, self.enigma.m_rotor)
        self.assertIs(self.enigma.m_rotor.prev_rotor, self.enigma.r_rotor)
        self.assertIs(self.enigma.m_rotor.next_rotor, self.enigma.l_rotor)

class TestSetPlugs(unittest.TestCase):
    def setUp(self):
        self.enigma = Enigma()

    def test_initial_swaps_addition(self):
        """Test adding initial swaps to an empty plugboard."""
        swaps = ['AB', 'CD']
        self.enigma.set_plugs(swaps)
        expected_swaps = {'A': 'B', 'B': 'A', 'C': 'D', 'D': 'C'}
        self.assertEqual(self.enigma.plugboard.swaps, expected_swaps)

    def test_add_additional_swaps_without_replacement(self):
        """Adding more swaps without replacement should keep existing swaps."""
        initial_swaps = ['AB', 'CD']
        new_swaps = ['EF', 'GH']
        self.enigma.set_plugs(initial_swaps)
        self.enigma.set_plugs(new_swaps, replace=False)
        expected_swaps = {'A': 'B', 'B': 'A', 'C': 'D', 'D': 'C', 'E': 'F', 'F': 'E', 'G': 'H', 'H': 'G'}
        self.assertEqual(self.enigma.plugboard.swaps, expected_swaps)

    def test_replace_swaps(self):
        """Replacing swaps should remove all previous swaps and add new ones."""
        self.enigma.set_plugs(['AB', 'CD'])
        self.enigma.set_plugs(['XY', 'WZ'], replace=True)
        expected_swaps = {'X': 'Y', 'Y': 'X', 'W': 'Z', 'Z': 'W'}
        self.assertEqual(self.enigma.plugboard.swaps, expected_swaps)

    def test_empty_swaps_with_replace(self):
        """Providing an empty swaps list with replace=True should clear all swaps."""
        self.enigma.set_plugs(['AB', 'CD'])
        self.enigma.set_plugs([], replace=True)
        self.assertEqual(self.enigma.plugboard.swaps, {})

    def test_empty_swaps_without_replace(self):
        """Providing an empty swaps list with replace=False should not affect existing swaps."""
        initial_swaps = ['AB', 'CD']
        self.enigma.set_plugs(initial_swaps)
        self.enigma.set_plugs([], replace=False)
        expected_swaps = {'A': 'B', 'B': 'A', 'C': 'D', 'D': 'C'}
        self.assertEqual(self.enigma.plugboard.swaps, expected_swaps)

    @patch('builtins.print')
    def test_set_plugs_with_print(self, mocked_print):
        swaps = ['AB', 'CD']
        self.enigma.set_plugs(swaps, printIt=True)
        expected_first_call = ('Plugboard successfully updated. New swaps are:',)
        self.assertEqual(mocked_print.call_args_list[0].args, expected_first_call)

if __name__ == '__main__':
    unittest.main()





