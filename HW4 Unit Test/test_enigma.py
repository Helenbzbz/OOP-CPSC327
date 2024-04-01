import unittest
from components import Rotor, ROTOR_WIRINGS, ROTOR_NOTCHES, ALPHABET, Reflector, Plugboard 
from machine import Enigma

class TestRotor(unittest.TestCase):

    def test_valid_initialization(self):
        rotor = Rotor('I', 'A')
        self.assertEqual(rotor.rotor_num, 'I')
        self.assertEqual(rotor.window, 'A')
        self.assertEqual(rotor.offset, 0)  # A is the 0th letter in the alphabet.
        self.assertEqual(rotor.wiring, ROTOR_WIRINGS['I'])
        self.assertEqual(rotor.notch, ROTOR_NOTCHES['I'])

    def test_repr(self):
        rotor = Rotor('II', 'B')
        expected_repr = f"Wiring:\n{ROTOR_WIRINGS['II']}\nWindow: B"
        self.assertEqual(repr(rotor), expected_repr)

    def test_invalid_rotor_number(self):
        with self.assertRaises(ValueError):
            Rotor('VI', 'A')

    def test_step(self):
        rotor = Rotor('I', 'Q')  # Q is the notch for rotor I.
        rotor.step()
        self.assertEqual(rotor.window, 'R')
        self.assertEqual(rotor.offset, 17)

    def test_step_with_next_rotor(self):
        next_rotor = Rotor('II', 'A')
        rotor = Rotor('I', 'Q', next_rotor=next_rotor)  # Set up next rotor.
        rotor.step()
        self.assertEqual(rotor.window, 'R')
        self.assertEqual(next_rotor.window, 'B')  # Next rotor should step as well.

    def test_double_step(self):
        next_rotor = Rotor('III', 'V')  # V is the notch for rotor III.
        mid_rotor = Rotor('II', 'E', next_rotor=next_rotor)  # E is the notch for rotor II.
        rotor = Rotor('I', 'Q', next_rotor=mid_rotor)  # Setup chain.
        rotor.step()
        self.assertEqual(mid_rotor.window, 'F')  # Mid rotor should double step.
        self.assertEqual(next_rotor.window, 'W')  # Next rotor should step due to double step.

    def test_encode_letter_forward(self):
        rotor = Rotor('I', 'A')  # Initial setting at A.
        output = rotor.encode_letter('A', forward=True, return_letter=True)
        self.assertEqual(output, 'E')  # Based on 'I' wiring forward.

    def test_encode_letter_backward(self):
        rotor = Rotor('I', 'A')
        index = ALPHABET.index('E')  # Find index of 'E', the output of 'A' through rotor 'I'.
        output = rotor.encode_letter(index, forward=False, return_letter=True)
        self.assertEqual(output, 'A')  # Reverse transformation should yield 'A'.

    def test_encode_letter_chain_forward(self):
        rotor1 = Rotor('I', 'A')
        rotor2 = Rotor('II', 'A', prev_rotor=rotor1)
        rotor1.next_rotor = rotor2
        output = rotor1.encode_letter('A', forward=True, return_letter=True)
        # Expected result is specific to wiring configurations.
        self.assertEqual(output, 'J')  # Expected output based on wiring and initial settings.

    def test_encode_letter_chain_backward(self):
        rotor1 = Rotor('I', 'A')
        rotor2 = Rotor('II', 'A', prev_rotor=rotor1)
        rotor1.next_rotor = rotor2
        # Reverse transformation should yield original input.
        index = ALPHABET.index('J')  # Result of forward transformation in the previous test.
        output = rotor2.encode_letter(index, forward=False, return_letter=True)
        self.assertEqual(output, 'A')

    def test_change_setting(self):
        rotor = Rotor('I', 'A')
        rotor.change_setting('M')
        self.assertEqual(rotor.window, 'M')
        self.assertEqual(rotor.offset, ALPHABET.index('M')) 
    
    def test_step_from_z_to_a(self):
        rotor = Rotor('I', 'Z')
        rotor.step()
        self.assertEqual(rotor.window, 'A')  # Ensure it wraps around correctly.
        self.assertEqual(rotor.offset, 0)

class TestReflector(unittest.TestCase):
    def test_initialization(self):
        reflector = Reflector()
        expected_wiring = {'A':'Y', 'B':'R', 'C':'U', 'D':'H', 'E':'Q', 'F':'S', 'G':'L', 'H':'D',
                           'I':'P', 'J':'X', 'K':'N', 'L':'G', 'M':'O', 'N':'K', 'O':'M', 'P':'I',
                           'Q':'E', 'R':'B', 'S':'F', 'T':'Z', 'U': 'C', 'V':'W', 'W':'V', 'X':'J',
                           'Y':'A', 'Z':'T'}
        self.assertEqual(reflector.wiring, expected_wiring)

    def test_repr(self):
        reflector = Reflector()
        expected_repr = "Reflector wiring: \n" + str(reflector.wiring)
        self.assertEqual(repr(reflector), expected_repr)
    
class TestPlugboard(unittest.TestCase):

    def test_initialization_with_valid_swaps(self):
        plugboard = Plugboard(['AB', 'CD'])
        expected_swaps = {'A': 'B', 'B': 'A', 'C': 'D', 'D': 'C'}
        self.assertEqual(plugboard.swaps, expected_swaps)

    def test_initialization_without_swaps(self):
        plugboard = Plugboard([])
        self.assertEqual(plugboard.swaps, {})

    def test_initialization_with_none_swaps(self):
        plugboard = Plugboard(None)
        self.assertEqual(plugboard.swaps, {})

    def test_repr(self):
        plugboard = Plugboard(['AB', 'CD'])
        expected_output = "A <-> B\nC <-> D"  # The order depends on how swaps are stored and iterated.
        self.assertEqual(repr(plugboard), expected_output)

    def test_update_swaps_add_new(self):
        plugboard = Plugboard(['AB'])
        plugboard.update_swaps(['XY'], replace=False)
        expected_swaps = {'A': 'B', 'B': 'A', 'X': 'Y', 'Y': 'X'}
        self.assertEqual(plugboard.swaps, expected_swaps)

    def test_update_swaps_replace(self):
        plugboard = Plugboard(['AB'])
        plugboard.update_swaps(['XY'], replace=True)
        expected_swaps = {'X': 'Y', 'Y': 'X'}
        self.assertEqual(plugboard.swaps, expected_swaps)

    def test_update_swaps_exceed_max_swaps(self):
        plugboard = Plugboard([])
        with self.assertLogs() as captured:
            plugboard.update_swaps(['AB', 'CD', 'EF', 'GH', 'IJ', 'KL', 'MN'], replace=True)
        self.assertIn('Only a maximum of 6 swaps is allowed.', captured.output[0])

    def test_update_swaps_with_none(self):
        plugboard = Plugboard(['AB'])
        plugboard.update_swaps(None, replace=True)
        self.assertEqual(plugboard.swaps, {})

class TestEnigma(unittest.TestCase):

    def test_enigma_initialization(self):
        enigma = Enigma()
        self.assertEqual(enigma.key, 'AAA')
        self.assertEqual(enigma.rotor_order, ['I', 'II', 'III'])

    def test_enigma_repr(self):
        enigma = Enigma()
        expected_repr = "Keyboard <-> Plugboard <->  Rotor I <-> Rotor  II <-> Rotor  III <-> Reflector \nKey:  + AAA"
        self.assertEqual(repr(enigma), expected_repr)

    def test_encipher_decipher(self):
        enigma = Enigma(key='AAA', swaps=[('A', 'B')])
        message = "HELLO"
        enciphered = enigma.encipher(message)
        deciphered = enigma.decipher(enciphered)
        self.assertNotEqual(message, enciphered)
        self.assertEqual(message, deciphered.replace(" ", ""))
    
    def test_encode_decode_letter(self):
        enigma = Enigma(key='AAA', swaps=[('H', 'I')])
        # H gets swapped to I, encodes through rotors and reflector, then back
        encoded_letter = enigma.encode_decode_letter('H')
        self.assertNotEqual('H', encoded_letter)

    def test_rotor_stepping(self):
        enigma = Enigma(key='VDZ')  # Set starting positions to ensure rotor stepping
        # Check that rotor stepping occurs correctly after encoding a letter
        enigma.encipher('A')
        self.assertNotEqual(enigma.r_rotor.window, 'Z')  # Right rotor should step

    def test_set_rotor_position(self):
        enigma = Enigma()
        enigma.set_rotor_position('BCD')
        self.assertEqual(enigma.key, 'BCD')
        self.assertEqual(enigma.l_rotor.window, 'B')
        self.assertEqual(enigma.m_rotor.window, 'C')
        self.assertEqual(enigma.r_rotor.window, 'D')

    def test_set_rotor_position_invalid_input(self):
        enigma = Enigma()
        with self.assertRaises(ValueError):  # Assuming you change print to raising ValueError for invalid inputs
            enigma.set_rotor_position('ABCD')  # Too long

    def test_set_rotor_order(self):
        enigma = Enigma()
        enigma.set_rotor_order(['III', 'I', 'II'])
        self.assertEqual(enigma.rotor_order, ['III', 'I', 'II'])
        self.assertEqual(enigma.l_rotor.rotor_num, 'III')
        self.assertEqual(enigma.m_rotor.rotor_num, 'I')
        self.assertEqual(enigma.r_rotor.rotor_num, 'II')

    def test_set_plugs(self):
        enigma = Enigma()
        enigma.set_plugs([('X', 'Z')], replace=True)
        self.assertIn('X', enigma.plugboard.swaps)
        self.assertIn('Z', enigma.plugboard.swaps['X'])

    def test_set_plugs_replace(self):
        enigma = Enigma(swaps=[('A', 'B')])
        enigma.set_plugs([('X', 'Z')], replace=True)
        self.assertNotIn('A', enigma.plugboard.swaps)
        self.assertIn('X', enigma.plugboard.swaps)

    def test_invalid_key_length(self):
        with self.assertRaises(ValueError):
            Enigma(key='ABCD')

    def test_invalid_letter_encipher(self):
        enigma = Enigma()
        with self.assertRaises(ValueError):
            enigma.encipher('123')

if __name__ == '__main__':
    unittest.main()






