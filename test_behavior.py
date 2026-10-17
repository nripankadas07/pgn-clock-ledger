import unittest
from pgn_clock_ledger import analyze
H='[TimeControl "300+2"]\n[Result "*"]\n'
G='1. e4 {[%clk 0:04:59]} e5 {[%clk 0:05:00]} 2. Nf3 {[%clk 0:04:58]} Nc6 {[%clk 0:04:57]} *'

class ClockTests(unittest.TestCase):
    def test_increment_accounting(self):
        r=analyze(H+G);self.assertEqual([p['elapsed_millis'] for p in r['plies']],[3000,2000,3000,5000]);self.assertEqual(r['known_elapsed_totals_millis'],{'white':6000,'black':7000});self.assertFalse(r['findings'])
    def test_fractional_clock_milliseconds(self):
        r=analyze(H+'1.e4 {[%clk 0:04:59.125]} *');self.assertEqual(r['plies'][0]['elapsed_millis'],2875)
    def test_missing_clocks_resynchronize_per_side(self):
        r=analyze(H+'1. e4 e5 {[%clk 0:05:00]} 2. Nf3 {[%clk 0:04:50]} Nc6 {[%clk 0:04:58]} 3. Bb5 {[%clk 0:04:49]} *');self.assertEqual([p['status'] for p in r['plies']],['clock_missing','computed_under_increment_convention','prior_clock_missing','computed_under_increment_convention','computed_under_increment_convention']);self.assertEqual(r['plies'][-1]['elapsed_millis'],3000)
    def test_clock_increase_is_finding_then_new_baseline(self):
        r=analyze(H+'1.e4 {[%clk 0:05:10]} e5 {[%clk 0:05:00]} 2.Nf3 {[%clk 0:05:09]} *');self.assertEqual(r['plies'][0]['status'],'clock_increase_exceeds_increment');self.assertEqual(r['plies'][2]['elapsed_millis'],3000)
    def test_variation_clocks_do_not_overwrite_mainline(self):
        r=analyze(H+'1.e4 {[%clk 0:04:59]} (1.d4 {[%clk 9:99:99]} (1.c4)) e5 {[%clk 0:05:00]} *');self.assertEqual(len(r['plies']),2);self.assertEqual(r['known_elapsed_totals_millis'],{'white':3000,'black':2000})
    def test_comments_and_nags(self):
        r=analyze(H+'1.e4!? $1 {a comment} {[%clk 0:04:59]} ; ignored [%clk bad]\ne5 {[%clk 0:05:00]} *');self.assertFalse(r['findings'])
    def test_explicit_black_move_number(self):
        self.assertEqual(len(analyze(H+'1.e4 1...e5 *')['plies']),2)
    def test_wrong_move_number_or_side(self):
        for body in ['2.e4 *','1...e5 *','1.e4 2...e5 *','1. 1.e4 *']:
            with self.subTest(body=body),self.assertRaises(ValueError):analyze(H+body)
    def test_castling_promotion_capture_labels(self):
        r=analyze(H+'1.O-O O-O-O 2.exd8=Q+ Nbd7 *');self.assertEqual(len(r['plies']),4)
    def test_leading_and_duplicate_clocks_refused(self):
        for body in ['{[%clk 0:05:00]} 1.e4 *','1.e4 {[%clk 0:04:59]} {[%clk 0:04:58]} *','1. {[%clk 0:04:59]} e4 *']:
            with self.assertRaises(ValueError):analyze(H+body)
    def test_bad_clock_annotations(self):
        for c in ['0:60:00','0:00:60','0:05:00.1234','-1:00:00','oops']:
            with self.subTest(c=c),self.assertRaises(ValueError):analyze(H+'1.e4 {[%clk '+c+']} *')
    def test_invalid_time_controls(self):
        for tc in ['300','40/7200:3600','300+2.5','0+2','86401+0','300+3601']:
            with self.assertRaises(ValueError):analyze(H.replace('300+2',tc)+G)
    def test_header_duplicates_and_nonstandard_starts(self):
        for header in ['[TimeControl "300+2"]','[FEN "x"]','[SetUp "0"]','[Variant "Atomic"]']:
            with self.assertRaises(ValueError):analyze(header+H+G)
    def test_header_result_consistency(self):
        with self.assertRaises(ValueError):analyze(H.replace('[Result "*"]','[Result "1-0"]')+G)
    def test_one_game_and_terminator(self):
        for b in ['1.e4','1.e4 * 1.d4 *','1.e4 * [Event "next"]','1. *','*']:
            with self.assertRaises(ValueError):analyze(H+b)
    def test_balanced_comments_and_variations(self):
        for b in ['1.e4 {bad *','1.e4 {a {b} } *','1.e4 (e5 *','1.e4 ) *']:
            with self.assertRaises(ValueError):analyze(H+b)
    def test_zero_clock_not_flag_claim(self):
        r=analyze(H+'1.e4 {[%clk 0:00:00]} *');self.assertEqual(r['plies'][0]['elapsed_millis'],302000);self.assertNotIn('flag',r)
    def test_all_missing_is_unknown_not_zero_evidence(self):
        r=analyze(H+'1.e4 e5 *');self.assertEqual(len(r['findings']),2);self.assertEqual(r['computed_plies'],{'white':0,'black':0})
    def test_escaped_metadata_not_executed(self):
        r=analyze('[Event "a\\\"b"]\n'+H+G);self.assertIn('Event',r['ignored_header_keys'])
    def test_unsupported_label_and_input_budget(self):
        for b in ['1.e9 *','1.hello *','1.'+'a'*65+' *']:
            with self.assertRaises(ValueError):analyze(H+b)
        with self.assertRaises(ValueError):analyze(H+(' '*131072)+G)

if __name__=='__main__':unittest.main()
