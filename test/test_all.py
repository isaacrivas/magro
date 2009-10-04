import unittest
import test

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromNames([
        'test.test_env',
        'test.test_lex',
        'test.test_yacc',
        'test.test_ast',
        'test.test_results',
        'test.test_context',
        'test.test_templates',
        'test.test_htmltags',
        'test.test_bugs',
    ])
    unittest.TextTestRunner(verbosity=2).run(suite)
